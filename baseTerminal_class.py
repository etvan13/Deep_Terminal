import sys
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

    def default_message(self):
        Terminal.newpage()
        return f"{self.counter.get_counters()}\n" + "Type 'help' for a list of commands.\n"
    
    def process_command(self, command):
        if command in self.commands:
            response = self.commands[command]()
        else:
            response = "Unknown command."
        return self.default_message() + response + "\n"  # Append a newline

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
    
    # Utilize this tool at the top of each 'new page'
    @staticmethod
    def newpage():
        # Clear the console screen
        os.system('cls' if os.name == 'nt' else 'clear')

    def add_external_command(self, command_name, command_function):
        self.commands[command_name] = command_function

    ##COMMANDS##
    def show_help(self):
        return "- help\n- greetings\n- forwards\n- backwards"
    
    def greet(self):
        return "Hello World!"

    def forwards(self):
        self.counter.increment()
        return "Moved forwards."

    def backwards(self):
        self.counter.decrement()
        return "Moved backwards."
    
    #Function takes a 'distance' in base 10 and returns a counter object + the distance
    def calculate_final_coordinate(self, distance):
        # Convert the current counter to base 10, add the distance, and convert back
        current_base10 = self.counter.baseTenConv()
        final_base10 = current_base10 + distance
        return self.counter.coord_conv(final_base10)
    #########
    

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
        return ' '.join(str(c).zfill(2) for c in self.counters)
    
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
            # Assuming ref_counter is an instance of Counter
            next_coord = ref_counter.baseTenConv()

        # Calculate the distance and convert it to coordinate format
        distance_base_10 = next_coord - curr_cord
        return self.coord_conv(distance_base_10)
    

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
