import os
import sys
import time
import threading
import termios
import tty

# Global variables
last_activity_time = time.time()
current_timeout_duration = 180  # Default duration in seconds (3 minutes)
stop_watchdog = threading.Event()  # This line initializes the stop_watchdog event
timer_lock = threading.Lock()

def reset_activity_timer(new_timeout_duration=None):
    global last_activity_time, current_timeout_duration
    with timer_lock:
        last_activity_time = time.time()
        if new_timeout_duration is not None:
            current_timeout_duration = new_timeout_duration

def watchdog_timer():
    while not stop_watchdog.is_set():
        time.sleep(1)  # Check every second
        with timer_lock:
            if (time.time() - last_activity_time) > current_timeout_duration:
                restart_program()
                break

def set_normal_term():
    fd = sys.stdin.fileno()
    normal_settings = termios.tcgetattr(fd)
    termios.tcsetattr(fd, termios.TCSADRAIN, normal_settings)

def restart_program():
    print("Restarting program...")
    set_normal_term()
    stop_watchdog.set()
    os.system('reset')
    os.execv(sys.executable, [sys.executable] + sys.argv)

def start_watchdog_timer():
    stop_watchdog.clear()
    watchdog_thread = threading.Thread(target=watchdog_timer)
    watchdog_thread.daemon = True
    watchdog_thread.start()

def stop_watchdog_timer():
    stop_watchdog.set()

def get_time_since_last_activity():
    global last_activity_time
    return time.time() - last_activity_time