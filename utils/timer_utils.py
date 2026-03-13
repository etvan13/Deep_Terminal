import time
import threading

DEFAULT_TIMEOUT = 120  # seconds

last_activity_time = time.time()
current_timeout_duration = DEFAULT_TIMEOUT
stop_watchdog = threading.Event()
timer_lock = threading.Lock()

timeout_triggered = False


def reset_activity_timer(value=None):
    """
    Reset the inactivity timer.

    If value is None → reset to DEFAULT_TIMEOUT.
    If value is provided → use that timeout duration.
    """
    global last_activity_time, current_timeout_duration

    with timer_lock:
        last_activity_time = time.time()
        current_timeout_duration = DEFAULT_TIMEOUT if value is None else value


def watchdog_timer():
    """Background thread that monitors inactivity."""
    global timeout_triggered

    while not stop_watchdog.is_set():
        time.sleep(1)

        try:
            with timer_lock:
                expired = (time.time() - last_activity_time) > current_timeout_duration

            if expired:
                timeout_triggered = True
                return

        except Exception:
            return


def start_watchdog_timer():
    """Start the watchdog thread."""
    global timeout_triggered

    timeout_triggered = False
    reset_activity_timer()
    stop_watchdog.clear()

    t = threading.Thread(target=watchdog_timer, daemon=True)
    t.start()


def stop_watchdog_timer():
    """Stop the watchdog thread."""
    stop_watchdog.set()


def get_timeout_state():
    """Return whether a timeout has occurred."""
    return timeout_triggered


def get_time_since_last_activity():
    with timer_lock:
        return time.time() - last_activity_time