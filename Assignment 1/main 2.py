# ---------------------- imports

import sys

import numpy as np

# ---------------------- string pool


class StringPool:

    pool_size = 500000
    max_word_count = 50000

    num_chars = 0 # current index

    def __init__(self):

        self.pool = np.zeros(self.pool_size, np.object_)
        self.word_start = np.zeros(self.max_word_count, int)
        self.word_end = np.zeros(self.max_word_count, int)
        self.word_count = np.zeros(self.max_word_count, int)

        return

    def add_string_to_pool(self, node, word, word_length):

        self.word_start[node] = self.num_chars + 1
        self.word_end[node] = self.num_chars + word_length
        self.word_count[node] = 1

        for i in range(word_length):  # i in [0, word_length - 1]
            self.pool[self.num_chars + i + 1] = word[i]

        self.num_chars += word_length

        return

    def increment_word_count(self, k):

        self.word_count[k] += 1

        return

    def compare_word(self, current, word, word_length):  # item 20 in guide

        clen = self.word_end[current] - self.word_start[current] + 1
        shorter = min(clen, word_length)
        offset = self.word_start[current] - 1

        for i in range(1, shorter+1):
            if word[i-1] < self.pool[offset + i]:
                return -1
            else:
                if word[i-1] > self.pool[offset + i]:
                    return 1

        if clen > word_length:
            return -1
        else:
            if clen < word_length:
                return 1

        return 0

    def get_word(self, i):

        return "".join([self.pool[j] for j in range(self.word_start[i], self.word_end[i]+1)])

    def get_word_count(self, i):

        return self.word_count[i]

    def print_pool(self):

        for i in range(0, self.max_word_count):
            if self.word_count[i] != 0:
                word = "".join([self.pool[j] for j in range(self.word_start[i], self.word_end[i]+1)])
                print(self.word_start[i], self.word_end[i], self.word_count[i], word)

        return


class AVLTree:

    max_word_count = 50000

    num_words = 0
    root = 0

    index = 0

    def __init__(self, sp):

        self.tree_left = np.zeros(self.max_word_count, int)
        self.tree_right = np.zeros(self.max_word_count, int)

        self.tree_height = np.empty(self.max_word_count, int)
        for i in range(self.max_word_count):
            self.tree_height[i] = -1

        self.sp = sp

        return

    def AVL_insert(self, word, word_length):  # public method

        self.root = self.__AVL_insert(self.root, word, word_length)

        return

    def __AVL_insert(self, node, word, word_length):  # private method prefixed by __

        if node == 0:
            # Add a word to the tree 16
            self.num_words += 1
            node = self.num_words

            self.sp.add_string_to_pool(node, word, word_length)

            self.tree_left[node] = 0
            self.tree_right[node] = 0
            self.tree_height[node] = 0

            return node

        test = self.sp.compare_word(node, word, word_length)

        if test < 0:
            self.tree_left[node] = self.__AVL_insert(self.tree_left[node], word, word_length)

            # Left insertion balance check 17
            if self.tree_height[self.tree_left[node]] - self.tree_height[self.tree_right[node]] == 2:
                test = self.sp.compare_word(self.tree_left[node], word, word_length)
                if test < 0:
                    node = self.__rotate_right(node)
                else:
                    node = self.__double_right(node)

        elif test > 0:
            self.tree_right[node] = self.__AVL_insert(self.tree_right[node], word, word_length)

            # Right insertion balance check 18
            if self.tree_height[self.tree_right[node]] - self.tree_height[self.tree_left[node]] == 2:
                test = self.sp.compare_word(self.tree_right[node], word, word_length)
                if test < 0:
                    node = self.__double_left(node)
                else:
                    node = self.__rotate_left(node)

        else:
            self.sp.increment_word_count(node)

        self.tree_height[node] = max(self.tree_height[self.tree_left[node]], self.tree_height[self.tree_right[node]]) + 1

        return node

    def __rotate_right(self, node):  # item 22 in guide

        k1 = self.tree_left[node]
        self.tree_left[node] = self.tree_right[k1]
        self.tree_right[k1] = node
        self.tree_height[node] = max(self.tree_height[self.tree_left[node]], self.tree_height[self.tree_right[node]]) + 1
        self.tree_height[k1] = max(self.tree_height[self.tree_left[k1]], self.tree_height[self.tree_right[k1]]) + 1

        return k1

    def __double_right(self, node):  # item 24 in guide

        self.tree_left[node] = self.__rotate_left(self.tree_left[node])
        node = self.__rotate_right(node)

        return node

    def __rotate_left(self, node):  # item 22 in guide

        k1 = self.tree_right[node]
        self.tree_right[node] = self.tree_left[k1]
        self.tree_left[k1] = node

        self.tree_height[node] = max(self.tree_height[self.tree_left[node]], self.tree_height[self.tree_right[node]]) + 1
        self.tree_height[k1] = max(self.tree_height[self.tree_left[k1]], self.tree_height[self.tree_right[k1]]) + 1

        return k1

    def __double_left(self, node):  # item 24 in guide

        self.tree_right[node] = self.__rotate_right(self.tree_right[node])
        node = self.__rotate_left(node)

        return node

    def in_order(self):

        self.index = 0
        self.__in_order(self.root)

        return

    def __in_order(self, node):

        if node == 0:
            return

        self.__in_order(self.tree_left[node])

        self.index += 1
        self.tree_height[self.index] = node

        self.__in_order(self.tree_right[node])

        return

    def merge_sort(self):

        self.__merge_sort(1, self.num_words)

        return

    def __merge_sort(self, left, right):

        if left < right:
            mid = (left + right) // 2
            self.__merge_sort(left, mid)
            self.__merge_sort(mid + 1, right)
            self.__merge(left, mid, mid + 1, right)

        return

    def __merge(self, l1, l2, r1, r2):

        apos = l1
        bpos = r1
        cpos = l1

        while (apos <= l2) and (bpos <= r2):
            if self.sp.get_word_count(self.tree_height[apos]) >= self.sp.get_word_count(self.tree_height[bpos]):
                self.tree_left[cpos] = self.tree_height[apos]
                cpos += 1
                apos += 1
            else:
                self.tree_left[cpos] = self.tree_height[bpos]
                cpos += 1
                bpos += 1

        while apos <= l2:
            self.tree_left[cpos] = self.tree_height[apos]
            cpos += 1
            apos += 1

        while bpos <= r2:
            self.tree_left[cpos] = self.tree_height[bpos]
            cpos += 1
            bpos += 1

        for cpos in range(l1, r2+1):
            self.tree_height[cpos] = self.tree_left[cpos]

        return

    def print_tree(self):

        for i in range(1, self.num_words+1):
            if self.tree_height[i] != -1:
                print(self.sp.get_word(self.tree_height[i]), self.sp.get_word_count(self.tree_height[i]))

        return

    def print_top_ten(self):

        print("The first 10 words sorted alphabetically within frequency:")
        for i in range(1, 10+1):
            print("The word:", self.sp.get_word(self.tree_height[i]), "occurs", self.sp.get_word_count(self.tree_height[i]), "times.")

        return

    def print_unique(self):

        print("The unique words sorted alphabetically:")
        for i in range(1, self.num_words+1):
            if self.sp.get_word_count(self.tree_height[i]) == 1:
                print("The word:", self.sp.get_word(self.tree_height[i]), "occurs", self.sp.get_word_count(self.tree_height[i]), "times.")

        return

    def print_last_ten(self):

        print("The last 10 words sorted alphabetically within frequency:")
        for i in range(self.num_words-9, self.num_words+1):
            print("The word:", self.sp.get_word(self.tree_height[i]), "occurs", self.sp.get_word_count(self.tree_height[i]), "times.")

        return


# ---------------------- word functions

def process_word(word):

    pw = ''
    for letter in word:
        if letter.isalpha():
            pw += letter.lower()

    return pw


# ---------------------- main

def main():

    sp = StringPool()
    avl = AVLTree(sp)

    print("Please enter the name of the input file:", file=sys.stderr)
    filename = sys.stdin.readline()
    filename = filename.rstrip("\n")

    try:
        f = open(filename, "r", encoding="utf-8")
    except OSError as exception:
        print("Error opening file ", filename, ". Program will exit.", sep="")
        return

    # process the words in the input text
    for line in f:
        words = line.split()  # does last word have "\n" at end

        if len(words) > 0:  # not a blank line
            
            for w in words:
                pw = process_word(w)  # may result in no word e.g. contained no alpha characters

                if len(pw) > 0:
                    avl.AVL_insert(pw, len(pw))

    avl.in_order()

    avl.merge_sort()

    # print output
    print()
    avl.print_top_ten()

    print()
    avl.print_last_ten()

    print()
    avl.print_unique()

    return


# ---------------------- execute main

if __name__ == '__main__':
    sys.exit(main())
