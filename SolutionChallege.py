import json
import math


class SparseTable:
    def __init__(self, nn, mm, initial_key):
        self.nn = nn
        self.mm = mm
        self.k = 1  # current level
        self.n = 1  # number of genuine keys
        self.m = int(nn[0] * mm[0])  # table size
        self.head = 0
        self.table = [initial_key] * self.m

    def _is_genuine(self, pos):
        """Check if the key at pos is genuine (first in its run)"""
        if pos == self.head:
            return True
        prev_pos = (pos - 1) % self.m
        return self.table[pos] != self.table[prev_pos]

    def _find_position(self, x):
        """Binary search to find the insertion position for x"""
        left, right = 0, self.m - 1
        while left <= right:
            mid = (left + right) // 2
            actual_pos = (self.head + mid) % self.m
            mid_val = self.table[actual_pos]

            if mid_val < x:
                left = mid + 1
            elif mid_val > x:
                right = mid - 1
            else:
                # Found the value, need to find first occurrence
                while mid > 0 and self.table[(self.head + mid - 1) % self.m] == x:
                    mid -= 1
                return (self.head + mid) % self.m
        return (self.head + left) % self.m

    def _count_genuine_keys(self):
        """Count the number of genuine keys in the table"""
        count = 0
        for i in range(self.m):
            if self._is_genuine(i):
                count += 1
        return count

    def _rebuild_table(self, new_k):
        """Rebuild the table with new level k"""
        # Collect all genuine keys
        genuine_keys = []
        for i in range(self.m):
            if self._is_genuine(i):
                genuine_keys.append(self.table[i])
        genuine_keys.sort()

        # Update parameters
        self.k = new_k
        self.n = len(genuine_keys)
        self.m = int(self.nn[self.k - 1] * self.mm[self.k - 1])
        self.head = 0
        self.table = [None] * self.m

        # Distribute keys evenly
        if self.n == 0:
            return

        q = self.m // self.n
        r = self.m % self.n

        pos = 0
        for i in range(self.n):
            # Place genuine key
            self.table[pos] = genuine_keys[i]

            # Determine interval size
            interval_size = q + 1 if i < r else q

            # Fill dummy keys (equal to next genuine key)
            fill_value = genuine_keys[i + 1] if i < self.n - 1 else genuine_keys[-1]
            for j in range(1, interval_size):
                next_pos = (pos + j) % self.m
                self.table[next_pos] = fill_value

            pos = (pos + interval_size) % self.m

    def insert(self, x):
        """Insert a key into the table"""
        # Check if we need to rebuild
        if self.n >= self.nn[self.k - 1] and self.k < len(self.nn):
            self._rebuild_table(self.k + 1)

        pos = self._find_position(x)

        # Case 1: Inserting at a dummy key position
        if not self._is_genuine(pos):
            self.table[pos] = x
            self.n += 1
            return

        # Case 2: Need to shift genuine keys
        # Find the end of the genuine keys run
        end_pos = pos
        while True:
            next_pos = (end_pos + 1) % self.m
            if next_pos == self.head or not self._is_genuine(next_pos):
                break
            end_pos = next_pos

        # Shift all genuine keys from pos to end_pos one position right
        current = end_pos
        while current != pos:
            prev = (current - 1) % self.m
            self.table[current] = self.table[prev]
            current = prev

        # Insert the new key
        self.table[pos] = x
        self.n += 1

        # Update head if necessary
        if pos <= self.head <= end_pos:
            self.head = (self.head + 1) % self.m

    def lookup(self, x):
        """Find a key in the table"""
        pos = self._find_position(x)
        if self.table[pos] == x:
            return True, pos
        else:
            return False, pos

    def delete(self, x):
        """Delete a key from the table"""
        # Find the first occurrence of x
        pos = None
        for i in range(self.m):
            actual_pos = (self.head + i) % self.m
            if self.table[actual_pos] == x and self._is_genuine(actual_pos):
                pos = actual_pos
                break

        if pos is None:
            return False

        # Find the length of the dummy run after x
        L = 1
        next_pos = (pos + L) % self.m
        while next_pos != pos and self.table[next_pos] == x:
            L += 1
            next_pos = (pos + L) % self.m

        # The next genuine key
        next_genuine_pos = (pos + L) % self.m
        next_genuine = self.table[next_genuine_pos] if L < self.m else x

        # Replace all positions with next genuine key
        for i in range(L):
            self.table[(pos + i) % self.m] = next_genuine

        self.n -= 1

        # Check if we need to downsize
        if self.k > 1 and self.n <= self.nn[self.k - 2]:
            self._rebuild_table(self.k - 1)

        return True

    def __str__(self):
        """String representation of the table with head marker"""
        elements = []
        for i in range(self.m):
            key = self.table[(self.head + i) % self.m]
            if i == 0:
                elements.append(f">{key}<")
            else:
                elements.append(str(key))
        return f"[{', '.join(elements)}]"


def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python library_sorting.py <json_file>")
        return

    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {sys.argv[1]} not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {sys.argv[1]}")
        return

    nn = data["nn"]
    mm = data["mm"]
    k = data.get("k", 1)  # Default to 1 if not specified
    initial_key = data.get("initial_key", data.get("k", 0))  # Handle both possible field names

    table = SparseTable(nn, mm, initial_key)
    print(f"CREATE with k={k}, n_k={nn}, m_k={mm}, key={initial_key}")
    print(table)

    for action in data["actions"]:
        op = action["action"]
        key = action["key"]

        if op == "insert":
            table.insert(key)
            print(f"INSERT {key}")
            print(table)
        elif op == "delete":
            success = table.delete(key)
            print(f"DELETE {key}")
            print(table)
        elif op == "lookup":
            found, pos = table.lookup(key)
            if found:
                print(f"Key {key} found at position {pos}.")
            else:
                print(f"Key {key} not found. It should be at position {pos}.")
            print(table)


if __name__ == "__main__":
    main()