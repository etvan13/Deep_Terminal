import json
from pathlib import Path


class Counter:
    """
    Base-60 six-slot DEEP terminal coordinate counter.

    Coordinate format:
        a b c d e f

    Each slot ranges from 0 to 59.
    Overflow beyond the final slot increments the universe count.
    """

    def __init__(self, save_path=None, auto_load=True):
        self.counters = [0] * 6
        self.universes = 0

        self.save_path = Path(save_path) if save_path else Path("data/current_coordinate.json")
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        if auto_load:
            self.load()

    def copy(self):
        """Return a copy of the current counter."""
        new_counter = Counter(save_path=self.save_path, auto_load=False)
        new_counter.counters = self.counters[:]
        new_counter.universes = self.universes
        return new_counter

    def load(self):
        """Load counter state from disk if available."""
        if not self.save_path.exists():
            self.save()
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            self.counters = data.get("coordinate_list", [0] * 6)
            self.universes = data.get("universes", 0)

        except (json.JSONDecodeError, OSError):
            print("Counter save file invalid. Resetting to zero state.")
            self.counters = [0] * 6
            self.universes = 0
            self.save()

    def save(self):
        """Save counter state to disk."""
        data = {
            "coordinate": self.get_counters(),
            "coordinate_list": self.counters,
            "universes": self.universes,
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=4)

    def increment(self):
        self._update_counters(1)
        self.save()

    def decrement(self):
        self._update_counters(-1)
        self.save()

    def spec_change(self, value):
        self._update_counters(value)
        self.save()

    def _update_counters(self, delta):
        for i in range(len(self.counters)):
            self.counters[i] += delta

            if delta > 0 and self.counters[i] >= 60:
                self.counters[i] %= 60
                if i == len(self.counters) - 1:
                    self.universes += 1
                continue

            if delta < 0 and self.counters[i] < 0:
                self.counters[i] = 59
                if i == len(self.counters) - 1:
                    self.universes -= 1
                continue

            break

    @staticmethod
    def parse_coordinate(coord_str):
        """Parse a coordinate string of the form '## ## ## ## ## ##'."""
        parts = coord_str.split()

        if len(parts) != 6 or not all(part.isdigit() and 0 <= int(part) < 60 for part in parts):
            raise ValueError(
                "Invalid coordinate format. Expected: ## ## ## ## ## ## with values 0-59."
            )

        return [int(x) for x in parts]

    def get_counters(self):
        """Return the coordinate as a space-separated string."""
        return " ".join(map(str, self.counters))

    def get_counters_list(self):
        """Return the coordinate as a list."""
        return self.counters[:]

    def baseTenConv(self, digits=None):
        """
        Convert the internal counters or an external base-60 digit list to base-10.
        """
        if digits is None:
            digits = self.counters

        return sum(d * (60 ** i) for i, d in enumerate(digits))

    def strCoord_conv(self, number):
        """Convert a base-10 number into a zero-padded coordinate string."""
        digits = self.coord_conv(number)
        return " ".join(str(d).zfill(2) for d in digits)

    def coord_conv(self, number):
        """Convert a base-10 number into a six-slot base-60 coordinate list."""
        number %= (60 ** 6)

        digits = []
        while number > 0:
            digits.append(number % 60)
            number //= 60

        while len(digits) < 6:
            digits.append(0)

        return digits

    def univ_count(self, number):
        """Return the universe count represented by a raw base-10 number."""
        return number // (60 ** 6)

    def calculate_distance(self, ref_counter):
        """
        Return the coordinate distance from the current counter to another counter.
        """
        curr_coord = self.baseTenConv()

        if isinstance(ref_counter, list):
            next_coord = self.baseTenConv(ref_counter)
        else:
            next_coord = ref_counter.baseTenConv()

        distance_base_10 = next_coord - curr_coord
        return self.coord_conv(distance_base_10)