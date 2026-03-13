# # Simple Paradoxical Use License (SPUL)

# **This license applies to the base terminal structure, that being: the coordinate system and the navigability of it base data structure.**

# 1. **Permission to Use:**
#    - Anyone is free to use, copy, distribute, and create derivative works from this work, including for commercial purposes.

# 2. **Paradoxical Ownership 'Kaus':**
#    - Ownership of the original work is paradoxically assigned 'Kaus,' which exists perpetually in the future and is always out of reach of any present or entity.

# 3. **Derivative Works:**
#    - Derivative works can be created, but they must include this license, ensuring that the original basis remains unaltered and free from control or ownership claims. The derivative works can be used for any purpose.

# 4. **Enforcement Clause:**
#    - Any person or entity that respects and abides by the terms of this license has the right to enforce these terms against those who fail to comply.

# 5. **Universal Applicability:**
#    - This license is applicable universally, regardless of jurisdiction.

# By using this work, you agree to the terms of the Simple Paradoxical Use License (SPUL).


import os
import json

# -------------------- #
# Centered Print/Input #
# -------------------- #
def print_tabbed(text, tab_width=25):
    """
    Prints text centered by adding a tab of spaces before each line.
    :param text: The text to print.
    :param tab_width: The number of spaces for the tab (default is 25).
    """
    tab = ' ' * tab_width
    lines = text.split('\n')
    for line in lines:
        print(tab + line)

def tabbed_input(prompt, tab_width=25):
    """
    Displays a prompt centered by adding a tab of spaces before it and waits for user input.
    :param prompt: The prompt text to display.
    :param tab_width: The number of spaces for the tab (default is 25).
    :return: The user input.
    """
    tab = ' ' * tab_width
    try:
        return input(f"{tab}{prompt}")
    except EOFError:
        print("\nInput interrupted. Please try again or use the designated exit command.")
        return ""  # Return an empty string


# ---------------- #
# Main Terminal    #
# ---------------- #
class Terminal:
    def __init__(self, starting_coordinate="0 0 0 0 0 0"):
        """
        Initializes the Terminal object.
        :param starting_coordinate: The initial coordinate to start the terminal on (default is "0 0 0 0 0 0").
        """
        self.counter = Counter(starting_coordinate)  # Initialize Counter with a starting coordinate
        self.data_manager = DataManager()  # Initialize the DataManager
        self.start_coordinate = starting_coordinate  # Save the starting coordinate
        self.current_coordinate = starting_coordinate  # Set the current coordinate

        # Define available commands
        self.commands = {
            "help":      self.show_help,
            "greetings": self.greet,
            "forwards":  self.forwards,
            "backwards": self.backwards,
            "save_data": self.save_data_command,
            "load_data": self.load_data_command,
            "set_coord": self.set_coordinate_command,
        }

    @staticmethod
    def newpage():
        """
        Clears the terminal screen.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def set_start_coordinate(self, coordinate):
        """
        Sets the starting and current coordinate for the terminal.
        :param coordinate: The coordinate to set as the starting point.
        """
        self.start_coordinate = coordinate
        self.current_coordinate = coordinate

    def default_message(self):
        """
        Generates the default terminal message, including the current coordinate.
        :return: The default message as a string.
        """
        self.newpage()
        return f"Current Coordinate: {self.current_coordinate}\n" + "Type 'help' for a list of commands.\n"

    def process_command(self, command):
        """
        Processes a user-entered command and executes the corresponding method.
        :param command: The command entered by the user.
        :return: The response message from the executed command.
        """
        if command in self.commands:
            response = self.commands[command]()
        else:
            response = "Unknown command."
        return self.default_message() + "\n" + response + "\n"

    def run(self):
        """
        Starts the terminal's main input loop, allowing the user to enter commands.
        """
        print(self.default_message())
        while True:
            command_input = input("> ")
            command = command_input.lower()
            output = self.process_command(command)
            print(output)
            if command == "exit":
                break

    # ---------- Built-in Terminal Commands ---------- #
    def show_help(self):
        """
        Displays a list of available terminal commands.
        :return: A string containing the help message.
        """
        return (
            "Available commands:\n"
            "- help      : Show this help\n"
            "- greetings : Prints a simple greeting\n"
            "- forwards  : Move counter forward\n"
            "- backwards : Move counter backward\n"
            "- save_data : Prompt to save data at a coordinate\n"
            "- load_data : Prompt to load data from a coordinate\n"
            "- set_coord : Allow user to alter the current coordinate\n"
            "- exit      : Exit the application"
        )

    def greet(self):
        """
        Returns a simple greeting message.
        """
        return "Hello Universe!"

    def set_coordinate_command(self):
        """
        Prompts the user to set the current coordinate and updates the Counter's state.
        """
        coord = input("Enter new coordinate: ")
        try:
            # Update both the Counter object and the current coordinate
            self.counter.set_coordinate(coord)
            self.current_coordinate = coord
            return f"Counter set to: {self.counter.get_counters()}"
        except ValueError as e:
            return str(e)

    def forwards(self):
        """
        Increments the counter by one step and updates the current coordinate.
        """
        self.counter.increment()  # Increment the internal counter
        self.current_coordinate = self.counter.get_counters()  # Update the terminal's current coordinate
        return f"Moved forwards to {self.current_coordinate}."

    def backwards(self):
        """
        Decrements the counter by one step and updates the current coordinate.
        """
        self.counter.decrement()  # Decrement the internal counter
        self.current_coordinate = self.counter.get_counters()  # Update the terminal's current coordinate
        return f"Moved backwards to {self.current_coordinate}."


    def save_data_command(self):
        """
        Prompts the user to save data at a specific coordinate.
        If no coordinate is entered, uses the current coordinate.
        """
        coord = input(
            f"Enter coordinate to save data (or press Enter to use the current: '{self.current_coordinate}'): "
        ).strip()
        if not coord:
            coord = self.current_coordinate  # Default to current coordinate

        title = input("Enter title: ")
        message = input("Enter message: ")
        self.data_manager.save_message(coord, title, message)
        return f"Data saved at '{coord}'."

    def load_data_command(self):
        """
        Prompts the user to load data from a specific coordinate.
        If no coordinate is entered, uses the current coordinate.
        """
        coord = input(
            f"Enter coordinate to load data (or press Enter to use the current: '{self.current_coordinate}'): "
        ).strip()
        if not coord:
            coord = self.current_coordinate  # Default to current coordinate

        messages = self.data_manager.load_messages(coord)
        if not messages:
            return f"No messages found at '{coord}'."

        # Format the messages for display
        lines = [f"Messages at '{coord}':"]
        for i, msg in enumerate(messages, start=1):
            lines.append(f"{i}) Title: {msg['title']}\n   Msg: {msg['message']}")

        return "\n".join(lines)





# -------------- #
# Counter Class  #
# -------------- #
class Counter:
    def __init__(self, starting_coordinate="0 0 0 0 0 0"):
        """
        Initializes the Counter with a specific starting coordinate.
        The coordinate is parsed into a list of integers, and the universe count is set to 0.
        """
        self.counters = self.parse_coordinate(starting_coordinate)  # Parse and store the starting coordinate
        self.universes = 0  # Universes start at 0

    @staticmethod
    def parse_coordinate(coord_str):
        """
        Parses a coordinate string (e.g., "1 58 0 0 1 0") into a list of integers.
        """
        if ' ' in coord_str:
            parts = coord_str.split()
            if len(parts) != 6 or not all(part.isdigit() and int(part) < 60 for part in parts):
                raise ValueError("Invalid coordinate format. Each number must be less than 60. Format: ## ## ## ## ## ##")
            return [int(x) for x in parts]
        else:
            raise ValueError("Invalid input. Expected coordinate format: ## ## ## ## ## ##")

    def get_counters(self):
        """
        Returns the current counter as a formatted string.
        """
        return ' '.join(str(c) for c in self.counters)

    def set_coordinate(self, coordinate):
        """
        Sets the counter to a new coordinate.
        """
        self.counters = self.parse_coordinate(coordinate)  # Parse and set the new counters

    def increment(self):
        """
        Increments the counter by 1, rolling over to the next higher counter if needed.
        """
        self._update_counters(1)

    def decrement(self):
        """
        Decrements the counter by 1, rolling under to the next lower counter if needed.
        """
        self._update_counters(-1)

    def _update_counters(self, delta):
        """
        Updates the counter by a given delta (positive or negative) and handles roll-over/roll-under.
        """
        for i in range(len(self.counters)):
            self.counters[i] += delta
            if delta > 0 and self.counters[i] == 60:
                self.counters[i] = 0
                if i == len(self.counters) - 1:
                    self.universes += 1  # Roll over to the next universe
                continue
            elif delta < 0 and self.counters[i] == -1:
                self.counters[i] = 59
                if i == len(self.counters) - 1:
                    self.universes -= 1  # Roll under to the previous universe
                continue
            break

    def univ_count(self):
        """
        Returns the current universe count.
        """
        return self.universes



# ------------------ #
# Data Manager Class #    #!#!#!#! Rewrite/expand for separate data structure !#!#!#!#
# ------------------ #
import os
import json

class DataManager:
    """
    A more dynamic, coordinate-based data store.
    Each coordinate (format 'p0 p1 p2 p3 p4 p5') is broken down into:
      base_dir / p0 / p1 / p2 / p3 / p4 / p5.json
    Then, inside p5.json, we store a dict like:
      {
        "p0 p1 p2 p3 p4 p5": {
            "messages": [...],
            "pointer_data": [...]
        }
      }
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            # By default, store data alongside the script in a folder named 'coordinate_data'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(script_dir, "coordinate_data")

        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_message(self, coordinate, title, message):
        """
        Save a new 'message' under the given coordinate.
        """
        # Parse coordinate into a file path
        file_path = self._coordinate_to_filepath(coordinate)
        json_data = self._load_or_create_json(file_path)

        # Ensure that the dictionary has a top-level key for this coordinate
        if coordinate not in json_data:
            json_data[coordinate] = {}

        # If there's no "messages" list for this coordinate, initialize it
        if "messages" not in json_data[coordinate]:
            json_data[coordinate]["messages"] = []

        # Create the new message entry
        new_entry = {
            "coordinate": coordinate,
            "title": title,
            "message": message
        }
        # Append it
        json_data[coordinate]["messages"].append(new_entry)

        # Write out the file
        self._write_json(file_path, json_data)

    def load_messages(self, coordinate):
        """
        Return the 'messages' list for the given coordinate. 
        If no file or no messages, return [].
        """
        file_path = self._coordinate_to_filepath(coordinate)
        if not os.path.exists(file_path):
            return []

        json_data = self._load_or_create_json(file_path)
        # Grab the coordinate node
        coord_node = json_data.get(coordinate, {})
        # Return whatever is in 'messages'
        return coord_node.get("messages", [])

    # ------------------------- #
    #   Internal Helper Funcs   #
    # ------------------------- #

    def _coordinate_to_filepath(self, coordinate):
        """
        Translates the 6-part coordinate into a directory path + filename.
          e.g.  '1 58 0 0 1 0' -> base_dir / '1' / '58' / '0' / '0' / '1' / '0.json'
        """
        parts = coordinate.split()
        if len(parts) != 6:
            raise ValueError(f"Expected 6 parts in coordinate, got {len(parts)}: {parts}")

        p0, p1, p2, p3, p4, p5 = parts

        # Build the directory
        dir_path = os.path.join(self.base_dir, p0, p1, p2, p3, p4)
        os.makedirs(dir_path, exist_ok=True)

        # File name is p5 + '.json'
        filename = f"{p5}.json"
        file_path = os.path.join(dir_path, filename)
        return file_path

    def _load_or_create_json(self, file_path):
        """
        Loads the JSON file if it exists, otherwise returns an empty dict.
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Corrupted or empty file -> just overwrite with a blank dict
                pass
        return {}

    def _write_json(self, file_path, data):
        """
        Writes 'data' as JSON to 'file_path'.
        """
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)



# ------------------ #
#     Entry Point    #
# ------------------ #
if __name__ == "__main__":
    # Example usage:
    my_terminal = Terminal()

    #!# Set the starting coordinate here #!#
    starting_coordinate = "10 0 0 0 0 0" # Note formatting (each ## is a number 0-59)
    my_terminal.set_start_coordinate(starting_coordinate)

    # Run the terminal
    my_terminal.run()
