import sqlite3
import curses
import time
import pygame

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
            "read": self.read_command
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
        return "\\newpage\n" + ascii_header + f"\n{self.counter.get_counters()}\n" + "Type 'help' for a list of commands, or more info.\n"

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
            print('\\newpage')
            print(f'{num_messages} new message(s) during traversal period.')
            print("If there are too many, just hold 'enter' to fast forward through them.")
            print("It's highly encouraged to read them though!\n")
            input('Press enter to start reading the messages > ')

            # Display queued messages in the order they were added (oldest first)
            for message in gear_demo_obj.message_queue:
                print('\\newpage\n' + message)
                input('Input any key to continue > ')  # Wait for user input before continuing

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

    def run(self):
        self.set_rps()  # Set the RPS value via CLI
        pygame.display.init()
        self.screen = pygame.display.set_mode((900, 600))  # Adjust size as needed
        pygame.font.init() #Initialize font
        self.font = pygame.font.Font('SourceCodePro-Regular.ttf', 15)
        self.start_gear_demo()
        pygame.quit()  # Quit Pygame when done

    
    def set_rps(self):
        try:
            rps_input = float(input("Enter RPS (greater than 0 and up to 1): "))
            if 0 < rps_input <= 1:
                self.rps = rps_input
                print(f"RPS set to {self.rps}")
            else:
                print("Invalid RPS value. Please enter a number greater than 0 and up to 1.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

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

        #self.terminal.counter.spec_change(self.accumulated_increment)

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

        # Display gear ratios
        gear_ratios_str = ' '.join([f"{gear:.10f}" for gear in self.gear_ratios])
        ratios_surface = self.font.render(f"Gear Ratios: {gear_ratios_str}", True, (255, 255, 255))
        self.screen.blit(ratios_surface, (10, 10))  # Adjust position as needed

        # Display counters
        counters_str = self.terminal.counter.get_counters()
        counters_surface = self.font.render(f"Counters: {counters_str}", True, (255, 255, 255))
        self.screen.blit(counters_surface, (10, 40))  # Adjust position as needed

        # Display new messages count if any
        if self.new_messages_count > 0:
            messages_surface = self.font.render(f"{self.new_messages_count} new message(s) available to read.", True, (255, 255, 255))
            self.screen.blit(messages_surface, (10, 70))  # Adjust position as needed

        pygame.display.flip()  # Update the screen

    def handle_key_press(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()  # Get the state of all keyboard buttons
            if keys[pygame.K_UP]:
                self.update_gear_ratios(1)
                self.update_counter_values(1)
            if keys[pygame.K_DOWN]:
                self.update_gear_ratios(-1)
                self.update_counter_values(-1)
            if keys[pygame.K_q]:  # Quit
                break

            self.display_info()  # Update the display based on the current state
            pygame.time.wait(10)  # Small delay to reduce CPU usage

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

        print("You input a message pressing enter for a new line")
        print("and type 'END' (all caps) on the last line to finish the message\n")

        print("You then are able to choose a title,")
        print("select a coordinate for it to be viewable at (if desired),")
        print("and choosing whether or not it's viewable on the list of readable messages!\n")

        input("Press enter to continue to message creation> ")

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

        reserved_commands = ["exit", "help", "back"]  # Add more reserved words as needed
        while True:
            title = input("Enter a title (default is current coordinate, type 'CANCEL' to abort): ").strip()
            # Use the current coordinate as the default title if no title is entered
            if not title:
                title = ' '.join(map(str, self.terminal.counter.get_counters_list()))
                break  # Exit the loop if a default title is used

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
        print("\\newpage")
        message = self.input_message()
        return message + "\nBack to main terminal."


class Read:
    def __init__(self, terminal):
        self.terminal = terminal

    def read_command(self):
        message = ""  # Initialize the message to be returned
        conn = sqlite3.connect('deep_messages.db')
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, title FROM messages WHERE on_list = 1")
            messages = cur.fetchall()

            if not messages:
                message += "No viewable messages."
                return message

            print("List of available messages:\n")
            for msg_id, title in messages:
                print(f"{title}")

            selected_title = input("\nEnter the title of the message to read: ")
            if (selected_title == "exit"):
                return "Exiting."
            cur.execute("SELECT input_coord, title, message FROM messages WHERE title = ?", (selected_title,))
            message_data = cur.fetchone()

            if message_data:
                coord, title, text = message_data
                print('\\newpage')
                print(f"Written at {coord}\n\n{title} :\n\n{text}\n")
                input("\nPress any key to continue > ")  # Wait for user input before continuing
                return ""
            else:
                message += "No message found with that title.\n"
        finally:
            conn.close()
        
        return message


    @staticmethod
    def check_and_display_messages(coord):
        messages_with_ids = Read.get_messages_for_coord(coord)  # This now includes IDs
        for _, formatted_message in messages_with_ids:  # Unpack the tuple, ignoring the ID
            print('\\newpage\n' + formatted_message)
            input('Input any key to continue > ')

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
