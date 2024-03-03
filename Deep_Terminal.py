import sqlite3
import sys
import os
import pygame

from DilationClasses import *

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
            "dilation": self.dilation_command
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
        if command in self.commands:
            response = self.commands[command]()
        else:
            response = "Unknown command."
        return self.default_message() + '\n' + response + "\n"  # Append a newline

    def run(self):
        # Start the terminal with the default message
        print(self.default_message())  
        while True:
            command_input = input("> ")
            command = command_input.lower()
            output = self.process_command(command)
            print(output)
    
    @staticmethod
    def newpage():
        # Clear the console screen
        os.system('cls' if os.name == 'nt' else 'clear')
    
    ##UNUSED##
    def add_external_command(self, command_name, command_function):
        self.commands[command_name] = command_function

    ##COMMANDS##
    def show_help(self):
        return "- help\n- greetings\n- gear demo\n- forwards\n- backwards\n- input\n- read"
    
    def greet(self):
        return "Hello Universe!"
    
    def gearDemo_command(self):
        gear_demo_obj = GearDemo(self)
        gear_demo_obj.run()

        # Check if there are any messages in the queue
        if gear_demo_obj.message_queue:
            # Display a general message about the queued messages
            num_messages = len(gear_demo_obj.message_queue)
            Terminal.newpage()
            print(f'{num_messages} new message(s) during traversal period.')
            print("If there are too many, just hold 'enter' to fast forward through them.")
            print("It's highly encouraged to read them though!\n")
            input('Press \'enter\' to start reading the messages > ')

            # Display queued messages in the order they were added (oldest first)
            for message in gear_demo_obj.message_queue:
                Terminal.newpage()
                print(message)
                input('Press \'enter\' to continue > ')  # Wait for user input before continuing

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
        dil_obj = Dilation(self)
        output = dil_obj.run()
        return output


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
        self.gear_images, self.gear_rects = self.load_and_scale_gear_images()
        # Sets the gears to their correct state initially
        self.update_gear_pics()

    def run(self):
        # Store the original file descriptor for standard input
        stdin_fd = sys.stdin.fileno()
        stdin_copy = os.dup(stdin_fd)

        self.set_rps()  # Set the RPS value via CLI
        pygame.display.init()
        self.screen = pygame.display.set_mode((900, 600))  # Adjust size as needed
        pygame.font.init()  # Initialize font
        self.font = pygame.font.Font('SourceCodePro-Regular.ttf', 12)
        
        # Start the gear demo loop
        self.start_gear_demo()
        
        # Quit Pygame display
        pygame.display.quit()
        pygame.quit()

        # Restore the original standard input
        os.dup2(stdin_copy, stdin_fd)
        os.close(stdin_copy)

    
    def set_rps(self):
        try:
            rps_input = float(input("A speed 1-10 (10 being the fastest 1 the slowest): "))
            if 0 < rps_input <= 10:
                self.rps = 1.5 * (rps_input/10)
            else:
                print("Invalid RPS value. Please enter a number greater than 0 and up to 10.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def load_and_scale_gear_images(self):
        gear_images = []
        gear_rects = []
        window_size = (900, 600)
        original_image = pygame.image.load("FinalGear.png")
        scale_factor = .18  # Scale factor to adjust gear size
        scaled_image = pygame.transform.scale(original_image, (int(original_image.get_width() * scale_factor), 
                                                            int(original_image.get_height() * scale_factor)))

        # Calculate the total width of all gears combined
        total_gears_width = sum([scaled_image.get_width() for _ in range(6)])
        # Calculate the remaining space after placing all gears
        remaining_space = window_size[0] - total_gears_width
        # Distribute the remaining space into 7 parts (6 gaps + 1 extra for margins)
        gap_size = remaining_space // 7

        for i in range(6):
            gear_images.append(scaled_image)
            gear_rect = scaled_image.get_rect()
            # Position the center of each gear based on its index
            # New position logic to bring gears closer together
            gear_rect.center = (gap_size + i * (scaled_image.get_width() + gap_size), window_size[1] // 2)
            gear_rects.append(gear_rect)
        
        return gear_images, gear_rects


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
        # Store the original scaled images to rotate them from scratch each frame
        if not hasattr(self, 'original_gear_images'):
            self.original_gear_images = self.gear_images.copy()

        # Update each gear's rotation angle based on its ratio
        for i, gear_ratio in enumerate(self.gear_ratios):
            angle = -(gear_ratio * 360)
            # Always rotate from the original scaled image
            self.gear_images[i] = pygame.transform.rotate(self.original_gear_images[i], angle)
            # Recalculate the gear_rect to account for the change in image dimensions after rotation
            self.gear_rects[i] = self.gear_images[i].get_rect(center=self.gear_rects[i].center)

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
        self.screen.blit(ratios_surface, (10, 430))  # Adjust position as needed

        # Display counters
        counters_str = self.terminal.counter.get_counters()
        counters_surface = self.font.render(f"    Counters: {counters_str}", True, (255, 255, 255))
        self.screen.blit(counters_surface, (10, 470))  # Adjust position as needed

        # Display new messages count if any
        if self.new_messages_count > 0:
            messages_surface = self.font.render(f"    {self.new_messages_count} new message(s) available to read.", True, (255, 255, 255))
            self.screen.blit(messages_surface, (10, 500))  # Adjust position as needed

        # Quit message
        quit_surface = self.font.render("                               Press 'q' to go to the main terminal. (More stuff to check out!)", True, (255, 255, 255))
        self.screen.blit(quit_surface, (10, 550))

        pygame.display.flip()  # Update the screen

    def blit_ascii_header(self, screen, font):
        ascii_lines = [
"                        ______ _____ ___________   _____                   _             _ ",
"                        |  _  |  ___|  ___| ___ \ |_   _|                 (_)           | |",
"                        | | | | |__ | |__ | |_/ /   | | ___ _ __ _ __ ___  _ _ __   __ _| |",
"                        | | | |  __||  __||  __/    | |/ _ | '__| '_ ` _ \| | '_ \ / _` | |",
"                        | |/ /| |___| |___| |       | |  __| |  | | | | | | | | | | (_| | |",
"                        |___/ \____/\____/\_|       \_/\___|_|  |_| |_| |_|_|_| |_|\__,_|_|",
"                                                                _______________                    ",
"                                                                |    \__    _______ _____    _____  ",
"                                                                |    | |    |_/ __ \\\__  \  /     \ ",
"                                                            /\__|    | |    |\  ___/ / __ \|  Y Y  \\",
"                                                            \________| |____| \___  (____  |__|_|  /",
"                                                                                  \/     \/      \/        ",
"",
"                   Welcome To The Gear Ratio Demonstration! Hold the 'up' or 'down' arrow keys to change",
"                   the gear values. For reference, it takes about 46 billion 'cranks' to make the last",
"                   gear value hit '1'. That's the size of the Observable Universe's radius in lightyears!"
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

            keys = pygame.key.get_pressed()  # Get the state of all keyboard buttons
            if keys[pygame.K_UP]:
                self.update_gear_ratios(1)
                self.update_gear_pics()
                self.update_counter_values(1)
            if keys[pygame.K_DOWN]:
                self.update_gear_ratios(-1)
                self.update_gear_pics()
                self.update_counter_values(-1)
            if keys[pygame.K_q]:  # Quit
                break

            self.display_info()  # Update the display based on the current state
            pygame.time.wait(30)  # Small delay to reduce CPU usage

    def start_gear_demo(self):
        self.handle_key_press()  # Directly call the method containing the game loop


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
        print("This is the input command! Use it to input a text message into the system.")
        print("It works as follows:\n")

        print("You input a message pressing \'enter'\ for a new line")
        print("and type 'END' (all caps) on the last line to finish the message\n")

        print("You then are able to choose a title,")
        print("select a coordinate for it to be viewable at (if desired),")
        print("and choosing whether or not it's viewable on the list of readable messages!\n")

        input("Press \'enter\' to continue to message creation> ")

        print("\nEnter the text to log (type 'END' on a new line to finish, 'EXIT' to cancel):")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            elif line == "EXIT":
                return "Text input cancelled."

            lines.append(line)
        text = "\n".join(lines)

        reserved_commands = ["exit", "help", "next", "back"]  # Add more reserved words as needed
        while True:
            title = input("Enter a title (default is current coordinate, type 'cancel' to abort): ").strip()
            # Use the current coordinate as the default title if no title is entered
            if not title:
                title = ' '.join(map(str, self.terminal.counter.get_counters_list()))
                break  # Exit the loop if a default title is used

            # Check if the title length exceeds 25 characters
            if len(title) > 25:
                print("Title too long! Please limit the title to 25 characters.")
                continue  # Prompt the user to enter a new title

            # Check if the entered title is a reserved command
            if title.lower() in reserved_commands:
                print("The entered title is a reserved command. Please enter a different title.")
            elif title.lower() == 'cancel':
                # Handle the case where the user wants to cancel the input
                return "Input cancelled."
            else:
                break  # Exit the loop if a valid title is entered

        display_coord = None  # Initialize display_coord
        while input("Display text at a specific coordinate? (Y/N): ").lower() == 'y':
            coord_input = input("Enter coordinate (# # # # # #): ")
            try:
                # Attempt to parse the entered coordinate
                display_coord = Counter.parse_coordinate(coord_input)
                break  # Exit the loop if the coordinate is successfully parsed
            except ValueError as e:
                # Inform the user of the error and prompt to try again
                print(f"Error: {e}. Please try again or skip the coordinate input.")

        on_list = input("Display title on list of viewable texts (Y/N): ").lower() == 'y'

        print("\nReview your text:")
        print(text)
        confirm = input("Confirm text?(There are no takebacks)... Type CONFIRM (no to cancel): ").lower()
        if confirm != "confirm":
            return "Text input cancelled."

        self.write_to_database(title, self.terminal.counter.get_counters_list(), display_coord, text, on_list)
        return "Text logged."

    def run(self):
        Terminal.newpage()
        message = self.input_message()
        return message + "\nBack to main terminal."


class Read:
    def __init__(self, terminal):
        self.terminal = terminal

    def read_command(self):
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, title FROM messages WHERE on_list = 1 ORDER BY id DESC")
            all_titles = cur.fetchall()

            if not all_titles:
                return Terminal.newpage() + "No viewable messages."

            page = 0
            page_size = 10  # Total titles per page, 5 rows with 2 titles each for 5x2 layout
            titles_per_row = 2  # Titles per row
            title_width = 30  # Width allocated for each title

            while True:
                Terminal.newpage()  # Clear the screen
                print(self.terminal.default_message())  # Display the terminal's header
                print("List of available messages:\n")

                start_index = page * page_size
                end_index = start_index + page_size
                page_titles = all_titles[start_index:end_index]

                for i in range(0, len(page_titles), titles_per_row):
                    # Format and print titles with fixed width to ensure alignment
                    row_titles = [f"{title:<{title_width}}" for _, title in page_titles[i:i + titles_per_row]]
                    print(' '.join(row_titles))

                print("\nPage " + str(page))
                navigation = "Enter 'next' for more, 'back' for previous, a title to read, or 'exit' to go back: "
                command = input(navigation).lower()

                if command == "exit":
                    break
                elif command == "next" and len(all_titles) > end_index:
                    page += 1
                elif command == "back" and page > 0:
                    page -= 1
                else:
                    cur.execute("SELECT input_coord, title, message FROM messages WHERE LOWER(title) = LOWER(?) ORDER BY id DESC", (command,))
                    messages_data = cur.fetchall()

                    if messages_data:
                        for coord, title, text in messages_data:
                            Terminal.newpage()
                            print(f"Written at {coord}\n\n{title} :\n\n{text}\n")
                            input("\nPress \'enter\' to continue > ")
                    else:
                        Terminal.newpage()
                        print("No message found with that title.")
                        input("Press \'enter\' to continue > ")

        finally:
            conn.close()

        return "Finished reading messages. "


    @staticmethod
    def check_and_display_messages(coord):
        messages_with_ids = Read.get_messages_for_coord(coord)  # This now includes IDs
        for _, formatted_message in messages_with_ids:  # Unpack the tuple, ignoring the ID
            Terminal.newpage()
            print(formatted_message)
            input('Press \'enter\' to continue > ')

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
        print(self.terminal.default_message())
        response = self.read_command()
        return response + "Back to main terminal." # Return the response for the terminal to handle


class Dilation:
    def __init__(self, terminal):
        self.terminal = terminal
        self.commands = {
            "help": self.show_help,
            "inevitable progression": self.inevitable_progression,
            "spacetime dilation": self.spacetime_dilation,
        }

    def show_help(self):
        msg = "List of dilation demos:\n"
        return msg + "- help\n- inevitable progression\n- spacetime dilation"

    def inevitable_progression(self):
        options = {
            "1d demo": OneDDemo,
            "2d demo": TwoDDemo,
            "3d demo": ThreeDDemo,
            "graph view": GraphView,
        }
        return self.show_options(options, "Inevitable Progression Options")

    def spacetime_dilation(self):
        options = {
            "complex observer": TimeDilation,
            "unknown": UnknownFunctionality,
        }
        return self.show_options(options, "Spacetime Dilation Options")

    def show_options(self, options, title):
        print(f"{title}:")
        for key in options.keys():
            print(f"- {key}")
        
        print()
        while True:
            selected_option = input("Select an option by typing its name (or type 'exit' to return to the main terminal): ").lower()
            
            if selected_option == "exit":
                return "exit_to_main"  # Use a specific flag to indicate exiting to the main terminal

            elif selected_option in options:
                selected_class = options[selected_option]()
                Terminal.newpage()
                result = selected_class.run()
                if result == "exit_to_main":  # Check if the sub-command also requests to exit to the main terminal
                    return "exit_to_main"
                break
            else:
                print("Invalid option selected. Please try again or type 'exit' to return to the main terminal.")

    def process_command(self, command):
        command = command.lower()
        if command in self.commands:
            response = self.commands[command]()
            if response == "exit_to_main":  # Check for the exit flag
                return "exit_to_main"
            elif response is None:
                response = ""
        else:
            response = "Unknown command.\n"
        return response

    def run(self):
        print()
        print(self.show_help())
        while True:
            print()
            command_input = input("Dilation> ")
            command = command_input.lower()

            if command == "exit":
                return "Exiting back to main terminal."
            else:
                output = self.process_command(command)
                if output == "exit_to_main":  # Handle the exit flag to break out of the loop
                    return "Exiting back to main terminal."
                print(output)
