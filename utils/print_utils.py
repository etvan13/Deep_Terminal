def print_tabbed(text, tab_width=16):
    """
    Print text with a left indentation to give the terminal
    a centered / console-style appearance.

    The text may contain multiple lines.
    """
    tab = " " * tab_width

    for line in text.split("\n"):
        print(tab + line)


def tabbed_input(prompt="> ", tab_width=16):
    """
    Input prompt that aligns with the tabbed terminal layout.
    """
    tab = " " * tab_width

    try:
        return input(f"{tab}{prompt}")
    except EOFError:
        print("\nInput interrupted. Please try again or use the exit command.")
        return ""