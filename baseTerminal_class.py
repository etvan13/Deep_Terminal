import os

class Terminal:
    def __init__(self):
        self.counter = Counter()  # Initialize the counter object
        self.commands = {
            "help": self.show_help,
            "greetings": self.greet,
            "forwards": self.forwards,
            "backwards": self.backwards,
            # Additional commands can be added here
        }

    # Clears current screen
    @staticmethod
    def newpage():
        # Clear the console screen
        os.system('cls' if os.name == 'nt' else 'clear')

    # Header message of terminal
    def default_message(self):
        self.newpage()
        return f"{self.counter.get_counters()}\n" + "Type 'help' for a list of commands.\n"
    
    # Checks the inputted command for validity returning its output
    def process_command(self, command):
        if command in self.commands:
            response = self.commands[command]()
        else:
            response = "Unknown command."
        return self.default_message() + "\n" + response + "\n"  # Append a newline

    # Runs the current Terminal
    def run(self):
        # Start the terminal with the default message
        print(self.default_message())  
        while True:
            command_input = input("> ")
            command = command_input.lower()
            output = self.process_command(command)
            print(output)
            if command == "exit":
                break
    
    # Filler for adding external commands
    def add_external_command(self, command_name, command_function):
        self.commands[command_name] = command_function

    ####COMMANDS####
    
    # Prints a list of available commands
    def show_help(self):
        return "- help\n- greetings\n- forwards\n- backwards"
    
    # Returns a greeting
    def greet(self):
        return "Hello Universe!"

    # Moves the counter object forwards 1
    def forwards(self):
        self.counter.increment()
        return "Moved forwards."

    # Moves the counter object backwards 1
    def backwards(self):
        self.counter.decrement()
        return "Moved backwards."

    ##################
    

class Counter:
    # Initialize object
    def __init__(self):
        self.counters = [0] * 6  # Initialize six counters
        self.universes = 0 # Initialize universes counter

    # Copy constructor
    def copy(self):
        # Create a new instance of Counter
        new_counter = Counter()
        # Copy the counters array
        new_counter.counters = self.counters[:]
        return new_counter

    # Increase counter by 1
    def increment(self):
        self._update_counters(1)

    # Decrease counter by 1
    def decrement(self):
        self._update_counters(-1)
    
    # Special increment based on value
    def spec_change(self, value):
        self._update_counters(value)

    # Takes inputted number and alters counters by that value
    def _update_counters(self, delta):
        # Start from the first counter and update
        for i in range(len(self.counters)):
            self.counters[i] += delta
            # Check for roll-over or roll-under
            if delta > 0 and self.counters[i] == 60:
                self.counters[i] = 0
                if i == len(self.counters) - 1:
                    self.universes += 1  # Increment universes if the last counter rolls over
                continue
            elif delta < 0 and self.counters[i] == -1:
                self.counters[i] = 59
                if i == len(self.counters) - 1:
                    self.universes -= 1  # Decrement universes if the last counter rolls under
                continue
            break  # Stop updating if no carry-over or borrow
    
    # Splits the counter string into a list of counters
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

    # Joins the counter list into a string format # # # # # #
    def get_counters(self):
        # Returns the counters in a formatted string
        return ' '.join(str(c) for c in self.counters)
    
    def get_counters_list(self):
        return self.counters

    # Converts list of counters (Each a subsequent power of 60) into a single base 10 number
    def baseTenConv(self, digits=None):
        """
        Convert the internal counters or an external list of base-60 digits to a base-10 number.
        
        :param digits: (Optional) List of integers representing the base-60 digits.
        :return: Base-10 integer.
        """
        if digits is None:
            digits = self.counters

        return sum(d * (60 ** i) for i, d in enumerate(digits))

    # Returns a string counter given a base 10 number
    def strCoord_conv(self, number):
        number %= (60 ** 6)  # Modulo to get the value within the current universe

        digits = []
        while number > 0:
            digits.append(number % 60)
            number //= 60

        while len(digits) < 6:
            digits.append(0)

        return ' '.join(str(d) for d in digits)
    
    # Returns a list coordinate for calculations given a number
    def coord_conv(self, number):
        number %= (60 ** 6)  # Modulo to get the value within the current universe

        digits = []
        while number > 0:
            digits.append(number % 60)
            number //= 60

        while len(digits) < 6:
            digits.append(0)

        return digits
    
    # Returns universe count (Amount of times overflow happens)
    def univ_count(self):
        return self.universes  # Return the number of universes

    # Takes a separate counter and returns the distance between the two in counter form
    def calculate_distance(self, ref_counter):
        # Convert the internal counter to its total base10 equivalent
        curr_cord = self.baseTenConv()

        # Check if ref_counter is a list and convert it using baseTenConv
        if isinstance(ref_counter, list):
            next_coord = self.baseTenConv(ref_counter)
        else:
            # Assuming ref_counter is an instance of Counter
            next_coord = ref_counter.baseTenConv()

        # Calculate the distance and convert it to coordinate format
        distance_base_10 = next_coord - curr_cord
        return self.coord_conv(distance_base_10)
    
    #Function takes a 'distance' in base 10 and returns a counter object + the distance
    def calculate_final_coordinate(self, distance):
        # Convert the current counter to base 10, add the distance, and convert back
        current_base10 = self.counter.baseTenConv()
        final_base10 = current_base10 + distance
        return self.counter.coord_conv(final_base10)
    

#Template class for new commands
class SkeleClass:
    def __init__(self, terminal, external_commands=None):
        self.terminal = terminal
        self.commands = {
            "help": self.show_help,
            # Add more internal commands here
            # ...
        }
        if external_commands:
            self.commands.update(external_commands)

    def show_help(self):
        help_message = "Available commands:\n"
        for cmd in self.commands:
            help_message += f"- {cmd}\n"
        return help_message

    def process_command(self, command):
        if command in self.commands:
            response = self.commands[command]()
            if response is None:
                response = ""
        else:
            response = "Unknown command."
        return response

    def run(self):
        print(self.show_help())
        while True:
            command_input = input("> ")
            command = command_input.lower()

            if command == "exit":
                print("Exiting.")
                break
            else:
                output = self.process_command(command)
                print(output)
