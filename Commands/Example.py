class ExampleCommand:
    """
    Example external command for the portable DEEP terminal.

    This shows contributors the expected shape of a command class:
    - accept terminal and counter in __init__
    - implement a run() method
    - optionally provide internal help/subcommands
    """

    def __init__(self, terminal):
        self.terminal = terminal
        self.counter = terminal.counter

        self.commands = {
            "help": self.show_help,
            "where": self.show_coordinate,
            "hello": self.say_hello,
        }

    def show_help(self):
        print(
            "\nExample command options:\n"
            "- help  : show this message\n"
            "- where : print current coordinate\n"
            "- hello : print a greeting\n"
            "- exit  : return to the main terminal\n"
        )

    def show_coordinate(self):
        print(f"Current Coordinate: {self.counter.get_counters()}")

    def say_hello(self):
        print("Hello from the example command!")

    def run(self):
        self.terminal.newpage()
        print("Entered example command.")
        print("Type 'help' for options, or 'exit' to return.\n")

        while True:
            user_input = input("example> ").strip().lower()

            if user_input == "exit":
                break
            elif user_input in self.commands:
                self.commands[user_input]()
            elif not user_input:
                continue
            else:
                print("Unknown example subcommand. Type 'help' for options.")