import pygame
import math
import random
import sys
import os
import json
import logging

from utils.timer_utils import reset_activity_timer
from config import get_leaderboard_path

LEADERBOARD_FILE = get_leaderboard_path()

class Trajectory:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=logging.WARNING)  # Change to DEBUG for detailed logs
        self.logger = logging.getLogger(__name__)

        # Default exit message
        self.exit_message = "Leaving Trajectory Demo"

        # Track whether user pressed ESC (quit), so we can skip name screen
        self.user_quit = False

        # Store the original file descriptor for standard input
        self.stdin_fd = sys.stdin.fileno()
        self.stdin_copy = os.dup(self.stdin_fd)

        try:
            pygame.init()
            # Hide the mouse cursor
            pygame.mouse.set_visible(False)
            # Make arrow keys repeat when held
            pygame.key.set_repeat(200, 40)

            # Constants
            self.WIDTH, self.HEIGHT = 800, 600
            self.ORIGIN_X, self.ORIGIN_Y = 100, self.HEIGHT - 50  # Starting position
            self.G = 9.80665  # Gravity
            self.FPS = 60

            # Wind variables
            self.wind_enabled = False     # Decided at intro screen
            self.wind = 0.0               # Horizontal acceleration
            self.wind_max = 1.0           # Start with 1.0 max wind
            self.wind_arrow_length = 60   # For the single arrow in the corner

            # Colors
            self.MIDNIGHT_BLUE = (25, 25, 112)
            self.WHITE = (255, 255, 255)
            self.RED = (255, 0, 0)
            self.GREEN = (0, 255, 0)
            self.BLUE = (0, 0, 255)
            self.YELLOW = (255, 255, 0)
            self.PURPLE = (128, 0, 128)
            self.COLORS = [self.GREEN, self.BLUE, self.YELLOW, self.PURPLE]

            # Screen setup
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("2D Trajectory with Wind & 3 Strikes")
            self.clock = pygame.time.Clock()

            # Font setup
            self.FONT = pygame.font.Font(None, 36)
            self.MESSAGES_FONT = pygame.font.Font(None, 48)
            self.SMALL_FONT = pygame.font.Font(None, 24)

            self.running = True

            # Angle (0-90) controlled by left/right
            self.angle = 45
            # Power (0-100) controlled by up/down
            self.power = 50

            # Target
            self.target_radius = 10
            self.target_position = self.generate_new_target_position()

            # Level
            self.level = 1

            # 3 attempts (strikes) per level
            self.attempts = 3

            # Feedback message
            self.feedback_message = ""
            self.message_timer = 0

            # Leaderboard
            self.leaderboard_data = self.load_leaderboard()

            # Storing last shot path for dotted line
            self.last_trajectory_points = []
            self.last_trajectory_color = self.WHITE

        except pygame.error as e:
            self.logger.error(f"Pygame initialization failed: {e}")
            self.cleanup()
            raise SystemExit(e)

    # ------------------------------
    # Leaderboard Methods
    # ------------------------------
    def load_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except json.JSONDecodeError:
            pass
        return []

    def save_leaderboard(self):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(self.leaderboard_data, f, indent=4)

    def add_score_to_leaderboard(self, name, level):
        self.leaderboard_data.append({"name": name, "level": level})
        self.leaderboard_data.sort(key=lambda x: x['level'], reverse=True)
        self.leaderboard_data = self.leaderboard_data[:5]
        self.save_leaderboard()

    # ------------------------------
    # Game Logic
    # ------------------------------
    def generate_new_target_position(self):
        x = random.randint(150, self.WIDTH - 50)
        y = self.ORIGIN_Y
        return (x, y)

    def draw_ground(self):
        pygame.draw.line(self.screen, self.WHITE, (0, self.ORIGIN_Y), (self.WIDTH, self.ORIGIN_Y), 2)

    def draw_target(self):
        tx, ty = self.target_position
        pygame.draw.line(self.screen, self.RED, (tx - self.target_radius, ty - self.target_radius),
                         (tx + self.target_radius, ty + self.target_radius), 2)
        pygame.draw.line(self.screen, self.RED, (tx - self.target_radius, ty + self.target_radius),
                         (tx + self.target_radius, ty - self.target_radius), 2)

    def throw_projectile(self, angle, power, color):
        """
        Simulates throwing the projectile with the given angle, power, and color.
        Applies gravity + optional wind acceleration.
        Returns True if target is hit, else False.
        """
        t = 0
        trajectory_points = []

        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        time_multiplier = 3
        dt = (1 / self.FPS) * time_multiplier

        # Convert power into initial velocity (1:1)
        v0 = power

        # Wind as horizontal acceleration
        ax = self.wind
        vx0 = v0 * cos_angle
        vy0 = v0 * sin_angle

        hit_target = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit_pressed = True
                        self.running = False
                        return False

            # Projectile motion
            t += dt
            x = self.ORIGIN_X + vx0 * t + 0.5 * ax * (t ** 2)
            delta_y = (vy0 * t) - (0.5 * self.G * (t ** 2))
            y = self.ORIGIN_Y - delta_y

            # Stop if hits ground or goes off right edge
            if y >= self.ORIGIN_Y or x > self.WIDTH:
                break

            trajectory_points.append((x, y))

            # Draw everything
            self.screen.fill(self.MIDNIGHT_BLUE)
            self.draw_ground()
            self.draw_target()
            self.draw_pivot_point()
            self.draw_aiming_line()

            # Wind visuals
            if self.wind_enabled:
                self.draw_wind_field()
                self.draw_wind_arrow()

            # Dotted line from last shot
            self.draw_last_shot()

            # Draw current shot's trajectory
            for px, py in trajectory_points:
                pygame.draw.circle(self.screen, color, (int(px), int(py)), 3)

            # Current projectile
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 5)

            # Check collision
            if self.check_collision(x, y):
                self.feedback_message = "Hit!"
                self.message_timer = pygame.time.get_ticks()
                self.handle_hit()
                hit_target = True
                break

            self.display_feedback()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        # Store last shot path for dotted line
        self.last_trajectory_points = trajectory_points[:]
        self.last_trajectory_color = color

        # Final draw after motion ends
        self.screen.fill(self.MIDNIGHT_BLUE)
        self.draw_ground()
        self.draw_target()
        self.draw_pivot_point()
        self.draw_aiming_line()
        if self.wind_enabled:
            self.draw_wind_field()
            self.draw_wind_arrow()
        self.draw_last_shot()

        for px, py in trajectory_points:
            pygame.draw.circle(self.screen, color, (int(px), int(py)), 3)

        self.display_feedback()
        pygame.display.flip()

        return hit_target

    def draw_pivot_point(self):
        pygame.draw.circle(self.screen, self.YELLOW, (self.ORIGIN_X, self.ORIGIN_Y), 5)

    def draw_aiming_line(self):
        angle_rad = math.radians(self.angle)
        line_length = 50
        end_x = self.ORIGIN_X + line_length * math.cos(angle_rad)
        end_y = self.ORIGIN_Y - line_length * math.sin(angle_rad)
        pygame.draw.line(self.screen, self.YELLOW, (self.ORIGIN_X, self.ORIGIN_Y), (end_x, end_y), 2)

    def draw_last_shot(self):
        """
        Draw a dotted line for the previous shot.
        """
        if not self.last_trajectory_points:
            return
        for i, (x, y) in enumerate(self.last_trajectory_points):
            if i % 5 == 0:  # skip some points to make it look dotted
                pygame.draw.circle(self.screen, self.last_trajectory_color, (int(x), int(y)), 2)

    def check_collision(self, x, y):
        tx, ty = self.target_position
        dist = math.hypot(x - tx, y - ty)
        return dist <= self.target_radius + 5

    def handle_hit(self):
        """
        Called when target is hit:
         - Increases level
         - Resets attempts
         - Shrinks target (down to min radius 5)
         - Regenerates target
         - If wind enabled, gradually increase wind_max, then re-randomize
        """
        self.level += 1
        self.attempts = 3
        self.target_radius = max(5, self.target_radius - 1)
        self.target_position = self.generate_new_target_position()

        # Increase wind magnitude range as level goes up, capping at 3.0
        if self.wind_enabled:
            self.wind_max = min(3.0, self.wind_max + 0.4)
            self.randomize_wind()

    def randomize_wind(self):
        """
        Random horizontal wind acceleration in [-wind_max, wind_max].
        """
        self.wind = random.uniform(-self.wind_max, self.wind_max)

    def display_feedback(self):
        if self.feedback_message:
            now = pygame.time.get_ticks()
            if now - self.message_timer < 2000:
                msg_surf = self.MESSAGES_FONT.render(self.feedback_message, True, self.YELLOW)
                msg_rect = msg_surf.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
                self.screen.blit(msg_surf, msg_rect)
            else:
                self.feedback_message = ""

    def run(self):
        """
        Main game loop.
        """
        reset_activity_timer()

        # Intro screen for picking wind or not
        self.show_intro_screen()
        if self.wind_enabled:
            self.randomize_wind()

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.user_quit = True
                        self.running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        reset_activity_timer()
                        if event.key == pygame.K_ESCAPE:
                            self.user_quit = True
                            self.running = False
                            break
                        elif event.key == pygame.K_SPACE:
                            hit = self.throw_projectile(self.angle, self.power, random.choice(self.COLORS))
                            if not hit:
                                self.attempts -= 1
                                if self.attempts <= 0:
                                    # Game over
                                    self.feedback_message = "Game Over!"
                                    self.message_timer = pygame.time.get_ticks()
                                    self.end_game_prompt()
                                    self.running = False
                                    break
                        elif event.key == pygame.K_RIGHT:
                            self.angle = max(0, self.angle - 1)  # Right arrow decreases angle
                        elif event.key == pygame.K_LEFT:
                            self.angle = min(90, self.angle + 1) # Left arrow increases angle
                        elif event.key == pygame.K_UP:
                            self.power = min(100, self.power + 1)
                        elif event.key == pygame.K_DOWN:
                            self.power = max(0, self.power - 1)

                # Draw
                self.screen.fill(self.MIDNIGHT_BLUE)
                self.draw_ground()
                self.draw_target()
                self.draw_pivot_point()
                self.draw_aiming_line()
                self.draw_last_shot()

                if self.wind_enabled:
                    self.draw_wind_field()
                    self.draw_wind_arrow()

                angle_text = self.FONT.render(f"Angle: {self.angle}°", True, self.GREEN)
                power_text = self.FONT.render(f"Power: {self.power}", True, self.GREEN)
                instructions = self.FONT.render("ARROWS=Angle/Power, SPACE=Fire, ESC=QUIT", True, self.YELLOW)
                level_text = self.FONT.render(f"Level: {self.level}", True, self.WHITE)
                attempts_text = self.FONT.render(f"Strikes Left: {self.attempts}", True, self.WHITE)

                self.screen.blit(angle_text, (20, 20))
                self.screen.blit(power_text, (20, 60))
                self.screen.blit(instructions, (20, 100))
                self.screen.blit(level_text, (20, 140))
                self.screen.blit(attempts_text, (20, 180))

                self.draw_leaderboard()
                self.display_feedback()

                pygame.display.flip()
                self.clock.tick(self.FPS)

            # If the loop ended *without* attempts dropping to zero and the user did *not* quit,
            # we ask for their name. Otherwise, skip.
            if self.attempts > 0 and not self.user_quit:
                self.end_game_prompt()

            return self.exit_message

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise
        finally:
            pygame.display.quit()
            pygame.quit()
            os.dup2(self.stdin_copy, self.stdin_fd)
            os.close(self.stdin_copy)

    def show_intro_screen(self):
        choosing = True
        selected_option = "No wind"  # Default

        while choosing:
            self.screen.fill((0, 0, 0))
            title = self.MESSAGES_FONT.render("2D Trajectory Demo", True, self.YELLOW)
            title_rect = title.get_rect(center=(self.WIDTH // 2, 80))
            self.screen.blit(title, title_rect)

            sub_text = self.FONT.render(
                "Press W to enable wind, S to disable, then ENTER to begin.",
                True, self.WHITE
            )
            sub_rect = sub_text.get_rect(center=(self.WIDTH // 2, 160))
            self.screen.blit(sub_text, sub_rect)

            current_choice = self.FONT.render(f"Current choice: {selected_option}", True, self.GREEN)
            curr_rect = current_choice.get_rect(center=(self.WIDTH // 2, 220))
            self.screen.blit(current_choice, curr_rect)

            explanation = [
                "Goal: Hit the target. Each level you get 3 strikes.",
                "Hit target to move to next level. The target shrinks each time!",
                "If wind is enabled, there's horizontal acceleration that grows by level.",
                "QUIT at any time with ESC"
            ]
            y_off = 300
            for line in explanation:
                line_surf = self.SMALL_FONT.render(line, True, self.WHITE)
                line_rect = line_surf.get_rect(center=(self.WIDTH // 2, y_off))
                y_off += 30
                self.screen.blit(line_surf, line_rect)

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.user_quit = True
                    self.running = False
                    choosing = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        choosing = False

                    elif event.key == pygame.K_ESCAPE:
                        self.user_quit = True
                        self.running = False
                        choosing = False

                    elif event.key == pygame.K_w:
                        selected_option = "Wind enabled"
                        self.wind_enabled = True

                    elif event.key == pygame.K_s:
                        selected_option = "No wind"
                        self.wind_enabled = False

    def draw_wind_field(self, spacing=80):
        """
        Draw a field of small arrows to visualize wind across the screen.
        Each arrow is drawn at points in a grid. The length/direction
        depends on self.wind; if near zero, draw a dot.
        """
        arrow_color = (200, 200, 200)  # Light gray
        # Scale arrow length so you can see direction
        # but not overshadow everything
        scale = 20 * abs(self.wind)

        for x in range(spacing // 2, self.WIDTH, spacing):
            for y in range(50, self.ORIGIN_Y - 20, spacing):
                # Center the arrow at (x, y)
                if abs(self.wind) < 0.01:
                    # Just draw a small dot if wind ~ 0
                    pygame.draw.circle(self.screen, arrow_color, (x, y), 2)
                else:
                    half_len = max(scale, 5) / 2.0
                    if self.wind > 0:
                        start_pos = (x - half_len, y)
                        end_pos = (x + half_len, y)
                    else:
                        start_pos = (x + half_len, y)
                        end_pos = (x - half_len, y)

                    pygame.draw.line(self.screen, arrow_color, start_pos, end_pos, 2)
                    # Arrow tip
                    tip_size = 5
                    if self.wind > 0:
                        tip_x = end_pos[0]
                        tip_y = end_pos[1]
                        pygame.draw.polygon(self.screen, arrow_color,
                            [(tip_x, tip_y),
                             (tip_x - tip_size, tip_y - tip_size/2),
                             (tip_x - tip_size, tip_y + tip_size/2)])
                    else:
                        tip_x = end_pos[0]
                        tip_y = end_pos[1]
                        pygame.draw.polygon(self.screen, arrow_color,
                            [(tip_x, tip_y),
                             (tip_x + tip_size, tip_y - tip_size/2),
                             (tip_x + tip_size, tip_y + tip_size/2)])

    def draw_wind_arrow(self):
        """
        Small arrow in top-right corner indicating numeric wind.
        """
        text = self.SMALL_FONT.render(f"Wind: {self.wind:.2f}", True, self.WHITE)
        self.screen.blit(text, (self.WIDTH - 130, 80))

        if abs(self.wind) < 0.01:
            # No arrow if wind is effectively zero
            return

        arrow_x = self.WIDTH - 100
        arrow_y = 60

        # Adjust arrow length based on ratio to self.wind_max
        ratio = abs(self.wind) / self.wind_max if self.wind_max != 0 else 0
        length = self.wind_arrow_length * ratio
        length = max(10, length)  # minimal arrow length so it's visible

        if self.wind > 0:
            start_pos = (arrow_x - length/2, arrow_y)
            end_pos = (arrow_x + length/2, arrow_y)
        else:
            start_pos = (arrow_x + length/2, arrow_y)
            end_pos = (arrow_x - length/2, arrow_y)

        pygame.draw.line(self.screen, self.WHITE, start_pos, end_pos, 3)
        # Arrow tip
        tip_size = 10
        if self.wind > 0:
            tip_x = end_pos[0]
            tip_y = end_pos[1]
            pygame.draw.polygon(self.screen, self.WHITE,
                [(tip_x, tip_y),
                 (tip_x - tip_size, tip_y - tip_size/2),
                 (tip_x - tip_size, tip_y + tip_size/2)])
        else:
            tip_x = end_pos[0]
            tip_y = end_pos[1]
            pygame.draw.polygon(self.screen, self.WHITE,
                [(tip_x, tip_y),
                 (tip_x + tip_size, tip_y - tip_size/2),
                 (tip_x + tip_size, tip_y + tip_size/2)])

    def draw_leaderboard(self):
        """
        Draws "Leaderboard (Top 5)" and centers each subsequent entry
        under that header.
        """
        # Draw header near top-right
        header_text = "Leaderboard (Top 5)"
        header_surf = self.FONT.render(header_text, True, self.WHITE)
        header_rect = header_surf.get_rect(topright=(self.WIDTH - 20, 20))
        self.screen.blit(header_surf, header_rect)

        # We'll center the names under the header by using header_rect.centerx
        center_x = header_rect.centerx
        y_pos = header_rect.bottom + 20  # Some spacing after the header

        for entry in self.leaderboard_data:
            text_str = f"{entry['name']} - Lvl {entry['level']}"
            row_text = self.SMALL_FONT.render(text_str, True, self.WHITE)
            row_rect = row_text.get_rect()
            row_rect.centerx = center_x
            row_rect.top = y_pos
            self.screen.blit(row_text, row_rect)
            y_pos += row_rect.height + 5

    def end_game_prompt(self):
        """
        Ends the game, prompting for a name if user wants to save.
        """
        self.show_popup_message(f"You reached Level {self.level}!", color=self.YELLOW, duration=500)
        name = self.prompt_for_name()
        if name:
            self.add_score_to_leaderboard(name, self.level)
            self.exit_message = "Successfully Logged Score"
        else:
            self.exit_message = "Leaving Trajectory Demo"

    def prompt_for_name(self):
        """
        Opens an overlay to type name. ENTER to confirm, ESC to skip.
        Returns the typed string, or None if cancelled/empty.
        """
        pygame.event.clear()

        input_box = pygame.Rect(self.WIDTH//2 - 100, self.HEIGHT//2, 200, 40)
        user_text = ""
        active = True

        while active:
            self.screen.fill((0,0,0))
            prompt_label = self.FONT.render("Enter your name for the leaderboard (or ESC to skip):", True, self.WHITE)
            self.screen.blit(prompt_label, (self.WIDTH//2 - prompt_label.get_width()//2, self.HEIGHT//2 - 40))

            pygame.draw.rect(self.screen, self.WHITE, input_box, 2)

            text_surface = self.FONT.render(user_text, True, self.WHITE)
            self.screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_RETURN:
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        # Limit name length to 10
                        if len(user_text) < 10 and event.unicode.isprintable():
                            user_text += event.unicode

        user_text = user_text.strip()
        return user_text if user_text else None

    def show_popup_message(self, text, color, duration=2000):
        start_time = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            if now - start_time > duration:
                break

            self.screen.fill((0, 0, 0))
            label = self.MESSAGES_FONT.render(text, True, color)
            rect = label.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
            self.screen.blit(label, rect)
            pygame.display.flip()
            self.clock.tick(30)

    def cleanup(self):
        pygame.display.quit()
        pygame.quit()
        os.dup2(self.stdin_copy, self.stdin_fd)
        os.close(self.stdin_copy)
