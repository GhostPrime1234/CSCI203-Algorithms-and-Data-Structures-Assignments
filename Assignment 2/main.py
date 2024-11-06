class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * self.size

    def _hash(self, key):
        return key % self.size

    def _probe(self, hashed_key):
        original_hashed_key = hashed_key
        while self.table[hashed_key] is not None and self.table[hashed_key][0] is not None:
            hashed_key = (hashed_key + 1) % self.size
            if hashed_key == original_hashed_key:
                raise Exception("Hash table is full")
        return hashed_key

    def insert(self, key, value):
        hashed_key = self._hash(key)
        if self.table[hashed_key] is None:
            self.table[hashed_key] = (key, value)
        else:
            hashed_key = self._probe(hashed_key)
            self.table[hashed_key] = (key, value)

    def get(self, key):
        hashed_key = self._hash(key)
        probing_attempts = 0
        while probing_attempts < self.size:
            if self.table[hashed_key] is None:
                return None
            elif self.table[hashed_key][0] == key:
                return self.table[hashed_key][1]
            hashed_key = (hashed_key + 1) % self.size
            probing_attempts += 1
        return None

    def update(self, key, value):
        hashed_key = self._hash(key)
        probing_attempts = 0
        while probing_attempts < self.size:
            if self.table[hashed_key] is None:
                return False
            elif self.table[hashed_key][0] == key:
                self.table[hashed_key] = (key, value)
                return True
            hashed_key = (hashed_key + 1) % self.size
            probing_attempts += 1
        return False

    def keys(self):
        return [entry[0] for entry in self.table if entry is not None]

class Customer:
    def __init__(self, arrival_time, service_time, priority):
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.priority = priority

    def __lt__(self, other):
        # Prioritise based on arrival time if same priority
        if self.priority == other.priority:
            return self.arrival_time < other.arrival_time
        # Prioritise higher-priority customers
        return self.priority > other.priority

class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def insert(self, element):
        self.heap.append(element)
        self._heapify_up(self._get_length(self.heap) - 1)

    def _heapify_up(self, index):
        while index != 0 and self.heap[self.parent(index)] > self.heap[index]:
            self.heap[index], self.heap[self.parent(index)] = self.heap[self.parent(index)], self.heap[index]
            index = self.parent(index)

    def extract_min(self):
        if self._get_length(self.heap) == 0:
            return None
        root = self.heap[0]
        last_element = self.heap.pop()
        if self._get_length(self.heap) > 0:
            self.heap[0] = last_element
            self._heapify_down(0)
        return root

    def _heapify_down(self, index):
        smallest = index
        left = self.left_child(index)
        right = self.right_child(index)

        if left < self._get_length(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left

        if right < self._get_length(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def is_empty(self):
        return self._get_length(self.heap) == 0

    @staticmethod
    def _get_length(lst):
        count = 0
        for _ in lst:
            count += 1
        return count

class Queue:
    def __init__(self):
        self.queue = MinHeap()

    def enqueue(self, customer):
        self.queue.insert(customer)

    def dequeue(self):
        return self.queue.extract_min()

    def is_empty(self):
        return self.queue.is_empty()

class BankSimulation:
    def __init__(self, num_tellers):
        self.num_tellers = num_tellers
        self.tellers = HashTable()
        self.queue = Queue()
        self.time = 0
        self.max_queue_length = 0
        self.total_queue_time = 0
        self.total_idle_time = HashTable()
        self.customers_served = HashTable()
        self.last_busy_time = HashTable()
        self.round_robin_counter = 0  # Round-robin counter to keep track of the starting point

        for i in range(self.num_tellers):
            self.tellers.insert(i, None)
            self.total_idle_time.insert(i, 0)
            self.customers_served.insert(i, 0)
            self.last_busy_time.insert(i, 0)

    def read_file(self, filename):
        customers = []
        with open(filename, 'r') as file:
            for line in file:
                try:
                    arrival_time, service_time, priority = self._parse_line(line.strip())
                    if arrival_time == 0 and service_time == 0:
                        break
                    customers.append(Customer(arrival_time, service_time, priority))
                except ValueError as e:
                    pass
        return customers

    def _parse_line(self, line):
        values = []
        value = ""
        for char in line:
            if char == ' ':
                values.append(float(value))
                value = ""
            else:
                value += char

        values.append(float(value))
        return values

    def run(self, filename):
        customers = self.read_file(filename)
        for customer in customers:
            self.time = customer.arrival_time
            self.allocate_customer(customer)
            self.update_tellers()

        while not self.queue.is_empty():
            self.update_tellers()
            self.time += 1

        self.print_statistics()

    def allocate_customer(self, customer):
        teller_id = self.find_idle_teller()
        if teller_id is not None:
            self.tellers.update(teller_id, (customer, self.time + customer.service_time))
            self.update_customers_served(teller_id)
        else:
            self.queue.enqueue(customer)
            self.update_queue_length()

    def update_tellers(self):
        for i in self.tellers.keys():
            teller_status = self.tellers.get(i)
            if teller_status is not None:
                customer, finish_time = teller_status
                if self.time >= finish_time:
                    # Teller becomes idle
                    self.tellers.update(i, None)
                    # Update idle time for the teller
                    self.update_total_idle_time(i)

                    # Process the next customer in the queue if available
                    if not self.queue.is_empty():
                        next_customer = self.queue.dequeue()
                        self.tellers.update(i, (next_customer, self.time + next_customer.service_time))
                        self.update_customers_served(i)
                    self.last_busy_time.update(i, self.time)  # Update last busy time

    def find_idle_teller(self):
        start_index = self.round_robin_counter
        for index in range(self.num_tellers):
            teller_id = (start_index + index) % self.num_tellers
            if self.tellers.get(teller_id) is None:
                # Update round_robin_counter for next allocation
                self.round_robin_counter = (teller_id + 1) % self.num_tellers
                return teller_id
        return None

    def update_queue_length(self):
        current_length = self._get_queue_length()
        if current_length > self.max_queue_length:
            self.max_queue_length = current_length
        self.total_queue_time += current_length

    def _get_queue_length(self):
        # Implement the manual count instead of len()
        count = 0
        for _ in self.queue.queue.heap:
            count += 1
        return count

    def update_customers_served(self, teller_id):
        served = self.customers_served.get(teller_id)
        self.customers_served.update(teller_id, served + 1)

    def update_total_idle_time(self, teller_id):
        last_busy = self.last_busy_time.get(teller_id)
        if last_busy is not None and self.time > last_busy:
            idle_time = self.total_idle_time.get(teller_id)
            idle_time += (self.time - last_busy)
            self.total_idle_time.update(teller_id, idle_time)

        else:
            # If the teller has not been busy, we cannot calculate idle time correctl
            print(f"Teller {teller_id} not found in total_idle_time or has not been idle")

    def print_statistics(self):
        total_service_time = 0
        total_waiting_time = 0
        num_customers_served = 0

        for index in self.tellers.keys():
            entry = self.tellers.get(index)
            if entry is not None:
                customer, finish_time = entry
                total_service_time += customer.service_time
                waiting_time = finish_time - customer.arrival_time - customer.service_time
                total_waiting_time += waiting_time
                num_customers_served += 1

        avg_service_time_per_customer = (total_service_time / num_customers_served) if num_customers_served > 0 else 0
        avg_waiting_time_per_customer = (total_waiting_time / num_customers_served) if num_customers_served > 0 else 0

        print("Simulation Statistics")
        print("Customers Served by Each Teller")
        for i in self.tellers.keys():
            print(f"Teller [{i}]: {self.customers_served.get(i)}")

        print(f"Total Time of Simulation: {self.time:.2f}")
        print(f"Average Service Time per Customer: {avg_service_time_per_customer:.4f}")
        print(f"Average Waiting Time per Customer: {avg_waiting_time_per_customer:.3f}")
        print(f"Maximum Length of the Queue: {self.max_queue_length}")
        print(f"Average Length of the Queue: {self.total_queue_time / self.time:.4f}")

        print("Average Idle Rate of Each Teller")
        for i in self.tellers.keys():
            idle_time = self.total_idle_time.get(i)
            idle_rate = (idle_time / self.time) if self.time > 0 else 0
            print(f"Teller [{i}]: {idle_rate:.7f}")


if __name__ == "__main__":
    num_tellers_input = int(input("Please enter the number of tellers: "))
    input_file = input("Please enter the name of the input file: ")
    print("Simulation Inputs",
    f"Number of tellers: {num_tellers_input}",
    f"Name of input file: {input_file}", sep="\n", end="\n\n")

    simulation = BankSimulation(num_tellers_input)
    simulation.run(input_file)
