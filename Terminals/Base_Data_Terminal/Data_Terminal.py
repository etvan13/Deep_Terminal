import os
import sys
import json
import difflib

try:
    import readline
except ImportError:
    readline = None


# ============================================================
# Simple Paradoxical Use License (SPUL)
# ============================================================
# This license applies to the base terminal structure:
# the coordinate system and the navigability of its base data structure.
#
# 1. Permission to Use:
#    Anyone is free to use, copy, distribute, and create derivative
#    works from this work, including for commercial purposes.
#
# 2. Paradoxical Ownership "Kaus":
#    Ownership of the original work is paradoxically assigned to "Kaus,"
#    which exists perpetually in the future and is always out of reach
#    of any present person or entity.
#
# 3. Derivative Works:
#    Derivative works may be created, but they must include this license,
#    ensuring that the original basis remains unaltered and free from
#    control or ownership claims.
#
# 4. Enforcement Clause:
#    Any person or entity that respects and abides by the terms of this
#    license has the right to enforce these terms against those who fail
#    to comply.
#
# 5. Universal Applicability:
#    This license is applicable universally, regardless of jurisdiction.
#
# By using this work, you agree to the terms of the SPUL.
# ============================================================


# ============================================================
# Optional UI Helpers
# ============================================================
def print_tabbed(text, tab_width=4):
    """
    Print text with a fixed left padding.
    """
    tab = " " * tab_width
    for line in text.split("\n"):
        print(tab + line)


def tabbed_input(prompt, tab_width=4):
    """
    Display an input prompt with a fixed left padding.
    """
    tab = " " * tab_width
    try:
        return input(f"{tab}{prompt}")
    except EOFError:
        print("\nInput interrupted.")
        return ""


# ============================================================
# Counter
# ============================================================
class Counter:
    """
    A 6-part base-60 counter.

    Example:
        0 0 0 0 0 0 -> 1 0 0 0 0 0

    In this implementation, the leftmost slot changes first.
    """

    def __init__(self, starting_coordinate="0 0 0 0 0 0"):
        self.counters = self.parse_coordinate(starting_coordinate)
        self.universes = 0

    @staticmethod
    def parse_coordinate(coord_str):
        parts = coord_str.split()

        if len(parts) != 6:
            raise ValueError(
                "Invalid coordinate format. Expected: ## ## ## ## ## ##"
            )

        values = []
        for part in parts:
            if not part.isdigit():
                raise ValueError("Each coordinate part must be a non-negative integer.")
            value = int(part)
            if not 0 <= value < 60:
                raise ValueError("Each coordinate value must be between 0 and 59.")
            values.append(value)

        return values

    def get_counters(self):
        return " ".join(str(c) for c in self.counters)

    def set_coordinate(self, coordinate):
        self.counters = self.parse_coordinate(coordinate)

    def increment(self):
        self._update_counters(1)

    def decrement(self):
        self._update_counters(-1)

    def _update_counters(self, delta):
        for i in range(len(self.counters)):
            self.counters[i] += delta

            if delta > 0 and self.counters[i] == 60:
                self.counters[i] = 0
                if i == len(self.counters) - 1:
                    self.universes += 1
                continue

            if delta < 0 and self.counters[i] == -1:
                self.counters[i] = 59
                if i == len(self.counters) - 1:
                    self.universes -= 1
                continue

            break

    def univ_count(self):
        return self.universes


# ============================================================
# Data Manager
# ============================================================
class DataManager:
    """
    Coordinate-based storage using reversed path nesting.

    Coordinate:
        p0 p1 p2 p3 p4 p5

    Filesystem:
        base_dir / p5 / p4 / p3 / p2 / p1.json

    Full coordinate is preserved as the key inside the JSON file.
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(script_dir, "coordinate_data")

        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_message(self, coordinate, title, message):
        Counter.parse_coordinate(coordinate)

        file_path = self._coordinate_to_filepath(coordinate)
        json_data = self._load_or_create_json(file_path)

        if coordinate not in json_data:
            json_data[coordinate] = {"messages": []}

        json_data[coordinate]["messages"].append({
            "coordinate": coordinate,
            "title": title,
            "message": message
        })

        self._write_json(file_path, json_data)

    def load_messages(self, coordinate):
        Counter.parse_coordinate(coordinate)

        file_path = self._coordinate_to_filepath(coordinate)
        if not os.path.exists(file_path):
            return []

        json_data = self._load_or_create_json(file_path)
        return json_data.get(coordinate, {}).get("messages", [])

    def _coordinate_to_filepath(self, coordinate):
        parts = coordinate.split()
        if len(parts) != 6:
            raise ValueError(f"Expected 6 parts in coordinate, got {len(parts)}.")

        p0, p1, p2, p3, p4, p5 = parts

        dir_path = os.path.join(self.base_dir, p5, p4, p3, p2)
        os.makedirs(dir_path, exist_ok=True)

        return os.path.join(dir_path, f"{p1}.json")

    def _load_or_create_json(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        return {}

    def _write_json(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


# ============================================================
# Terminal
# ============================================================
class Terminal:
    """
    A simple demonstration terminal for coordinate-based traversal and storage.

    This terminal is meant to show:
    - how a 6-part base-60 coordinate can be traversed
    - how coordinates can map to stored data
    - how data can be saved and loaded through terminal commands
    """

    def __init__(self, starting_coordinate="0 0 0 0 0 0"):
        self.counter = Counter(starting_coordinate)
        self.data_manager = DataManager()

        self.start_coordinate = starting_coordinate
        self.current_coordinate = starting_coordinate

        self.commands = {
            "help": self.show_help,
            "info": self.info_command,
            "greetings": self.greet,
            "forwards": self.forwards,
            "backwards": self.backwards,
            "save_data": self.save_data_command,
            "load_data": self.load_data_command,
            "set_coord": self.set_coordinate_command,
            "show_coord": self.show_coord_command,
            "exit": self.exit_command,
        }

        self.setup_readline()

    def setup_readline(self):
        """
        Enable basic tab-completion for commands when readline is available.
        """
        if readline is None:
            return

        readline.set_completer_delims("")

        def command_completer(text, state):
            matches = [cmd for cmd in self.commands if cmd.startswith(text)]
            return matches[state] if state < len(matches) else None

        readline.set_completer(command_completer)
        readline.parse_and_bind("tab: complete")

    @staticmethod
    def newpage():
        os.system("cls" if os.name == "nt" else "clear")

    def default_message(self):
        """
        Build the terminal header shown after each command.
        """
        self.newpage()
        return (
            "=== Coordinate Data Terminal ===\n"
            f"Current Coordinate: {self.current_coordinate}\n"
            f"Universe Offset: {self.counter.univ_count()}\n"
            "Type 'help' for commands.\n"
            "Type 'info' for terminal details.\n"
        )

    def info(self):
        return (
            "This terminal demonstrates a coordinate-based data structure.\n\n"
            "The coordinate is a six-part base-60 address.\n"
            "You can move through the coordinate space, store messages at a coordinate,\n"
            "and retrieve messages from a coordinate.\n\n"
            "It is meant to serve as a readable reference implementation showing\n"
            "how traversal, storage, and retrieval can all be tied to the same\n"
            "coordinate system.\n"
        )

    def info_command(self):
        return self.info()

    def fuzzy_check(self, input_command, valid_commands, cutoff=0.6):
        """
        Return the closest command match if similarity is high enough.
        """
        matches = difflib.get_close_matches(
            input_command,
            valid_commands,
            n=1,
            cutoff=cutoff
        )
        return matches[0] if matches else None

    def set_start_coordinate(self, coordinate):
        self.counter.set_coordinate(coordinate)
        self.start_coordinate = coordinate
        self.current_coordinate = coordinate

    def process_command(self, command, depth=0):
        """
        Resolve and run a command.

        Fuzzy matching is used so small typos can still resolve.
        """
        if depth > 5:
            return self.default_message() + "\nError: command resolution exceeded max depth.\n"

        if command in self.commands:
            response = self.commands[command]()
            return self.default_message() + "\n" + response + "\n"

        corrected = self.fuzzy_check(command, self.commands.keys(), cutoff=0.6)
        if corrected:
            return self.process_command(corrected, depth + 1)

        return self.default_message() + f"\nUnknown command: '{command}'\n"

    def run(self):
        """
        Main terminal loop.
        """
        print_tabbed(self.default_message())
        print_tabbed(self.info())

        while True:
            try:
                command_input = tabbed_input("> ").strip().lower()

                if not command_input:
                    continue

                output = self.process_command(command_input)
                print_tabbed(output)

            except KeyboardInterrupt:
                print("\nExiting terminal...")
                break
            except EOFError:
                print("\nExiting terminal...")
                break

        print("Terminal closed.")

    # --------------------------------------------------------
    # Commands
    # --------------------------------------------------------

    def show_help(self):
        return (
            "Available commands:\n"
            "- help       : Show this help message\n"
            "- info       : Explain what this terminal demonstrates\n"
            "- greetings  : Print a simple greeting\n"
            "- forwards   : Move forward one coordinate step\n"
            "- backwards  : Move backward one coordinate step\n"
            "- save_data  : Save a title/message at a coordinate\n"
            "- load_data  : Load messages from a coordinate\n"
            "- set_coord  : Manually set the current coordinate\n"
            "- show_coord : Show the current coordinate\n"
            "- exit       : Exit the terminal"
        )

    def greet(self):
        return "Hello Universe!"

    def show_coord_command(self):
        return f"Current Coordinate: {self.current_coordinate}"

    def set_coordinate_command(self):
        coord = input("Enter new coordinate: ").strip()
        try:
            self.counter.set_coordinate(coord)
            self.current_coordinate = self.counter.get_counters()
            return f"Counter set to: {self.current_coordinate}"
        except ValueError as e:
            return str(e)

    def forwards(self):
        self.counter.increment()
        self.current_coordinate = self.counter.get_counters()
        return f"Moved forwards.\nCurrent Coordinate: {self.current_coordinate}"

    def backwards(self):
        self.counter.decrement()
        self.current_coordinate = self.counter.get_counters()
        return f"Moved backwards.\nCurrent Coordinate: {self.current_coordinate}"

    def save_data_command(self):
        coord = input(
            f"Enter coordinate to save data (or press Enter to use current: '{self.current_coordinate}'): "
        ).strip()
        if not coord:
            coord = self.current_coordinate

        title = input("Enter title: ").strip()
        message = input("Enter message: ").strip()

        try:
            self.data_manager.save_message(coord, title, message)
            return f"Data saved at '{coord}'."
        except ValueError as e:
            return f"Save failed: {e}"

    def load_data_command(self):
        coord = input(
            f"Enter coordinate to load data (or press Enter to use current: '{self.current_coordinate}'): "
        ).strip()
        if not coord:
            coord = self.current_coordinate

        try:
            messages = self.data_manager.load_messages(coord)
        except ValueError as e:
            return f"Load failed: {e}"

        if not messages:
            return f"No messages found at '{coord}'."

        lines = [f"Messages at '{coord}':"]
        for i, msg in enumerate(messages, start=1):
            lines.append(f"{i}) Title: {msg['title']}")
            lines.append(f"   Msg: {msg['message']}")

        return "\n".join(lines)

    def exit_command(self):
        print("Exiting terminal...")
        sys.exit(0)


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    my_terminal = Terminal()
    my_terminal.set_start_coordinate("10 0 0 0 0 0")
    my_terminal.run()