# DEEP Terminal (Public Build)

A lightweight command-based terminal designed to demonstrate the structure and functionality of the DEEP Terminal system.

This public version preserves the **core command architecture and coordinate traversal system** while leaving out project-specific or restricted components from the full DEEP environment.

The goal of this repository is to provide a **portable version of the terminal** that anyone can run, explore, and extend.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/etvan13/Deep_Terminal
cd deep-terminal
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the terminal:

```bash
python main.py
```

---

# Basic Usage

Once the terminal starts, you will see the DEEP terminal banner and coordinate counter.

Commands can be entered directly at the prompt.

Example commands:

```
help
info
forwards
backwards
2d trajectory
```

Type:

```
help
```

to see the list of available commands.

---

# Terminal Counter

At the top of the interface you will see a **Terminal Counter**.

This represents a coordinate in a base-60 six-part system used by the DEEP terminal to track traversal through command interactions.

Most commands automatically advance the counter after execution.

Special commands like `forwards` and `backwards` allow direct movement through the coordinate path.

---

# Command Architecture

The terminal is designed to be easily extendable.

Commands follow a very simple structure:

1. A command is added to the command dictionary in `DeepTerminal`.
2. The command calls a class or function that performs the work.
3. The command returns a message to the terminal.

The terminal handles:

- printing output
- formatting
- coordinate updates
- inactivity timing

This separation keeps commands simple and allows contributors to focus only on the behavior they want to implement.

---

# Example Command Pattern

A typical command follows this structure:

```python
class ExampleCommand:
    def __init__(self, terminal):
        self.terminal = terminal

    def run(self):
        return "Example command executed."
```

The terminal registers the command:

```python
"example": self.example_command
```

And calls it:

```python
def example_command(self):
    cmd = ExampleCommand(self)
    return cmd.run()
```

---

# Inactivity Timer

The terminal includes an inactivity watchdog.

If the terminal is idle for too long, it will close automatically.

Commands that run for a long time can prevent this by calling:

```
reset_activity_timer()
```

from `utils.timer_utils`.

---

# Portable Public Build

This repository is a **portable version of the DEEP terminal**.

Some commands from the full system are preserved in the help menu but are unavailable in this build. These placeholders demonstrate how the full terminal is structured without exposing project-specific components.

---

# Goals of This Repository

This project exists to:

- demonstrate the DEEP terminal architecture
- provide a portable command-based terminal environment
- allow contributors to experiment with custom commands
- serve as a base for terminal-driven demos and tools

---

# Future Documentation

More detailed guides will be added later, including:

- writing custom commands
- command lifecycle
- coordinate traversal concepts
- demo command implementations

---

# License

This repository is provided for experimentation, learning, and extension.
