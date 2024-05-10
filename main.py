from Deep_Terminal import Terminal
from timer_utils import*
import signal


# Define a signal handler for ignoring signals
def ignore_signal(signum, frame): 
    return

# Runs the Terminal through main
def main():
    # Set the SIGINT handler to the ignore_signal function
    signal.signal(signal.SIGINT, ignore_signal) # Ignores Ctrl+C
    # signal.signal(signal.SIGTSTP, ignore_signal)  # Ignores Ctrl+Z
    try:
        terminal = Terminal()
        start_watchdog_timer()
        terminal.run_start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        stop_watchdog_timer() # clean up
        print("Stopping watchdog timer and cleaning up before exit/restart.")

if __name__ == "__main__":
    main()

