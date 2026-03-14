# DEEP Terminal Manual
## Introduction and Quick Start

The DEEP Terminal is a modular command-driven environment designed for experimentation, exploration, and extensibility.  
It operates similarly to a traditional terminal, but instead of system commands, it runs **Python command classes** that can perform simulations, tools, demonstrations, or interactive systems.

The terminal is intentionally designed to be easy to expand.  
Anyone can add new functionality by writing a small command class and registering it with the terminal.

This manual explains how the terminal works and how contributors can safely extend it.

---

# Core Concept

The DEEP Terminal is built around a very simple execution pattern:

1. The terminal runs an input loop.
2. The user types a command.
3. The terminal resolves that command from a command dictionary.
4. The terminal calls a wrapper function.
5. The wrapper creates an instance of a command class.
6. The command class runs its `run()` method.
7. When `run()` finishes, control returns to the terminal.

Because of this structure, **every command in the system is just a Python class with a `run()` method**.

If the `run()` function returns, the terminal resumes normally.

---

# Terminal Architecture Overview

The system is composed of several main parts.

### The Terminal Class

The terminal class is responsible for:

- handling user input
- resolving commands
- running command wrappers
- displaying the terminal header
- managing the coordinate counter
- managing activity timers

The terminal **does not contain the logic of commands themselves**.  
Instead, it delegates functionality to command classes.

---

### Command Classes

Commands are independent Python classes that implement their own functionality.

A command might:

- run a simulation
- display a visualization
- provide a sub-menu
- read or write data
- perform a calculation
- run an interactive demo

Each command is responsible only for its own behavior.

When the command finishes its task, it simply returns control to the terminal.

---

### The Counter System

The terminal maintains a coordinate counter composed of six base-60 values.

Example coordinate:

    0 0 0 0 0 0

Each command execution advances the counter unless the command explicitly manages traversal itself.

Traversal commands like `forwards` and `backwards` directly modify the counter.

The coordinate system acts as a lightweight way to track terminal progression.

---

### Utility Systems

The terminal also includes shared utilities:

- screen formatting helpers
- activity watchdog timers
- coordinate handling
- optional data storage systems

Commands may use these systems when needed.

---

# The Simplest Possible Command

The simplest command is just a Python class with a `run()` method.

Example:

    class HelloCommand:
        def run(self):
            print("Hello from the DEEP terminal.")

This command does nothing more than print a message.

When the function ends, the command exits automatically.

---

# Registering a Command

Commands are registered in the terminal's command dictionary.

Example:

    self.commands = {
        "hello": self.hello_command
    }

The terminal associates the command name (`hello`) with a wrapper function.

---

# The Wrapper Function

The wrapper function creates the command object and runs it.

Example:

    def hello_command(self):
        cmd = HelloCommand()
        cmd.run()
        return "Returning to terminal."

The wrapper is responsible for connecting the terminal to the command class.

---

# Execution Flow

When a user runs a command, the system follows this sequence:

    User Input
        ↓
    Terminal Command Lookup
        ↓
    Wrapper Function
        ↓
    Command Object Created
        ↓
    Command.run()
        ↓
    Command Finishes
        ↓
    Terminal Resumes

This pattern keeps the terminal stable while allowing commands to run freely.

---

# Why Commands Are Implemented as Classes

Commands are implemented as classes instead of standalone functions so they can:

- maintain internal state
- run internal loops
- access terminal resources
- build complex interactive tools

This design keeps the terminal flexible while preventing the core system from becoming complicated.

---

# Design Philosophy

The DEEP Terminal follows a few guiding principles.

### Commands should be independent

Commands should contain their own logic and avoid modifying the terminal itself.

### The terminal should remain lightweight

The terminal handles routing and coordination, not functionality.

### Commands must return control

Every command must eventually return from its `run()` function so the terminal can resume operation.

### Extensibility is a priority

The system is intentionally designed so new commands can be added easily.

---

# What This Manual Covers

The rest of this manual explains:

- how to create commands
- how to access terminal features
- how to work with the coordinate system
- how to create interactive commands
- how to safely integrate larger programs

By following the patterns described in this guide, contributors can extend the terminal without breaking the core system.

---

# Next Section

Next: **Creating Your First Command**