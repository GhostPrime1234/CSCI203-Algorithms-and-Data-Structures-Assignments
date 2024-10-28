import sys
import numpy as np


def string_hash(word: str, size: int) -> int:
    """Compute a hash index for the given word based on the table size."""
    hash_value = 0
    prime = 31  # A small prime number
    for char in word:
        hash_value = (hash_value * prime + ord(char)) % size
    return hash_value


class HashNode:
    def __init__(self, value=None):
        self.value = value
        self.count = 0 if value is None else 1
        self.next = None

    def increment(self):
        self.count += 1


# HashTable class to manage word counts using a hash table
class HashTable:
    def __init__(self, size: int = 50000):
        self.size = size
        self.table = np.array([HashNode() for _ in range(size)], dtype=np.object_)
        self.empty_count = size
        self.longest_chain = 0

    def table_insert(self, word: str):
        hash_index = string_hash(word, self.size)
        node = self.table[hash_index]

        if node.value is None:
            node.value = word
            node.increment()
            self.empty_count -= 1
        else:
            self.chain_insert(word, node)

    def chain_insert(self, word: str, node: HashNode):
        current_node = node
        chain_length = 0

        while current_node is not None:
            if current_node.value == word:
                current_node.increment()
                return
            chain_length += 1
            if current_node.next is None:
                break
            current_node = current_node.next

        current_node.next = HashNode(word)
        self.longest_chain = max(self.longest_chain, chain_length + 1)

    def get_word_counts(self) -> list:
        word_counts = []
        for node in self.table:
            current_node = node
            while current_node is not None:
                if current_node.value is not None:
                    word_counts.append((current_node.value, current_node.count))
                current_node = current_node.next
        return word_counts


# Stack class to manage words in a stack-like data structure
class Stack:
    def __init__(self):
        self.stack = []  # Initialise an empty list to represent the stack
        self.top: int = -1  # Index of the top element, -1 indicates an empty stack
        self.STACK_SIZE: int = 50000  # Maximum size of the stack

    def push(self, word):
        """Push a word onto the stack if there's space."""
        if self.top < self.STACK_SIZE - 1:
            self.stack.append(word)  # Add the word to the stack
            self.top += 1
        else:
            raise OverflowError("Stack is full")

    def pop(self):
        """Pop a word from the stack if it's not empty."""
        if self.top >= 0:
            stack_item = self.stack[self.top]  # Get the top element
            del self.stack[self.top]
            self.top -= 1  # Update the top index
            return stack_item  # Return the removed element
        else:
            raise IndexError("Stack is empty")  # Notify if the stack is empty

    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return self.top == -1  # Return True if the stack is empty.


def compare(item1, item2) -> int:
    """Compare two (word, count) tuples first by count, then by word."""
    if item1[1] != item2[1]:  # Compare frequencies
        return item1[1] - item2[1]  # Return difference in counts
    else:
        # Ensure we are comparing valid (word, count) pairs
        if item1[0] is None and item2[0] is None:
            return 0
        elif item1[0] is None:
            return -1
        elif item2[0] is None:
            return 1
        else:
            return (item2[0] > item1[0]) - (item2[0] < item1[0])  # Compare words alphabetically


def alphabetical_compare(item1, item2) -> int:
    """Compare two words alphabetically."""
    if item1 < item2:  # Compare words alphabetically
        return -1  # Item1 comes first alphabetically
    elif item1 > item2:
        return 1  # item1 comes later alphabetically
    else:
        return 0  # Both words are identical


# Heapsort functions
def siftdown(arr, start, end, m_compare):
    """Restore the heap property starting from index `start` and ending at index `end`."""
    root = start
    while True:
        child = 2 * root + 1  # Calculate Left child index

        if child > end:  # If child is out of bounds, stop
            break
        # Check if right child exists and is smaller

        if child + 1 <= end and m_compare(arr[child], arr[child + 1]) > 0:
            child += 1  # Point to the smaller child

        # If root is greater than the smaller child
        if m_compare(arr[root], arr[child]) > 0:
            arr[root], arr[child] = arr[child], arr[root]  # Swap root and child
            root = child  # Move down to the child node
        else:
            break


def makeheap(arr, m_compare):
    """Build a heap from an unsorted list."""
    length = len(arr)  # Get the number of elements in the array
    start = (length - 2) // 2  # Last parent node
    while start >= 0:
        siftdown(arr, start, length - 1, m_compare)  # Restore heap property
        start -= 1  # Move to the previous parent node


def heapsort(arr, m_compare):
    """Sort the list using heapsort algorithm."""
    makeheap(arr, m_compare)  # Build the initial heap
    end = len(arr) - 1  # Start with the last parent node
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]  # Move the largest element to the end
        end -= 1
        siftdown(arr, 0, end, m_compare)  # Restore the heap property


def process_file():
    """Process the file to count words, sort them and display results"""
    print("Please enter the name of the text file: ", end="", file=sys.stderr)
    filename = sys.stdin.readline().rstrip("\n")

    # Dictionary to store word counts
    hash_table = HashTable(size=50000)

    ascii_letters = 'abcdefghijklmnopqrstuvwxyz'

    try:
        # Reading file line by line
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.lower()
                line_words = line.split()

                for word in line_words:
                    word = ''.join(char for char in word if char in ascii_letters)
                    if word:
                        hash_table.table_insert(word)

    except FileNotFoundError:
        print(f"Error: The file {filename} is not found.", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"Error: The file {filename} is not UTF-8 encoded.", file=sys.stderr)

    word_count_pairs = hash_table.get_word_counts()
    heapsort(word_count_pairs, compare)

    print("Top 10 words by frequency:")
    for word, count in word_count_pairs[:10]:
        print(f"The word: {word} occurs {count} times.", end="\n")

    last_10_words = sorted(
        [(word, count) for word, count in word_count_pairs if count in [pair[1] for pair in word_count_pairs[-10:]]],
        key=lambda x: (x[1], x[0]),
        reverse=True
    )[-10:]

    print("\nLast 10 words sorted alphabetically within frequency:")
    for word, count in last_10_words:
        print(f"The word: {word} occurs {count} times.")

    unique_words_list = [(word, 1) for word, count in word_count_pairs if count == 1]
    heapsort(unique_words_list, alphabetical_compare)

    try:
        unique_words = Stack()
        for word, count in unique_words_list:
            unique_words.push((word, count))

        print("\nUnique words sorted alphabetically:")
        while not unique_words.is_empty():
            word = unique_words.pop()
            print(f"The word: {word[0]} occurs {word[1]} time.")
    except (IndexError, OverflowError) as error:
        print(error)


if __name__ == '__main__':
    sys.exit(process_file())
