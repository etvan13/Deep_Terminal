from pathlib import Path


def is_raspberry_pi():
    """Rough check for Raspberry Pi environment."""
    try:
        with open("/proc/device-tree/model") as f:
            return "raspberry pi" in f.read().lower()
    except FileNotFoundError:
        return False


def ensure_dir(path: Path):
    """Create a directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root():
    """Return the root directory of the repo."""
    return Path(__file__).resolve().parent


def get_data_path():
    """
    Return the main data directory.

    On Raspberry Pi:
        ~/Database/data

    On other systems:
        <repo>/data
    """
    if is_raspberry_pi():
        path = Path.home() / "Database" / "data"
    else:
        path = get_project_root() / "data"

    return ensure_dir(path)


def get_leaderboard_path():
    """
    Return the trajectory leaderboard file path.

    On Raspberry Pi:
        ~/Database/etc/trajectory_leaderboard.json

    On other systems:
        <repo>/data/trajectory_leaderboard.json
    """
    if is_raspberry_pi():
        etc_dir = ensure_dir(Path.home() / "Database" / "etc")
        return etc_dir / "trajectory_leaderboard.json"
    else:
        data_dir = get_data_path()
        return data_dir / "trajectory_leaderboard.json"