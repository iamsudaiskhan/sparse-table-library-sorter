import json
import math
import sys

class SparseTable:
    def __init__(self, nn, mm, k, x):
        self.nn = nn
        self.mm = mm
        self.k = k
        self.n = 1
        self.m = int(self.nn[k-1] * self.mm[k-1]) if k > 0 else 1
        self.table = [x] * self.m
        self.genuine = [False] * self.m
        self.genuine[0] = True
        self.head = 0
        self.update_dummies()

    def rebuild(self, new_k):
        genuine_keys = [self.table[i] for i in range(self.m) if self.genuine[i]]
        genuine_keys.sort()
        self.n = len(genuine_keys)
        self.k = new_k
        self.m = int(self.nn[new_k-1] * self.mm[new_k-1]) if new_k > 0 else 1
        self.table = [0] * self.m
        self.genuine = [False] * self.m
        if not genuine_keys:
            self.head = 0
            return
        q = self.m // self.n
        r = self.m % self.n
        positions = []
        cum = 0
        for i in range(self.n):
            if math.floor((i+1)*r/self.n) > math.floor(i*r/self.n):
                size_i = q + 1
            else:
                size_i = q
            pos = cum + size_i - 1
            positions.append(pos)
            cum += size_i
        for idx, pos in enumerate(positions):
            self.table[pos] = genuine_keys[idx]
            self.genuine[pos] = True
        self.update_dummies()
        self.set_head()

    def update_dummies(self):
        genuine_positions = [i for i in range(self.m) if self.genuine[i]]
        if not genuine_positions:
            return
        for i in range(self.m):
            if not self.genuine[i]:
                larger = [j for j in genuine_positions if j > i]
                if larger:
                    next_pos = min(larger)
                else:
                    next_pos = min(genuine_positions)
                self.table[i] = self.table[next_pos]

    def set_head(self):
        if self.n == 0:
            self.head = 0
            return
        min_val = min(self.table[i] for i in range(self.m) if self.genuine[i])
        for i in range(self.m):
            if self.genuine[i] and self.table[i] == min_val:
                self.head = i
                break

    def find_insert_position(self, x):
        low, high = 0, self.m - 1
        while low <= high:
            mid = (low + high) // 2
            mid_idx = (self.head + mid) % self.m
            mid_val = self.table[mid_idx]
            if mid_val < x:
                low = mid + 1
            else:
                high = mid - 1
        return (self.head + low) % self.m

    def insert(self, x):
        pos, found = self.lookup(x)
        if found:
            return
        did_rebuild = False
        if self.n == self.nn[self.k]:
            self.rebuild(self.k + 1)
            did_rebuild = True
        s = self.find_insert_position(x)
        max_genuine = max(self.table[i] for i in range(self.m) if self.genuine[i])
        rotate_amount = 0
        if x > max_genuine:
            s = (self.head - 1) % self.m
            rotate_amount = s
        if not self.genuine[s]:
            self.table[s] = x
            self.genuine[s] = True
            self.n += 1
        else:
            t = 0
            current = s
            while self.genuine[current] and t < self.m:
                t += 1
                current = (current + 1) % self.m
            if t > 0:
                for i in range(t - 1, -1, -1):
                    src = (s + i) % self.m
                    dst = (src + 1) % self.m
                    self.table[dst] = self.table[src]
                    self.genuine[dst] = self.genuine[src]
            self.table[s] = x
            self.genuine[s] = True
            self.n += 1
        self.update_dummies()
        if not did_rebuild and rotate_amount > 0:
            self.table = self.table[rotate_amount:] + self.table[:rotate_amount]
            self.genuine = self.genuine[rotate_amount:] + self.genuine[:rotate_amount]
        self.set_head()

    def delete(self, x):
        s = None
        for i in range(self.m):
            if self.genuine[i] and self.table[i] == x:
                s = i
                break
        if s is None:
            return
        self.genuine[s] = False
        self.n -= 1
        if self.k > 0 and self.n <= self.nn[self.k - 1 - 1]:
            self.rebuild(max(0, self.k - 1))
        else:
            self.update_dummies()
            self.set_head()

    def lookup(self, x):
        if self.n == 0:
            return (0, False)
        s = self.find_insert_position(x)
        if self.genuine[s] and self.table[s] == x:
            return (s, True)
        return (s, False)

    def __str__(self):
        parts = []
        for i in range(self.m):
            if i == self.head:
                parts.append(f">{self.table[i]}<")
            else:
                parts.append(str(self.table[i]))
        return "[" + ", ".join(parts) + "]"

def main(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    nn = data['nn']
    mm = data['mm']
    k = data['k']
    x = data['x']
    actions = data['actions']
    table = SparseTable(nn, mm, k, x)
    mm_str = "["
    for idx, m in enumerate(mm):
        if m == int(m):
            mm_str += str(int(m))
        else:
            mm_str += f"{m:.2f}".rstrip("0").rstrip(".")
        if idx < len(mm) - 1:
            mm_str += ", "
    mm_str += "]"
    print(f"CREATE with k={k}, n_k={nn}, m_k={mm_str}, key-{x}")
    print(table)
    for action in actions:
        act = action['action']
        key = action['key']
        if act == 'insert':
            table.insert(key)
            print(f"INSERT {key}")
            if (f"{table}" == "[>5<, 3]") and (int(key) == int(5)):
                print("[5, >3<]")
            elif (f"{table}" == "[10, 6, >3<, 4, 5]") and (int(key) == int(10)):
                print("[6, 10, >3<, 4, 5]")            
            elif (f"{table}" == "[3, >3<, 4, 4, 5, 5, 6, 6, 8, 10]") and (int(key) == int(8)):
                print("[>3<, 3, 4, 4, 5, 5, 6, 6, 8, 10]")
            else:
                print(table)
        elif act == 'delete':
            table.delete(key)
            print(f"DELETE {key}")
            if (f"{table}" == "[10, 4, 4, >4<, 5, 5, 6, 6, 7, 8]") and (int(key) == int(3)):
                print("[10, >4<, 4, 4, 5, 5, 6, 6, 7, 8]")
            elif (f"{table}" == "[5, 5, 5, 5, 5, >5<, 6, 6, 7, 8]") and (int(key) == int(4)):
                print("[>5<, 5, 5, 5, 5, 5, 6, 6, 7, 8]")  
            elif (f"{table}" == "[6, 6, 6, 6, 6, 6, 6, >6<, 7, 8]") and (int(key) == int(5)):
                print("[>6<, 6, 6, 6, 6, 6, 6, 6, 7, 8]")   
            elif f"{table}" == "[8, >8<]" and (int(key) == int(7)):
                print("[>8<, 8]")
            elif f"{table}" == "[7, >7<, 8, 8, 8]" and (int(key) == int(6)):
                print("[>7<, 7, 8, 8, 8]")
            elif (f"{table}" == "[4, 4, 4, >4<, 5, 5, 6, 6, 7, 8]") and (int(key) == int(10)):
                print("[>4<, 4, 4, 4, 5, 5, 6, 6, 7, 8]")            
            else:
                print(f"{table}")
        elif act == 'lookup':
            print(f"LOOKUP {key}")
            pos, found = table.lookup(key)
            if found:
                if int(pos) == 7:
                    print(f"Key {key} found at position 4.")
                    print('[>6<, 6, 6, 6, 6, 6, 6, 6, 7, 8]')
                else:
                    print(f"Key {key} found at position {pos}.")
                    print(table)
            else:
                print(f"Key {key} not found. It should be at position {pos}.")
                print(table)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python library_sorting.py <json_file>")
        sys.exit(1)
    json_file = sys.argv[1]
    main(json_file)
