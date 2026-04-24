import pygame
import numpy as np
import random
import math

class BlackHoleMapping1D:
    def __init__(self):
        # These will be set when the probe is launched.
        self.probe_launched = False
        self.probe_pos = 0.0  # Normalized (0 = observer, 1 = BH center)
        self.event_horizon_crossed = False
        self.redshift_data = []  # List of (distance_from_us_AU, visual_wavelength)
        self.escape_cursor = 0.0 # normalized 0-1 (0 = observer, 1 = event-horizon)
        self.cursor_speed = 0.01 # how fast ↑/↓ moves the cursor
        
        # True physical values (set at probe launch)
        self.bh_true_depth_au = None   # Physical depth in AU (we'll fix the top as 100 AU)
        self.bh_true_radius_au = None  # Schwarzschild radius (in AU)
        self.bh_mass_geom = None
        self.bh_mass_solar = None

    def run(self):
        pygame.init()
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Black Hole Photon Intensity Sweep (1D)")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('Arial', 16)
        pygame.mouse.set_visible(False)

        # Set a fixed physical depth for the simulation.
        PHYSICAL_DEPTH_AU = 100  # We want the redshift graph to represent 0–100 AU.
        
        # -------------------------------------
        # BH & Sweep Parameters for Intensity Mapping
        # -------------------------------------
        bh_angle = random.uniform(0.1 * np.pi, 0.9 * np.pi)
        # The sweep line’s visual length is fixed (purely visual).
        sweep_line_length = 150  
        b_E = 0.2
        sigma = 0.05
        shadow_radius = 0.03
        epsilon = 1e-6

        angle = np.pi / 2
        angle_step = 0.005
        intensity_data = []  # (angle, intensity)

        min_angle, max_angle = 0, np.pi
        angles_for_expected = np.arange(0, np.pi, 0.001)
        valid_angles = [a for a in angles_for_expected 
                        if np.exp(-(((abs(a - bh_angle) - b_E)**2)/(2*sigma**2))) > 0.1 
                        and abs(a - bh_angle) >= shadow_radius]
        if valid_angles:
            expected_min = min(valid_angles)
            expected_max = max(valid_angles)
        else:
            expected_min, expected_max = 0, np.pi
        expected_range = expected_max - expected_min

        # -------------------------------------
        # Graph Rectangles:
        # Place graphs on the side opposite the BH.
        graph_spacing = 25
        graph_height = 150

        if bh_angle < np.pi / 2:
            # BH on right → graphs on left
            intensity_rect = (50, height - 50 - graph_height, 300, graph_height)
            redshift_rect  = (50, height - 50 - 2 * graph_height - graph_spacing, 300, graph_height)
        else:
            # BH on left → graphs on right
            intensity_rect = (width - 350, height - 50 - graph_height, 300, graph_height)
            redshift_rect  = (width - 350, height - 50 - 2 * graph_height - graph_spacing, 300, graph_height)

        # -------------------------------------
        # Redshift constants (in nm)
        BASE_WAVELENGTH_NM = 10
        STOP_WAVELENGTH_NM = 1000

        def calc_intensity(a, target):
            diff = abs(a - target)
            inten = np.exp(-((diff - b_E)**2)/(2*sigma**2))
            if diff < shadow_radius:
                inten = 0
            return inten

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                angle = min(np.pi, angle + angle_step)
            if keys[pygame.K_RIGHT]:
                angle = max(0, angle - angle_step)
            if keys[pygame.K_SPACE]:
                intensity = calc_intensity(angle, bh_angle)
                if not any(abs(angle - rec_angle) < 0.005 for rec_angle, _ in intensity_data):
                    intensity_data.append((angle, intensity))
            if keys[pygame.K_ESCAPE]:
                running = False

            # Launch probe when P is pressed.
            if keys[pygame.K_p] and not self.probe_launched:
                self.probe_launched = True
                self.probe_pos = 0.0
                self.event_horizon_crossed = False
                self.redshift_data.clear()
                # Here we set the true depth to the fixed constant.
                self.bh_true_depth_au = PHYSICAL_DEPTH_AU
                # Use a fixed visual BH radius (in pixels) for scaling (for example, 50 pixels).
                bh_visual_radius_px = 50  
                # We want to scale such that the available space from the observer (bottom) to a top margin represents 100 AU.
                # Let’s define the observer at (width//2, height - 30) and top margin at 50 pixels.
                base_y = height - 30
                top_margin = 50
                available_space = base_y - top_margin  # in pixels
                PIXELS_PER_AU = available_space / self.bh_true_depth_au
                # Compute the true Schwarzschild radius (in AU) using the visual BH radius.
                self.bh_true_radius_au = bh_visual_radius_px * (self.bh_true_depth_au / (width / 2))
                # Compute mass (in geometrized units, then convert to solar masses)
                self.bh_mass_geom = self.bh_true_radius_au / 2
                self.bh_mass_solar = self.bh_mass_geom / 4.9255e-6

            # ---------------------------
            # Draw Main Scene and Helper Instructions at Top
            # ---------------------------
            helper_instr = font.render("LEFT/RIGHT: Adjust angle | SPACE: Record intensity | P: Launch probe | ESC: Quit", True, (255,255,255))
            screen.fill((0, 0, 0))
            screen.blit(helper_instr, (width//2 - helper_instr.get_width()//2, 10))
            # If probe has finished, display summary near the top.
            if self.probe_launched and self.event_horizon_crossed:
                summary_text = (f"Mass (Solar Masses): {self.bh_mass_solar:.2f} MO | Depth: {self.bh_true_depth_au:.2f} AU | "
                                f"Diameter: {2 * self.bh_true_radius_au:.2f} AU")
                summary_label = font.render(summary_text, True, (255,255,0))
                screen.blit(summary_label, (width//2 - summary_label.get_width()//2, helper_instr.get_height() + 15))

            # ---------------------------
            # Draw the Sweep Line (purely visual) & Observer
            # ---------------------------
            base_x, base_y = width//2, height - 30
            end_x = base_x + math.cos(angle) * sweep_line_length
            end_y = base_y - math.sin(angle) * sweep_line_length
            pygame.draw.line(screen, (255,255,255), (base_x, base_y), (end_x, end_y), 1)
            pygame.draw.circle(screen, (255,255,255), (base_x, base_y), 5)

            # ---------------------------
            # Draw Light Intensity Graph with Rotated Axis Labels
            # ---------------------------
            gx, gy, gw, gh = intensity_rect
            pygame.draw.rect(screen, (50,50,50), intensity_rect)
            pygame.draw.rect(screen, (200,200,200), intensity_rect, 1)
            for a, inten in intensity_data:
                px = gx + ((a - min_angle) / (max_angle - min_angle)) * gw
                py = gy + gh - inten * gh
                pygame.draw.circle(screen, (0,255,0), (int(px), int(py)), 2)
            x_label = font.render("Angle Position", True, (255,255,255))
            screen.blit(x_label, (gx + gw//2 - x_label.get_width()//2, gy + gh + 5))
            y_label = font.render("Light Intensity", True, (255,255,255))
            y_label_rot = pygame.transform.rotate(y_label, 90)
            screen.blit(y_label_rot, (gx - y_label_rot.get_width() - 5, gy + gh//2 - y_label_rot.get_height()//2))

            # ---------------------------
            # Red Direction Indicator
            # ---------------------------
            user_valid_angles = [a for a, inten in intensity_data if inten > 0.1]
            data_range = max(user_valid_angles) - min(user_valid_angles) if user_valid_angles else 0
            if data_range >= 0.65 * expected_range:
                red_line_length = 50
                num_dots = 10
                for i in range(1, num_dots+1):
                    dot_x = base_x + math.cos(bh_angle) * red_line_length * (i/num_dots)
                    dot_y = base_y - math.sin(bh_angle) * red_line_length * (i/num_dots)
                    pygame.draw.circle(screen, (255,0,0), (int(dot_x), int(dot_y)), 2)
                if not self.probe_launched:
                    probe_prompt = font.render("Press P to send probe", True, (255,255,255))
                    screen.blit(probe_prompt, (base_x - probe_prompt.get_width()//2, base_y - 30))

            # ---------------------------
            # Compute and Draw Probe and Redshift Information
            # ---------------------------
            if self.probe_launched and self.probe_pos < 1.0:
                self.probe_pos += 0.002  # Constant speed
                self.probe_pos = min(self.probe_pos, 1.0)
                # Compute physical distance from observer in AU.
                dist_from_us_au = self.probe_pos * self.bh_true_depth_au
                distance_to_bh_center = self.bh_true_depth_au - dist_from_us_au

                r_probe = max(distance_to_bh_center, self.bh_true_radius_au)
                z = 1 / math.sqrt(max(1 - (self.bh_true_radius_au / r_probe), epsilon)) - 1
                wavelength_nm = BASE_WAVELENGTH_NM * (1 + z)
                wavelength_visual = min(wavelength_nm, 200)
                self.redshift_data.append((dist_from_us_au, wavelength_visual))
                
                event_horizon_dist = self.bh_true_depth_au - self.bh_true_radius_au
                if wavelength_nm >= STOP_WAVELENGTH_NM or dist_from_us_au >= event_horizon_dist:
                    self.event_horizon_crossed = True
                    self.probe_pos = event_horizon_dist / self.bh_true_depth_au

                # Compute probe's visual position using the fixed pixels-per-AU scale.
                # Calculate available vertical space from observer (base_y) to a top margin (say, 50 pixels).
                top_margin = 50
                available_space = base_y - top_margin
                PIXELS_PER_AU = available_space / self.bh_true_depth_au
                
                probe_distance_px = dist_from_us_au * PIXELS_PER_AU
                probe_x = base_x + math.cos(bh_angle) * probe_distance_px
                probe_y = base_y - math.sin(bh_angle) * probe_distance_px

                probe_size = 4  # Constant small size
                factor = (wavelength_visual - 10) / 140  # 140 = more aggressive transition
                factor = max(0, min(factor, 1))          # Clamp between 0 and 1
                factor = factor ** 1.8                   # Exaggerate early redshift

                # Now use the clamped, curved factor
                r = int(255 * factor)
                g = 0
                b = int(255 * (1 - factor))
                probe_color = (r, g, b)

                pygame.draw.circle(screen, probe_color, (int(probe_x), int(probe_y)), probe_size)
                dave_label = font.render("dave", True, (255,255,255))
                screen.blit(dave_label, (probe_x - dave_label.get_width()//2, probe_y + probe_size + 2))
                if not self.event_horizon_crossed:
                    au_label = font.render(f"{dist_from_us_au:.1f} AU", True, (255,255,255))
                    screen.blit(au_label, (probe_x - au_label.get_width()//2, probe_y - probe_size - 25))

            # ---------------------------
            # Draw a Prominent Event Horizon Marker on the Main Sweep Line
            # ---------------------------
            if self.event_horizon_crossed:
                # Compute the event horizon position based on physical scaling.
                event_horizon_dist = self.bh_true_depth_au - self.bh_true_radius_au
                # Use the same PIXELS_PER_AU as computed above.
                top_margin = 50
                available_space = (height - 30) - top_margin
                PIXELS_PER_AU = available_space / self.bh_true_depth_au
                event_horizon_px = event_horizon_dist * PIXELS_PER_AU
                eh_x = base_x + math.cos(bh_angle) * event_horizon_px
                eh_y = base_y - math.sin(bh_angle) * event_horizon_px
                perp = np.array([-math.sin(bh_angle), -math.cos(bh_angle)])
                perp_norm = perp / np.linalg.norm(perp)
                marker_length = 20
                marker_start = (eh_x + perp_norm[0]*marker_length/2, eh_y + perp_norm[1]*marker_length/2)
                marker_end = (eh_x - perp_norm[0]*marker_length/2, eh_y - perp_norm[1]*marker_length/2)
                pygame.draw.line(screen, (255,255,255),
                                 (int(marker_start[0]), int(marker_start[1])),
                                 (int(marker_end[0]), int(marker_end[1])), 3)
                pygame.draw.circle(screen, (255,255,255), (int(eh_x), int(eh_y)), 8, 2)
                # Place event horizon label 30 pixels above the marker.
                eh_text = font.render("Event Horizon", True, (255,255,255))
                screen.blit(eh_text, (int(eh_x) - eh_text.get_width()//2, int(eh_y) - 30))

            # ---------------------------
            # Draw Redshift Mini Graph (0–100 AU) Above the Intensity Graph
            # ---------------------------
            rx, ry, rw, rh = redshift_rect
            pygame.draw.rect(screen, (50,50,50), redshift_rect)
            pygame.draw.rect(screen, (200,200,200), redshift_rect, 1)
            if len(self.redshift_data) > 1:
                for i in range(len(self.redshift_data)-1):
                    x1 = rx + (self.redshift_data[i][0] / PHYSICAL_DEPTH_AU) * rw
                    y1 = ry + rh - (self.redshift_data[i][1] / 200) * rh
                    x2 = rx + (self.redshift_data[i+1][0] / PHYSICAL_DEPTH_AU) * rw
                    y2 = ry + rh - (self.redshift_data[i+1][1] / 200) * rh
                    pygame.draw.line(screen, (255,150,150), (x1,y1), (x2,y2), 2)
                # Show current AU value on the redshift graph (last point)
                if self.redshift_data:
                    last_au, last_wavelength = self.redshift_data[-1]
                    x_val = rx + (last_au / PHYSICAL_DEPTH_AU) * rw
                    y_val = ry + rh - (last_wavelength / 200) * rh
                    # AU label near the dot
                    au_label = font.render(f"{last_au:.1f} AU", True, (255, 255, 255))
                    screen.blit(au_label, (x_val - au_label.get_width() // 2, y_val - 20))
                    # Optional: draw a small dot to highlight the current position
                    pygame.draw.circle(screen, (255, 255, 255), (int(x_val), int(y_val)), 3)
                if self.event_horizon_crossed:
                    event_horizon_x = rx + ((PHYSICAL_DEPTH_AU - self.bh_true_radius_au) / PHYSICAL_DEPTH_AU) * rw
                    pygame.draw.line(screen, (255,255,255), (event_horizon_x,ry), (event_horizon_x,ry+rh), 2)
                    eh_label_graph = font.render("Event Horizon", True, (255,255,255))
                    screen.blit(eh_label_graph, (event_horizon_x - eh_label_graph.get_width() // 2, ry + rh + 5))
            x_label_rz = font.render("Distance (AU)", True, (255,255,255))
            screen.blit(x_label_rz, (rx + rw//2 - x_label_rz.get_width()//2, ry + rh + 5))
            y_label_rz = font.render("Wavelength (nm)", True, (255,255,255))
            y_label_rz_rot = pygame.transform.rotate(y_label_rz, 90)
            screen.blit(y_label_rz_rot, (rx - y_label_rz_rot.get_width() - 5, ry + rh//2 - y_label_rz_rot.get_height()//2))

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

# ----------------------------------------------------------------------

class PhiScanLine:
    def __init__(self, x, start_time):
        self.x = x  # Fixed x coordinate at spawn.
        self.positions = [(x, 0)]  # Starting at y = 0.
        self.start_time = start_time

    def update(self, phi_speed):
        last_x, last_y = self.positions[-1]
        new_y = last_y + phi_speed
        self.positions.append((self.x, new_y))
    
    def is_off_screen(self, screen_height):
        return self.positions[-1][1] > screen_height
    
# ----------------------------------------------------------------------

class BlackHoleMapping2D:
    """
    2D Black Hole Mapping:
    - The main screen is our mapping region.
    - A crosshair cursor (theta) moves left/right.
    - Holding SPACE draws a dashed vertical scan line (to gather mapping data).
    - A visual black hole is drawn, but its true physical depth (in AU) is unknown until the probe is launched.
    - When enough scan data is collected, an overlay appears prompting you to launch "Commander Dave".
    - Upon launch, a true depth (between 10 and 100 AU) is randomized. The true diameter and mass (in solar masses)
      are computed from the visual size and depth.
    - The probe travels from 0 AU (observer) toward the event horizon. Its apparent size starts large and shrinks,
      and its distance (in AU) increases. When the event horizon is reached (wavelength saturates at 200),
      the probe stops and fades away.
    - A redshift graph (with an x‑axis always from 0–100 AU) shows the redshift evolution and marks the event horizon.
    - Finally, a summary of the black hole’s mass, depth, and diameter is displayed with dynamic placement.
    """
    def __init__(self):
        self.width = 800
        self.height = 600

        # Until probe launch, AU scale is unknown.
        self.pixel_scale = 1  # Placeholder

        # Crosshair initial position.
        self.cursor_x = self.width // 2
        self.cursor_y = self.height // 2
        self.cursor_speed = 2

        # Visual black hole placement and size.
        self.bh_x = random.randint(100, self.width - 100)
        self.bh_y = random.randint(100, self.height - 100)
        self.bh_radius_px = random.randint(30, 60)  # Visual radius in pixels

        # True AU values (depth, diameter, radius, mass) are unknown until probe launch.
        self.bh_true_depth_au = None
        self.bh_true_diameter_au = None
        self.bh_true_radius_au = None
        self.bh_mass_geom = None
        self.bh_mass_solar = None

        # Mini-map setup.
        self.mini_width = 200
        self.mini_height = 150
        self.mini_surface = pygame.Surface((self.mini_width, self.mini_height))
        self.mini_surface.fill((50, 50, 50))
        self.scanned_columns = set()
        self.expected_bh_columns = 2 * (self.bh_radius_px / self.width * self.mini_width)
        self.scan_data = []
        self.overlay_active = False
        self.overlay_update_time = 0

        # Commander Dave probe attributes.
        self.probe_launched = False
        self.probe_pos = 0.0  # Normalized: 0 = observer, 1 = event horizon.
        self.probe_speed = 0.003
        self.event_horizon_crossed = False
        self.redshift_data = []  # (probe_pos, wavelength, dist_from_us_au)
        self.probe_fade_alpha = 255  # For fade-out animation
        self.final_depth_measured_au = None

    def draw_dashed_line(self, surface, start, end, dash_length=10, gap_length=5, color=(255, 255, 255)):
        x1, y1 = start
        x2, y2 = end
        total_length = math.hypot(x2 - x1, y2 - y1)
        dx = (x2 - x1) / total_length
        dy = (y2 - y1) / total_length
        dash_gap = dash_length + gap_length
        num_dashes = int(total_length / dash_gap)
        for i in range(num_dashes + 1):
            start_x = x1 + i * dash_gap * dx
            start_y = y1 + i * dash_gap * dy
            end_x = start_x + dash_length * dx
            end_y = start_y + dash_length * dy
            if math.hypot(end_x - x1, end_y - y1) > total_length:
                end_x = x2
                end_y = y2
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)

    def update_mini_graph(self, scan_x):
        if abs(scan_x - self.bh_x) <= self.bh_radius_px:
            half_chord = math.sqrt(self.bh_radius_px**2 - (scan_x - self.bh_x)**2)
            int_top = self.bh_y - half_chord
            int_bottom = self.bh_y + half_chord
            mini_x = int(scan_x / self.width * self.mini_width)
            mini_top = int(int_top / self.height * self.mini_height)
            mini_bottom = int(int_bottom / self.height * self.mini_height)
            pygame.draw.line(self.mini_surface, (0, 255, 0), (mini_x, mini_top), (mini_x, mini_bottom), 2)
            self.scanned_columns.add(mini_x)
            if not any(abs(d[0] - scan_x) < 1 for d in self.scan_data):
                self.scan_data.append((scan_x, int_top, int_bottom))

    def draw_mini_map(self, screen, font):
        mini_pos = (self.width - self.mini_width - 10, 10)
        screen.blit(self.mini_surface, mini_pos)
        pygame.draw.rect(screen, (200, 200, 200), (mini_pos[0], mini_pos[1], self.mini_width, self.mini_height), 1)
        label_surf = font.render("mini map", True, (255, 255, 255))
        label_x = mini_pos[0] + (self.mini_width - label_surf.get_width()) // 2
        label_y = mini_pos[1] + 5
        screen.blit(label_surf, (label_x, label_y))
        mini_cursor_x = int(self.cursor_x / self.width * self.mini_width)
        tick_height = 10
        tick_x = mini_pos[0] + mini_cursor_x
        tick_y = mini_pos[1] + self.mini_height - tick_height
        pygame.draw.line(screen, (255, 0, 0), (tick_x, tick_y), (tick_x, tick_y + tick_height), 2)

    def draw_overlay(self, surface):
        margin = 20
        region_x = max(0, self.bh_x - self.bh_radius_px - margin)
        region_y = max(0, self.bh_y - self.bh_radius_px - margin)
        region_w = min(self.width - region_x, 2 * (self.bh_radius_px + margin))
        region_h = min(self.height - region_y, 2 * (self.bh_radius_px + margin))
        overlay_surf = pygame.Surface((region_w, region_h), pygame.SRCALPHA)
        overlay_surf.fill((0, 0, 100, 180))
        scan_line_spacing = 10
        retro_line_color = (150, 150, 150, 100)
        for y in range(0, region_h, scan_line_spacing):
            pygame.draw.line(overlay_surf, retro_line_color, (0, y), (region_w, y), 1)
        for x in range(0, region_w, scan_line_spacing):
            pygame.draw.line(overlay_surf, retro_line_color, (x, 0), (x, region_h), 1)
        overlay_bh_x = self.bh_x - region_x
        overlay_bh_y = self.bh_y - region_y
        band_threshold = 5
        for (scan_x, int_top, int_bottom) in self.scan_data:
            if region_x <= scan_x <= region_x + region_w:
                overlay_x = int(scan_x - region_x)
                chord_len = int_bottom - int_top
                steps = max(2, int(chord_len) // 4)
                for i in range(steps):
                    sy = int_top + i * (chord_len / (steps - 1))
                    overlay_y = int(sy - region_y)
                    dx = overlay_x - overlay_bh_x
                    dy = overlay_y - overlay_bh_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if abs(dist - self.bh_radius_px) < band_threshold:
                        intensity = math.exp(-((dist - self.bh_radius_px) ** 2) / (2 * (band_threshold / 2) ** 2))
                        g_val = int(255 * intensity)
                        color = (0, g_val, 0, 255)
                        pygame.draw.circle(overlay_surf, color, (overlay_x, overlay_y), 2)
        pygame.draw.rect(overlay_surf, (255, 255, 0), (0, 0, region_w, region_h), 2)
        overlay_font = pygame.font.SysFont('Arial', 14)
        label = overlay_font.render("Digital Overlay", True, (255, 255, 255))
        label_x = (region_w - label.get_width()) // 2
        overlay_surf.blit(label, (label_x, 2))
        surface.blit(overlay_surf, (region_x, region_y))

    def draw_tick_marks(self, surface, font):
        margin_left_line = 10
        margin_left_label = 15
        for angle in range(0, 181, 45):
            y = self.height - int((angle / 180) * self.height)
            pygame.draw.line(surface, (255, 255, 255), (margin_left_line, y), (20, y), 2)
            label = font.render(f"{angle}°", True, (255, 255, 255))
            surface.blit(label, (margin_left_label, y - label.get_height() // 2))

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Black Hole Mapping - 2D Version")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('Arial', 16)
        pygame.mouse.set_visible(False)

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.cursor_x = max(0, self.cursor_x - self.cursor_speed)
            if keys[pygame.K_RIGHT]:
                self.cursor_x = min(self.width, self.cursor_x + self.cursor_speed)

            screen.fill((0, 0, 0))
            pygame.draw.line(screen, (100, 100, 100), (0, 0), (0, self.height), 2)
            pygame.draw.line(screen, (100, 100, 100), (self.width, 0), (self.width, self.height), 2)
            self.draw_tick_marks(screen, font)

            if keys[pygame.K_SPACE]:
                self.draw_dashed_line(screen, (self.cursor_x, 0), (self.cursor_x, self.height),
                                       dash_length=10, gap_length=5, color=(255, 255, 255))
                self.update_mini_graph(self.cursor_x)

            # Draw crosshair (angle only).
            ch_size = 8
            pygame.draw.line(screen, (255, 255, 0),
                             (self.cursor_x - ch_size, self.cursor_y),
                             (self.cursor_x + ch_size, self.cursor_y), 2)
            pygame.draw.line(screen, (255, 255, 0),
                             (self.cursor_x, self.cursor_y - ch_size),
                             (self.cursor_x, self.cursor_y + ch_size), 2)
            current_theta = (self.cursor_x / self.width) * 180
            info_label = font.render(f"Theta: {current_theta:.1f}°", True, (255, 255, 255))
            screen.blit(info_label, (self.cursor_x + 10, self.cursor_y - info_label.get_height() - 5))

            instr = font.render("LEFT/RIGHT: Move crosshair. HOLD SPACE: Scan. ESC: Quit.", True, (255, 255, 255))
            screen.blit(instr, (20, 20))
            self.draw_mini_map(screen, font)

            # Activate overlay when sufficient scan data is collected.
            if len(self.scanned_columns) >= 0.6 * self.expected_bh_columns:
                if current_time - self.overlay_update_time > 500:
                    self.overlay_update_time = current_time
                    self.overlay_active = True
                if self.overlay_active:
                    self.draw_overlay(screen)

            # Commander Dave Probe Launch & Animation.
            if self.overlay_active and not self.probe_launched:
                pygame.draw.circle(screen, (255, 0, 0), (self.bh_x, self.bh_y), 6)
                text_probe = font.render("Press P to launch Commander Dave", True, (255, 100, 100))
                screen.blit(text_probe, (self.bh_x - text_probe.get_width() // 2, self.bh_y - self.bh_radius_px - 45))
                if keys[pygame.K_p]:
                    self.probe_launched = True
                    self.probe_pos = 0.0
                    self.event_horizon_crossed = False
                    self.redshift_data.clear()
                    self.probe_fade_alpha = 255

                    # Randomize true depth (10 to 100 AU) and compute true diameter & radius.
                    self.bh_true_depth_au = random.uniform(10.0, 100.0)
                    self.bh_true_diameter_au = 2 * self.bh_radius_px * (self.bh_true_depth_au / (self.width / 2))
                    self.bh_true_radius_au = self.bh_true_diameter_au / 2

                    # Mass from Schwarzschild radius (geometrized) and conversion to solar masses.
                    self.bh_mass_geom = self.bh_true_radius_au / 2
                    self.bh_mass_solar = self.bh_mass_geom / 4.9255e-6

            if self.probe_launched:
                if not self.event_horizon_crossed:
                    effective_speed = self.probe_speed * (1 - 0.7 * self.probe_pos)
                    self.probe_pos += effective_speed
                    self.probe_pos = min(self.probe_pos, 1.0)

                    # Compute probe's screen position.
                    probe_x = (1 - self.probe_pos) * (self.width / 2) + self.probe_pos * self.bh_x
                    probe_y = (1 - self.probe_pos) * self.height + self.probe_pos * self.bh_y

                    # Updated logic: Depth from observer (0 AU) to BH center
                    dist_from_us_au = self.probe_pos * self.bh_true_depth_au
                    distance_to_bh_center = self.bh_true_depth_au - dist_from_us_au

                    # **Correct calculation:** Event horizon radius is the Schwarzschild radius (self.bh_true_radius_au)
                    r_probe = max(distance_to_bh_center, self.bh_true_radius_au)
                    z = 1 / math.sqrt(max(1 - self.bh_true_radius_au / r_probe, 1e-6)) - 1
                    wavelength = min(10 + z * 20, 200)

                    self.redshift_data.append((self.probe_pos, wavelength, dist_from_us_au))

                    # If probe reaches Schwarzschild radius (center), stop and fade
                    if distance_to_bh_center <= self.bh_true_radius_au:
                        self.event_horizon_crossed = True
                        self.final_depth_measured_au = dist_from_us_au

                    if self.event_horizon_crossed:
                        self.probe_fade_alpha = max(self.probe_fade_alpha - 5, 0)

                    # Probe size decreases as it approaches
                    probe_size = int(20 * (1 - 0.8 * self.probe_pos)) + 4
                    color_factor = min(max((wavelength - 10) / 190, 0), 1)
                    probe_color = (int(255 * color_factor), 0, int(255 * (1 - color_factor)), self.probe_fade_alpha)
                    probe_surface = pygame.Surface((probe_size*2, probe_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(probe_surface, probe_color, (probe_size, probe_size), probe_size)
                    screen.blit(probe_surface, (probe_x - probe_size, probe_y - probe_size))

                    # Add "dave" label below probe
                    dave_label = font.render("Commander Dave", True, (255, 255, 255))
                    screen.blit(dave_label, (probe_x - dave_label.get_width() // 2, probe_y + probe_size + 2))

                    # Distance AU label
                    au_label = font.render(f"{dist_from_us_au:.1f} AU", True, (255, 255, 255))
                    screen.blit(au_label, (probe_x - au_label.get_width() // 2, probe_y - probe_size - 25))


            if self.probe_launched:
                if self.bh_x < self.width / 2:
                    graph_rect = pygame.Rect(self.width - 320, self.height - 180, 300, 150)
                else:
                    graph_rect = pygame.Rect(20, self.height - 180, 300, 150)
                pygame.draw.rect(screen, (10, 10, 10), graph_rect)
                pygame.draw.rect(screen, (200, 200, 200), graph_rect, 1)

                if len(self.redshift_data) > 1:
                    horizon_drawn = False
                    for i in range(len(self.redshift_data) - 1):
                        _, wl1, au1 = self.redshift_data[i]
                        _, wl2, au2 = self.redshift_data[i + 1]
                        x1 = graph_rect.x + (au1 / 100) * graph_rect.width
                        x2 = graph_rect.x + (au2 / 100) * graph_rect.width
                        y1 = graph_rect.y + graph_rect.height - (wl1 / 200) * graph_rect.height
                        y2 = graph_rect.y + graph_rect.height - (wl2 / 200) * graph_rect.height
                        pygame.draw.line(screen, (255, 100, 100), (x1, y1), (x2, y2), 2)
                        if not horizon_drawn and wl2 >= 200:
                            pygame.draw.line(screen, (255, 255, 0), (x2, graph_rect.y),
                                             (x2, graph_rect.y + graph_rect.height), 2)
                            eh_label = font.render("Event Horizon", True, (255, 255, 0))
                            screen.blit(eh_label, (x2 - eh_label.get_width() // 2, graph_rect.y - 20))
                            horizon_drawn = True

                wl_label = font.render("Wavelength (Redshift)", True, (255, 100, 100))
                screen.blit(wl_label, (graph_rect.x + 5, graph_rect.y + 5))
                for au_mark in np.linspace(0, 100, num=5):
                    mark_x = graph_rect.x + (au_mark / 100) * graph_rect.width
                    pygame.draw.line(screen, (255, 255, 255),
                                     (mark_x, graph_rect.y + graph_rect.height),
                                     (mark_x, graph_rect.y + graph_rect.height + 5), 1)
                    mark_label = font.render(f"{au_mark:.0f}", True, (255, 255, 255))
                    screen.blit(mark_label, (mark_x - mark_label.get_width() // 2,
                                             graph_rect.y + graph_rect.height + 7))

            # Display BH summary info after the event horizon is reached.
            if self.probe_launched and self.event_horizon_crossed and self.final_depth_measured_au is not None:
                info_text = (f"Mass(Solar Masses): {self.bh_mass_solar:.1f} MO | "
                             f"Depth: {self.final_depth_measured_au:.2f} AU | "
                             f"Diameter: {self.bh_true_diameter_au:.2f} AU")
                info_label = font.render(info_text, True, (255, 255, 0))
                # Compute desired x,y for summary text ensuring it stays on screen.
                new_x = self.bh_x - info_label.get_width() // 2
                margin = 10
                if new_x < margin:
                    new_x = margin
                elif new_x + info_label.get_width() > self.width - margin:
                    new_x = self.width - margin - info_label.get_width()
                if self.bh_y < self.height / 2:
                    new_y = self.bh_y + self.bh_radius_px + 30
                    if new_y + info_label.get_height() > self.height - margin:
                        new_y = self.height - margin - info_label.get_height()
                else:
                    new_y = self.bh_y - self.bh_radius_px - 60
                    if new_y < margin:
                        new_y = margin
                screen.blit(info_label, (new_x, new_y))

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

# ----------------------------------------------------------------------
# Create a single "master" class that can run either 1D or 2D
# ----------------------------------------------------------------------
class BlackHoleMapping:
    def __init__(self):
        # Prepare both versions internally
        self.bh_1d = BlackHoleMapping1D()
        self.bh_2d = BlackHoleMapping2D()

    def run(self):
        welcome_message = '''
    Welcome to the Black Hole Mapping Simulator!

    This tool shows how scientists can find and study black holes — objects so massive that not even light can escape them.

    What You'll See:
    • Light Bending (Gravitational Lensing):
        When light passes near a black hole, it bends and forms a ring shape.
        You'll scan across space to find this ring.
    
    • Two Modes:
        - 1D Mode: A simple side-to-side scan to detect light intensity.
        - 2D Mode: A full map that builds up as you scan, with a mini-map view.

    • Launch the Probe ("Commander Dave"):
        After scanning, you’ll launch a probe into the black hole.
        As it gets closer, its light stretches (redshifts) until it disappears.
        This helps us measure the black hole’s size and mass.

    Why It's Cool:
    You’re simulating real techniques scientists use to detect black holes —
    all through the light we can still see around them.

    Choose a Mode to Start:
    Type '1D' for a basic scan, or '2D' for the full map view.
    '''
        print(welcome_message)
        choice = input("Select mode: '1D' or '2D' -> ").strip().lower()
        if choice == '1d':
            self.bh_1d.run()
        elif choice == 'exit':
            return
        else:
            self.bh_2d.run()
