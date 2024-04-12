import sqlite3
import sys
import os
import pygame
import math
import signal
import glob
import subprocess
# import readline # for raspi

from DilationClasses import *
from timer_utils import*


def print_tabbed(text, tab_width=25):
    tab = ' ' * tab_width  # Create a string of spaces to represent the tab
    lines = text.split('\n')  # Split the text into lines
    for line in lines:
        print(tab + line)

def tabbed_input(prompt, tab_width=25):
    tab = ' ' * tab_width  # Create a string of spaces to represent the tab
    try:
        return input(f"{tab}{prompt}")
    except EOFError:
        print("\nInput interrupted. Please try again or use the designated exit command.")
        return ""  # Return an empty string or handle this case as you see fit

class Terminal:
    def __init__(self):
        self.counter = Counter()  # Initialize the counter object
        Input.setup_database() # Setting up the deep messages database
        self.commands = {
            "help": self.show_help,
            "greetings": self.greet,
            "gear demo": self.gearDemo_command,
            "forwards": self.forwards,
            "backwards": self.backwards,
            "input": self.input_command,
            "read": self.read_command,
            "time dilation": self.dilation_command,
            "progression" : self.progression_command,
            "credits" : self.credits_command
            # Additional commands can be added here
        }

    def default_message(self):
        ascii_header = r"""
______ _____ ___________   _____                   _             _ 
|  _  |  ___|  ___| ___ \ |_   _|                 (_)           | |
| | | | |__ | |__ | |_/ /   | | ___ _ __ _ __ ___  _ _ __   __ _| |
| | | |  __||  __||  __/    | |/ _ | '__| '_ ` _ \| | '_ \ / _` | |
| |/ /| |___| |___| |       | |  __| |  | | | | | | | | | | (_| | |
|___/ \____/\____/\_|       \_/\___|_|  |_| |_| |_|_|_| |_|\__,_|_|
                                        _______________                    
                                        |    \__    _______ _____    _____  
                                        |    | |    |_/ __ \\__  \  /     \ 
                                    /\__|    | |    |\  ___/ / __ \|  Y Y  \
                                    \________| |____| \___  (____  |__|_|  /
                                                          \/     \/      \/                
        """
        Terminal.newpage()
        return ascii_header + f"\n{self.counter.get_counters()}\n" + "Type 'help' for a list of commands, or more info.\n"

    def process_command(self, command):
        if command == "deepterminalstop2024":
            sys.exit(0)
        elif command in self.commands:
            response = self.commands[command]()
        else:
            response = "Unknown command."
        return self.default_message() + '\n' + response + "\n"  # Append a newline

    def run_start(self):
        self.gearDemo_command()
        self.run()

    def run(self):
        # Start the terminal with the default message
        print_tabbed(self.default_message())  
        while True:
            reset_activity_timer()
            command_input = tabbed_input("> ")
            command = command_input.lower()
            output = self.process_command(command)
            print_tabbed(output)
    
    @staticmethod
    def newpage():
        # Clear the console screen
        os.system('cls' if os.name == 'nt' else 'clear')
    
    ##UNUSED##
    def add_external_command(self, command_name, command_function):
        self.commands[command_name] = command_function

    ##COMMANDS##
    def credits_command(self):
        return '''
By: Ethan V., Nadia, E...'''

    def show_help(self):
        return "- help\n- greetings\n- gear demo\n- forwards\n- backwards\n- input\n- read\n- time dilation"
    
    def greet(self):
        return "Hello Universe!"
    
    def gearDemo_command(self):
        # Stop the watchdog timer before starting the gear demo
        stop_watchdog_timer()

        gear_demo_obj = GearDemo(self)
        gear_demo_obj.run()

        # Check if there are any messages in the queue
        if gear_demo_obj.message_queue:
            # Display a general message about the queued messages
            num_messages = len(gear_demo_obj.message_queue)
            Terminal.newpage()
            print_tabbed(f'{num_messages} new message(s) during traversal period.')
            print_tabbed("If there are too many, just hold 'enter' to fast forward through them.")
            print_tabbed("It's highly encouraged to read them though!\n")
            tabbed_input('Press \'enter\' to start reading the messages > ')

            # Display queued messages in the order they were added (oldest first)
            for message in gear_demo_obj.message_queue:
                Terminal.newpage()
                print(message)
                tabbed_input('Press \'enter\' to continue > ')  # Wait for user input before continuing
                
        # Restart the watchdog timer after the gear demo has finished
        start_watchdog_timer()
        
        return "Back to main terminal."

    def forwards(self):
        self.counter.increment()
        Read.check_and_display_messages(self.counter.get_counters_list()) #To check for message
        return "Moved forwards."

    def backwards(self):
        self.counter.decrement()
        Read.check_and_display_messages(self.counter.get_counters_list()) #To check for message
        return "Moved backwards."
    
    def input_command(self):
        input_obj = Input(self)
        message = input_obj.run()
        return message

    def read_command(self):
        read_obj = Read(self)
        message = read_obj.run()
        return message  # Use the returned message as the output for the terminal
    
    def dilation_command(self):
        # Assuming TimeDilation class is imported from dilationclasses.py
        demo = TimeDilation(self.newpage)  # Instantiate TimeDilation with newpage function
        self.newpage()  # Optionally clear the terminal screen before running the demo
        demo.run()  # Directly run the Time Dilation simulation
        while True:
            user_input = tabbed_input("Type 'exit' to return to the main terminal\n> ").strip().lower()
            if user_input == 'exit':
                break
        return "Exiting back to main terminal."
    
    def progression_command(self):
        demo = OneDDemo()
        self.newpage()
        demo.run()
        return "Exiting back to main terminal."


class Counter:
    def __init__(self):
        self.counters = [0] * 6  # Initialize six counters
        self.universes = 0 # Initialize universes counter

    def copy(self):
        # Create a new instance of Counter
        new_counter = Counter()
        # Copy the counters array
        new_counter.counters = self.counters[:]
        return new_counter

    def increment(self):
        self._update_counters(1)

    def decrement(self):
        self._update_counters(-1)
    
    def spec_change(self, value):
        self._update_counters(value)

    def _update_counters(self, delta):
        # Start from the first counter and update
        for i in range(len(self.counters)):
            self.counters[i] += delta
            # Check for roll-over or roll-under
            if delta > 0 and self.counters[i] >= 60:
                self.counters[i] %= 60
                if i == len(self.counters) - 1:
                    self.universes += 1  # Increment universes if the last counter rolls over
                continue
            elif delta < 0 and self.counters[i] == -1:
                self.counters[i] = 59
                if i == len(self.counters) - 1:
                    self.universes -= 1  # Decrement universes if the last counter rolls under
                continue
            break  # Stop updating if no carry-over or borrow
    
    @staticmethod
    def parse_coordinate(coord_str):
        if ' ' in coord_str:
            # Split the string by spaces and validate each part
            parts = coord_str.split()
            if len(parts) != 6 or not all(part.isdigit() and int(part) < 60 for part in parts):
                raise ValueError("Invalid coordinate format. Each number must be less than 60. Expected format: # # # # # #")
            return [int(x) for x in parts]
        else:
            raise ValueError("Invalid input. Expected a coordinate input.")


    def get_counters(self):
        # Returns the counters in a formatted string
        return ' '.join(map(str, self.counters))
    
    def get_counters_list(self):
        return self.counters

    def baseTenConv(self, digits=None):
        """
        Convert the internal counters or an external list of base-60 digits to a base-10 number.
        
        :param digits: (Optional) List of integers representing the base-60 digits.
        :return: Base-10 integer.
        """
        if digits is None:
            digits = self.counters

        return sum(d * (60 ** i) for i, d in enumerate(digits))

    #Returns a string coordinate for display given a #
    def strCoord_conv(self, number):
        number %= (60 ** 6)  # Modulo to get the value within the current universe

        digits = []
        while number > 0:
            digits.append(number % 60)
            number //= 60

        while len(digits) < 6:
            digits.append(0)

        return ' '.join(str(d).zfill(2) for d in digits)
    
    #Returns a list coordinate for calculations given a #
    def coord_conv(self, number):
        number %= (60 ** 6)  # Modulo to get the value within the current universe

        digits = []
        while number > 0:
            digits.append(number % 60)
            number //= 60

        while len(digits) < 6:
            digits.append(0)

        return digits
    
    def univ_count(self, number):
        return number // (60 ** 6)  # Return the number of universes

    def calculate_distance(self, ref_counter):
        # Convert the internal counter to its total base10 equivalent
        curr_cord = self.baseTenConv()

        # Check if ref_counter is a list and convert it using baseTenConv
        if isinstance(ref_counter, list):
            next_coord = self.baseTenConv(ref_counter)
        else:
            # ref_counter is an instance of Counter
            next_coord = ref_counter.baseTenConv()

        # Calculate the distance and convert it to coordinate format
        distance_base_10 = next_coord - curr_cord
        return self.coord_conv(distance_base_10)
    

class GearDemo:
    def __init__(self, terminal):
        self.terminal = terminal
        self.message_queue = [] # Empty list holding messages passed
        self.displayed_message_ids = set()  # Set to keep track of displayed message titles
        self.new_messages_count = 0

        self.inactivity_timeout = 10000  # 1 minute in milliseconds

        # Initialize gear_ratios with a copy to avoid modifying the original counter
        total_gear_value = self.terminal.counter.baseTenConv()
        self.gear_ratios = []
        for i in range(len(self.terminal.counter.counters)):
            # Calculate the gear's share of the total_gear_value
            gear_value = (total_gear_value / (60 ** i)) % 60
            # Convert the gear value to a ratio of a full rotation
            gear_ratio = gear_value / 60
            self.gear_ratios.append(gear_ratio)

        self.rps = 1  # Default RPS value
        self.accumulated_increment = 0

        # Initialize Gear images
        self.gear_images = []
        self.gear_rects = self.load_and_scale_gear_images()
        # Sets the gears to their correct state initially
        self.update_gear_pics()

    def run(self):
        # Store the original file descriptor for standard input
        stdin_fd = sys.stdin.fileno()
        stdin_copy = os.dup(stdin_fd)

        pygame.display.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.font.init()
        self.font = pygame.font.Font('SourceCodePro-Regular.ttf', 12)
        pygame.mouse.set_visible(False)

        # Enable key repeat (delay, interval)
        pygame.key.set_repeat(60)  # Starts repeating after 500ms and then every 100ms


        # Set the timer for inactivity detection
        pygame.time.set_timer(pygame.USEREVENT, self.inactivity_timeout)

        # Start the gear demo loop
        self.start_gear_demo()

        # Cleanup
        pygame.display.quit()
        pygame.quit()

        # Restore the original standard input
        os.dup2(stdin_copy, stdin_fd)
        os.close(stdin_copy)

    def load_and_scale_gear_images(self):
        window_size = (780, 600)
        original_image = pygame.image.load("FinalGear.png")
        scale_factor = 0.16  # Scale factor to adjust gear size
        scaled_image = pygame.transform.scale(original_image, (int(original_image.get_width() * scale_factor), 
                                                            int(original_image.get_height() * scale_factor)))

        gear_rects = []  # List to store the initial rect for each gear
        remaining_space = window_size[0] - (scaled_image.get_width() * 6)
        gap_size = remaining_space // 7  # Distribute the remaining space into 7 parts

        for i in range(6):
            # Calculate the position for each gear to be evenly spaced
            gear_rect = scaled_image.get_rect()
            gear_rect.center = (gap_size * (i + 1) + i * scaled_image.get_width(), window_size[1] // 2)
            gear_rects.append(gear_rect)

        # Store the scaled image and rects
        self.scaled_gear_image = scaled_image
        return gear_rects

    def update_gear_ratios(self, direction):
        # Base increment value for the first gear, as a fraction of a full rotation
        base_increment = direction * self.rps / 60

        for i in range(len(self.gear_ratios)):
            # Update the gear ratio by the base increment, adjusted by the gear's position (1/60th power)
            self.gear_ratios[i] += base_increment / (60 ** i)

            # Ensure the gear ratio wraps around at 1 in a circular manner
            if self.gear_ratios[i] >= 1:
                self.gear_ratios[i] -= int(self.gear_ratios[i])  # Keep the fractional part only
            elif self.gear_ratios[i] < 0:
                self.gear_ratios[i] = 1 - (-self.gear_ratios[i] % 1)  # Wrap around to just below 1

    def update_gear_pics(self):
        # Clear the current gear images list
        self.gear_images.clear()

        # Update each gear's rotation angle based on its ratio
        for i, gear_ratio in enumerate(self.gear_ratios):
            angle_degrees = gear_ratio * 360
            rotated_image = pygame.transform.rotate(self.scaled_gear_image, -angle_degrees)  # Negative for clockwise rotation
            rotated_rect = rotated_image.get_rect(center=self.gear_rects[i].center)  # Re-center the image

            # Store the rotated image and its new rect
            self.gear_images.append(rotated_image)
            self.gear_rects[i] = rotated_rect

    def update_counter_values(self, direction):
        # Accumulate increments in a floating-point variable
        self.accumulated_increment += direction * self.rps

        # Calculate the whole number part of the accumulated increment
        increment = int(self.accumulated_increment)

        if increment != 0:
            # Pass the whole number increment to the terminal counter
            self.terminal.counter.spec_change(increment)

            # Call queue_messages to queue messages based on the updated counter value
            self.queue_messages()

            # Subtract the whole number part from the accumulated increment
            self.accumulated_increment -= increment

    def queue_messages(self):
        coord = self.terminal.counter.get_counters_list()
        messages_with_ids = Read.get_messages_for_coord(coord)  #includes IDs

        for msg_id, formatted_message in messages_with_ids:
            if msg_id not in self.displayed_message_ids:  # Check if the ID is not in the set
                self.message_queue.append(formatted_message)
                self.displayed_message_ids.add(msg_id)  # Add the ID to the set
                self.new_messages_count += 1 #increments counter

    def display_info(self):
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background
        self.blit_ascii_header(self.screen, self.font)

        # Display each gear
        for i, gear_image in enumerate(self.gear_images):
            # Get the current top-left coordinates
            current_topleft_x, current_topleft_y = self.gear_rects[i].topleft
            # Adjust the y-coordinate by adding or subtracting the desired amount
            new_topleft_y = current_topleft_y + 45
            # Adjust the y-coordinate by adding or subtracting the desired amount
            new_topleft_x = current_topleft_x + 70
            # Blit the gear image at the new position
            self.screen.blit(gear_image, (new_topleft_x, new_topleft_y))

        # Display gear ratios
        gear_ratios_str = ' '.join([f"{gear:.10f}" for gear in self.gear_ratios])
        ratios_surface = self.font.render(f"    Gear Ratios: {gear_ratios_str}", True, (255, 255, 255))
        self.screen.blit(ratios_surface, (10, 440))  # Adjust position as needed

        # Display counters
        counters_str = self.terminal.counter.get_counters()
        counters_surface = self.font.render(f"    Counters: {counters_str}", True, (255, 255, 255))
        self.screen.blit(counters_surface, (10, 470))  # Adjust position as needed

        # Display new messages count if any
        if self.new_messages_count > 0:
            messages_surface = self.font.render(f"    {self.new_messages_count} new message(s) available to read.", True, (255, 255, 255))
            self.screen.blit(messages_surface, (10, 500))  # Adjust position as needed

        # Quit message
        quit_surface = self.font.render("                       Press 'q' to go to the main terminal. (More stuff to check out!)", True, (255, 255, 255))
        self.screen.blit(quit_surface, (10, 550))

        pygame.display.flip()  # Update the screen

    def blit_ascii_header(self, screen, font):
        ascii_lines = [
"                ______ _____ ___________   _____                   _             _ ",
"                |  _  |  ___|  ___| ___ \ |_   _|                 (_)           | |",
"                | | | | |__ | |__ | |_/ /   | | ___ _ __ _ __ ___  _ _ __   __ _| |",
"                | | | |  __||  __||  __/    | |/ _ | '__| '_ ` _ \| | '_ \ / _` | |",
"                | |/ /| |___| |___| |       | |  __| |  | | | | | | | | | | (_| | |",
"                |___/ \____/\____/\_|       \_/\___|_|  |_| |_| |_|_|_| |_|\__,_|_|",
"                                                        _______________                    ",
"                                                        |    \__    _______ _____    _____  ",
"                                                        |    | |    |_/ __ \\\__  \  /     \ ",
"                                                    /\__|    | |    |\  ___/ / __ \|  Y Y  \\",
"                                                    \________| |____| \___  (____  |__|_|  /",
"                                                                          \/     \/      \/        ",
"",
"           Welcome To The Gear Ratio Demonstration! Hold the 'up' or 'down' arrow keys to change",
"           the gear values. For reference, it takes about 46 billion 'cranks' to make the last",
"           gear value hit '1'. That's the size of the Observable Universe's radius in lightyears!"
        ]

        y_offset = 0  # Starting position
        for line in ascii_lines:
            text_surface = font.render(line, True, (255, 255, 255))  # White color
            screen.blit(text_surface, (10, y_offset))
            y_offset += font.get_linesize()  # Move to the next line

    def handle_key_press(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT:
                    self.show_sleep_screen()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False  # Stop the demo
                    else:
                        self.process_key(event.key)
                        pygame.time.set_timer(pygame.USEREVENT, self.inactivity_timeout)  # Reset the timer on any key press

            self.display_info()  # Continuously update the display

    def process_key(self, key):
        if (key == pygame.K_RIGHT) or (key == pygame.K_UP):
            self.update_gear_ratios(1)
            self.update_gear_pics()
            self.update_counter_values(1)
        elif (key == pygame.K_LEFT) or (key == pygame.K_DOWN):
            self.update_gear_ratios(-1)
            self.update_gear_pics()
            self.update_counter_values(-1)

    def show_sleep_screen(self):
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background

        # Font settings
        font = self.font  # Assuming self.font is already initialized as a Pygame font object

        # Gets counter in string format
        counter = ' '.join(map(str, self.terminal.counter.get_counters_list()))

        # Render "Deep Terminal" in the top left
        deep_terminal_surface = font.render("Deep Terminal", True, (255, 255, 255))
        self.screen.blit(deep_terminal_surface, (0, 5))  # Adjust margins as needed

        # Render "JTeam" in the top right
        jteam_surface = font.render("JTeam", True, (255, 255, 255))
        jteam_x = self.screen.get_width() - jteam_surface.get_width() - 20  # 20 pixels from the right edge
        self.screen.blit(jteam_surface, (jteam_x, 5))

        # Render counter in the center
        zzz_surface = font.render(counter, True, (255, 255, 255))
        zzz_x = (self.screen.get_width() // 2) - (zzz_surface.get_width() // 2) - 10 # 30 adjustment
        zzz_y = (self.screen.get_height() // 2) - (zzz_surface.get_height() // 2)
        self.screen.blit(zzz_surface, (zzz_x, zzz_y))

        # Render "Press any key to wake" at the bottom
        wake_surface = font.render("Press any key to wake", True, (255, 255, 255))
        wake_x = (self.screen.get_width() // 2) - (wake_surface.get_width() // 2) - 15 # 30 adjustment
        wake_y = self.screen.get_height() - wake_surface.get_height() - 10  # 10 pixels from the bottom
        self.screen.blit(wake_surface, (wake_x, wake_y))

        pygame.display.flip()  # Update the display with the new sleep screen layout

        # Wait for any key to wake up
        event = pygame.event.wait()
        while event.type not in [pygame.KEYDOWN, pygame.QUIT]:  # Wait for a key press or quit event
            event = pygame.event.wait()
        pygame.time.set_timer(pygame.USEREVENT, self.inactivity_timeout)  # Reset the timer after waking up

    def start_gear_demo(self):
        self.handle_key_press()  # Directly call the method containing the game loop
        pygame.time.set_timer(pygame.USEREVENT, 0)


class Input:
    def __init__(self, terminal):
        self.terminal = terminal
        self.setup_database()  # Ensure the database is set up

    @staticmethod
    def setup_database():
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            title TEXT DEFAULT NULL,
            input_coord TEXT NOT NULL,
            display_coord TEXT,
            message TEXT NOT NULL,
            on_list BOOLEAN DEFAULT 0
        )''')
        conn.commit()
        conn.close()

    def write_to_database(self, title, input_coord, display_coord, text, on_list):
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (title, input_coord, display_coord, message, on_list)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, ' '.join(map(str, input_coord)), 
             ' '.join(map(str, display_coord)) if display_coord else None, 
             text, on_list))
        conn.commit()
        conn.close()

    def input_message(self):
        # Intermediate explanation page
        print_tabbed("This is the input command! Use it to input a text message into the system.")
        print_tabbed("It works as follows:\n")

        print_tabbed("You input a message pressing \'enter' for a new line")
        print_tabbed("and type 'END' (all caps) on the last line to finish the message\n")

        print_tabbed("You then are able to choose a title,")
        print_tabbed("select a coordinate for it to be viewable at (if desired),")
        print_tabbed("and choosing whether or not it's viewable on the list of readable messages!\n")

        tabbed_input("Press \'enter\' to continue to message creation> ")

        print_tabbed("\nEnter the text to log (type 'END' on a new line to finish, 'EXIT' to cancel):")
        lines = []
        while True:
            reset_activity_timer()
            line = input()
            if line == "END":
                break
            elif line == "EXIT":
                return "Text input cancelled."

            lines.append(line)
        text = "\n".join(lines)

        reserved_commands = ["exit", "help", "next", "back"]  # Add more reserved words as needed
        reset_activity_timer()
        while True:
            title = tabbed_input("Enter a title (default is current coordinate, type 'cancel' to abort): ").strip()
            # Use the current coordinate as the default title if no title is entered
            if not title:
                title = ' '.join(map(str, self.terminal.counter.get_counters_list()))
                break  # Exit the loop if a default title is used

            # Check if the title length exceeds 25 characters
            if len(title) > 25:
                print_tabbed("Title too long! Please limit the title to 25 characters.")
                continue  # Prompt the user to enter a new title

            # Check if the entered title is a reserved command
            if title.lower() in reserved_commands:
                print_tabbed("The entered title is a reserved command. Please enter a different title.")
            elif title.lower() == 'cancel':
                # Handle the case where the user wants to cancel the input
                return "Input cancelled."
            else:
                break  # Exit the loop if a valid title is entered

        display_coord = None  # Initialize display_coord
        reset_activity_timer()
        while tabbed_input("Display text at a specific coordinate? (Y/N): ").lower() == 'y':
            coord_input = tabbed_input("Enter coordinate (# # # # # #): ")
            try:
                # Attempt to parse the entered coordinate
                display_coord = Counter.parse_coordinate(coord_input)
                break  # Exit the loop if the coordinate is successfully parsed
            except ValueError as e:
                # Inform the user of the error and prompt to try again
                print_tabbed(f"Error: {e}. Please try again or skip the coordinate input.")

        on_list = tabbed_input("Display title on list of viewable texts (Y/N): ").lower() == 'y'

        print_tabbed("\nReview your text:")
        print_tabbed(text)
        confirm = tabbed_input("Confirm text?(There are no takebacks)... Type CONFIRM (no to cancel): ").lower()
        if confirm != "confirm":
            return "Text input cancelled."

        self.write_to_database(title, self.terminal.counter.get_counters_list(), display_coord, text, on_list)
        return "Text logged."

    def run(self):
        Terminal.newpage()
        reset_activity_timer()
        message = self.input_message()
        return message + "\nBack to main terminal."


class Read:
    def __init__(self, terminal):
        self.terminal = terminal

    def helpFunc(self):
        Terminal.newpage()
        print_tabbed("""
\nWelcome to the message storing! Contained here are pages of messages left by
any who utilize the input command. Use the navigation tools to find a message, 
who knows, maybe you'll find something interesting!

The point is to simply find messages left by others on this terminal. If you'd like,
you can leave a message too, just navigate to the terminal and input the 'input' command.\n""")
        
        tabbed_input("Press 'enter' to continue.")
        return

    def read_command(self):
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        try:
            # Fetch the total count of messages to determine pagination
            cur.execute("SELECT COUNT(id) FROM messages WHERE on_list = 1")
            total_messages = cur.fetchone()[0]

            if not total_messages:
                return Terminal.newpage() + "No viewable messages."

            page_size = 10  # Define how many messages to display per page
            total_pages = (total_messages + page_size - 1) // page_size  # Calculate total number of pages

            # Start at the last page, which contains the most recent messages
            page = total_pages

            while True:
                reset_activity_timer()
                Terminal.newpage()  # Clear the screen
                print_tabbed(self.terminal.default_message())  # Display the terminal's header
                print_tabbed("List of available messages:\n")

                # Calculate the starting index for the current page
                start_index = total_messages - (page * page_size)

                # Fetch page-sized chunk of messages starting from start_index
                cur.execute("SELECT id, title FROM messages WHERE on_list = 1 ORDER BY id DESC LIMIT ? OFFSET ?", (page_size, max(0, start_index)))
                page_titles = cur.fetchall()

                # Display the messages in a 5x2 layout
                for i in range(0, len(page_titles), 2):
                    row_titles = [f"{title:<30}" for _, title in page_titles[i:i + 2]]
                    print_tabbed(' '.join(row_titles))

                print()
                print_tabbed(f"Page {page} of {total_pages}")  # Display the current page and total pages
                print()
                
                # User prompt for navigation
                navigation = '''
                    Enter: 'next' for older messages, 'back' for newer messages, 
                    'page #' to navigate to a specific page, a title to read, 
                    or 'exit' to go back to the main terminal: '''
                command = tabbed_input(navigation).lower()

                # Command handling
                if command == "exit":
                    break
                elif command.startswith("page ") and command.split()[1].isdigit():
                    requested_page = int(command.split()[1])
                    if 1 <= requested_page <= total_pages:
                        page = requested_page  # Jump to the requested page
                    else:
                        print_tabbed("Invalid page number.")
                elif command == "next" and page > 1:
                    page -= 1  # Move to an older set of messages
                elif command == "back" and page < total_pages:
                    page += 1  # Move to a newer set of messages
                else:
                    cur.execute("SELECT input_coord, title, message FROM messages WHERE LOWER(title) = LOWER(?) ORDER BY id DESC", (command,))
                    messages_data = cur.fetchall()

                    if messages_data:
                        for coord, title, text in messages_data:
                            reset_activity_timer(360)
                            Terminal.newpage()
                            print(f"Written at {coord}\n\n{title} :\n\n{text}\n")
                            print()
                            tabbed_input("Press \'enter\' to continue > ")
                    else:
                        Terminal.newpage()
                        print_tabbed("No message found with that title.")
                        tabbed_input("Press \'enter\' to continue > ")

        finally:
            conn.close()

        return "Finished reading messages. "

    @staticmethod
    def check_and_display_messages(coord):
        messages_with_ids = Read.get_messages_for_coord(coord)  # This now includes IDs
        for _, formatted_message in messages_with_ids:  # Unpack the tuple, ignoring the ID
            Terminal.newpage()
            print_tabbed(formatted_message)
            tabbed_input('Press \'enter\' to continue > ')

    @staticmethod
    def get_messages_for_coord(display_coord):
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        # Include ID in the SELECT statement
        cur.execute("SELECT id, input_coord, title, message FROM messages WHERE display_coord = ?", (' '.join(map(str, display_coord)),))
        results = cur.fetchall()
        conn.close()

        messages = []
        for msg_id, input_coord, title, text in results:
            formatted_message = (f"Written at {input_coord}\n\n{title} :\n\n{text}\n\nAuto display at {' '.join(map(str, display_coord))}\n")
            messages.append((msg_id, formatted_message))  # Include the ID with each message
        return messages

    def run(self):
        reset_activity_timer()
        self.helpFunc()
        print_tabbed(self.terminal.default_message())
        response = self.read_command()
        return response + "Back to main terminal." # Return the response for the terminal to handle
    