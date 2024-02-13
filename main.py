# from AllClasses.dilationTerminal_class import Terminal
from Deep_Terminal import Terminal
def main():
    terminal = Terminal()
    terminal.run()

if __name__ == "__main__":
    main()




# import sqlite3

# conn = sqlite3.connect('messages.db')
# cur = conn.cursor()
# cur.execute("SELECT * FROM messages")
# records = cur.fetchall()

# for record in records:
#     print(record)

# conn.close()

# from baseTerminal_class import Counter
# def main():
#     # Create a Counter instance
#     counter = Counter()
#     counter3 = Counter()
#     counter3.counters = [0, 1, 0, 0, 0, 0]

#     # Test 1: Increment the counter
#     counter.increment()
#     print(f"Test 1 - Increment: {counter.get_counters()}")  # Expect "01 00 00 00 00 00"

#     # Test 2: Decrement the counter
#     counter.decrement()
#     print(f"Test 2 - Decrement: {counter.get_counters()}")  # Expect "00 00 00 00 00 00"

#     # Test 3: Convert to base 10 ####PASS####
#     base10 = counter3.baseTenConv()
#     print(f"Test 3 - Base 10 Conversion: {base10}")  # Expect "0" for "00 00 00 00 00 00"

#     # Test 4: Convert base 10 to coordinate
#     coord = counter.coord_conv(777600000)
#     print(f"Test 4 - Base 10 to Coordinate: {coord}")  # Expect "01 00 01 00 00 00"

#     # Test 5: Calculate distance
#     counter2 = Counter()
#     counter2.counters = [1, 0, 0, 0, 1, 0]  # Set to "02 00 00 00 00 00"
#     distance = counter2.calculate_distance(counter3)
#     print(f"Test 5 - Distance: {distance}")  # Expect the distance from "00 00 00 00 00 00" to "02 00 00 00 00 00"

# if __name__ == "__main__":
#     main()
