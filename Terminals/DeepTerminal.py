import os
import sys
import difflib
import readline

from utils.counter import Counter
from utils.print_utils import*
from utils.timer_utils import*

from Commands.TrajectoryDemo import*
from Commands.Paper_Command.Paper import PaperCommand


class DeepTerminal:
    """
    Public-facing DEEP Terminal.

    This version preserves the core command flow and coordinate behavior
    of the full DEEP terminal while leaving out restricted or project-specific
    internals.

    The terminal is built around a simple pattern:
    - the terminal owns the input loop
    - commands are stored in dictionaries
    - the terminal resolves the user's input
    - the terminal runs the matching command function
    - most commands advance the counter after execution
    """

    def __init__(self):
        self.counter = Counter()

        # Commands that work in this public build
        self.commands = {
            "help": self.show_help,
            "info": self.info_command,
            "greetings": self.greet,
            "forwards": self.forwards,
            "backwards": self.backwards,
            "credits": self.credits_command,
            "research papers": self.paper_command,
            "2d trajectory": self.trajectory_command,
            "exit": self.exit_command,
        }

        # Commands preserved from the full DEEP terminal, but unavailable here
        self.unavailable_commands = {
            "planetary position": self.placeholder_command,
            "gear demo": self.placeholder_command,
            "quick message": self.placeholder_command,
            "leave message": self.placeholder_command,
            "read messages": self.placeholder_command,
            "dilation": self.placeholder_command,
            "black hole demo": self.placeholder_command,
            "black hole mapping": self.placeholder_command,
            "deep videos": self.placeholder_command,
            "suggestions": self.placeholder_command,
            "sleep": self.placeholder_command,
        }

        self.setup_readline()

    def setup_readline(self):
        """Enable simple tab completion for known commands."""
        readline.set_completer_delims("")

        def command_completer(text, state):
            matches = [cmd for cmd in self.commands if cmd.startswith(text)]
            return matches[state] if state < len(matches) else None

        readline.set_completer(command_completer)
        readline.parse_and_bind("tab: complete")

    @staticmethod
    def newpage():
        """Clear the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def default_message(self):
        """Build the terminal header shown after commands are processed."""
        ascii_header = r"""
    ______ _____ ___________   _____                   _             _
    |  _  \  ___|  ___| ___ \ |_   _|                 (_)           | |
    | | | | |__ | |__ | |_/ /   | | ___ _ __ _ __ ___  _ _ __   __ _| |
    | | | |  __||  __||  __/    | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
    | |/ /| |___| |___| |       | |  __/ |  | | | | | | | | | | (_| | |
    |___/ \____/\____/\_|       \_/\___|_|  |_| |_| |_|_|_| |_|\__,_|_|
        """

        self.newpage()
        return (
            f"{ascii_header}\n"
            f"Terminal Counter: {self.counter.get_counters()}\n"
            f"Type 'help' for commands.\n"
            f"Type 'info' for terminal details.\n"
        )

    def info(self):
        """Explain what this public build is and how it behaves."""
        return (
            "Welcome to the public DEEP Terminal build.\n\n"
            "This version preserves the core command flow and coordinate-based\n"
            "structure of the full DEEP terminal while leaving out restricted,\n"
            "private, or project-specific systems.\n\n"
            "The Terminal Counter is a base-60 six-part coordinate.\n"
            "Using commands advances the terminal through that coordinate space.\n"
            "The 'forwards' and 'backwards' commands move directly through the path,\n"
            "while most other commands advance the counter after they run.\n\n"
            "Some commands are intentionally preserved as unavailable placeholders\n"
            "so contributors can still see the broader structure of the terminal.\n"
        )

    def info_command(self):
        """Command wrapper for showing terminal information."""
        return self.info()

    def fuzzy_check(self, input_command, valid_commands, cutoff=0.6):
        """Return the closest matching command if similarity is high enough."""
        close_matches = difflib.get_close_matches(
            input_command,
            valid_commands,
            n=1,
            cutoff=cutoff
        )
        return close_matches[0] if close_matches else None

    def process_command(self, command, depth=0):
        """
        Resolve and run a command.

        Fuzzy matching is used so minor typos can still resolve to a command.
        Most commands advance the coordinate after successful execution.
        """
        if depth > 5:
            return "Error: command resolution exceeded maximum recursion depth."

        reset_activity_timer()

        if command in self.commands:
            response = self.commands[command]()

            # Most commands advance the terminal counter after execution.
            # 'backwards' is excluded because it already moves the counter directly.
            if command not in ["forwards", "backwards"]:
                self.counter.increment()

            return self.default_message() + "\n" + response + "\n"
        
        elif command in self.unavailable_commands:
            return (
                self.default_message() + f"\nThis command exists in the full DEEP terminal but is not "
                "\nincluded in the portable public build.\n"
            )

        corrected_cmd = self.fuzzy_check(command, self.commands.keys(), cutoff=0.6)
        if corrected_cmd:
            return self.process_command(corrected_cmd, depth + 1)

        return self.default_message() + f"\nUnknown command: '{command}'\n"

    def run(self):
        start_watchdog_timer() # Reboot timer to prevent sitting screens

        print_tabbed(self.default_message())
        print_tabbed(self.info())

        running = True

        while running:

            if get_timeout_state():
                print_tabbed(
                    "\nTerminal closed due to inactivity.\n\n"
                    "If this was unintentional, commands that run for a long time\n"
                    "should call reset_activity_timer() from utils.timer_utils.\n"
                )
                break

            try:
                command_input = tabbed_input("> ").strip().lower()

                if not command_input:
                    continue

                reset_activity_timer()

                output = self.process_command(command_input)

                print_tabbed(output)

            except KeyboardInterrupt:
                print("\nExiting terminal...")
                break

            except EOFError:
                print("\nExiting terminal...")
                break

        stop_watchdog_timer()
        print("Terminal closed.")

    #### COMMANDS ####

    def show_help(self):
        left_title = "Available commands:"
        right_title = "Unavailable in portable build:"

        left_list = list(self.commands.keys())
        right_list = list(self.unavailable_commands.keys())

        left_lines = [left_title] + [f"- {cmd}" for cmd in left_list]
        right_lines = [right_title] + [f"- {cmd}" for cmd in right_list]

        # Make both columns the same height
        max_lines = max(len(left_lines), len(right_lines))
        left_lines += [""] * (max_lines - len(left_lines))
        right_lines += [""] * (max_lines - len(right_lines))

        # Width of the left column
        left_width = max(len(line) for line in left_lines) + 6

        combined_lines = [
            f"{left:<{left_width}}{right}"
            for left, right in zip(left_lines, right_lines)
        ]

        return "\n".join(combined_lines)

    def greet(self):
        """Simple example command."""
        return "Hello Universe!"

    def forwards(self):
        """Move one step forward through the coordinate path."""
        self.counter.increment()
        return f"Moved forwards.\nCurrent Coordinate: {self.counter.get_counters()}"

    def backwards(self):
        """Move one step backward through the coordinate path."""
        self.counter.decrement()
        return f"Moved backwards.\nCurrent Coordinate: {self.counter.get_counters()}"

    def exit_command(self):
        """Exit the terminal program."""
        print("Exiting terminal...")
        sys.exit(0)

    def placeholder_command(self):
        """Used for commands preserved from the full terminal but not shipped here."""
        return (
            "This command exists in the full DEEP terminal, "
            "but is not included in the portable public build."
        )

    def paper_command(self):
        paper_obj = PaperCommand(self, newpage=self.newpage)
        message = paper_obj.run()
        return "Exiting back to main terminal."

    def trajectory_command(self):
        trajectory_obj = Trajectory()
        self.newpage()
        msg = trajectory_obj.run()
        return msg + "\nExiting back to main terminal."

    def credits_command(self):
        """Show DEEP project credits."""
        return """
DEEP Project Credits

James Thomas Florence (JT): "MACHKA"

2021-2022:
Emily Wong
Esteban Castillo
Navya Mittal
Zach Amos

2022-2023:
Ethan Van Swearingen: "Why? Kaus."
Jared Eshleman
Kevin Black
Lilliana Rogers: "LHOOQ"
Patrick Campbell: "I hardly know her"
Tyler Mitts

2023-2024:
'Other Chase' Thompson: "What is physics without love, what is love without physics..."
Jacob Rodriguez
Ben Guidry: "thank"
Chase Grochett: "Whoop!"
Derek Baughman: "love sosa"
Gabriel Kinjo Andrade: "Do not pray for easy lives, pray to be stranger"
Kay Tillis
Yubo Wang: "DEEP is the reason I bench 225 8 reps."

2024-2025:
Steven Alvarado: "With great power, comes great responsibility"
Andrew Blades: "Sharks with Frickin' Laser Beams" - Dr. Evil
Mabry Hogan: "Best astrologer & cosmetologist"
Austin Porter
Brandon Zhu
Ishika Patel
""".strip()