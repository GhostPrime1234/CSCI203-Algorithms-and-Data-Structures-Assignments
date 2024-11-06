#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <chrono>
#include <algorithm>
#include <cctype>
#include <queue>

// Stack Class Implementation
class Stack {
private:
    std::vector<std::string> stack;

public:
    // Push an item onto the stack
    void push(const std::string& word) {
        stack.push_back(word);
    }

    // Pop an item off the stack
    std::string pop() {
        if (stack.empty()) {
            throw std::out_of_range("Stack is empty");
        }
        std::string stack_item = stack.back();
        stack.pop_back();
        return stack_item;
    }

    // Check if the stack is empty
    bool is_empty() const {
        return stack.empty();
    }
};

// Comparator function for sorting word-count pairs
bool compare(const std::pair<std::string, int>& item1, const std::pair<std::string, int>& item2) {
    if (item1.second != item2.second)
        return item1.second > item2.second; // Sort by frequency in descending order
    else
        return item1.first < item2.first; // Sort alphabetically if frequencies are the same
}

// Function to clean and lowercase a word
std::string clean_word(const std::string& word) {
    std::string cleaned;
    for (char ch : word) {
        if (std::isalpha(ch)) {
            cleaned += std::tolower(ch);
        }
    }
    return cleaned;
}

void process_file() {
    std::cout << "Please enter the name of the text file: ";
    std::string filename;
    std::cin >> filename;

    std::unordered_map<std::string, int> word_count;
    std::vector<std::pair<std::string, int>> word_count_pairs;
    std::vector<std::string> unique_words_list;
    Stack unique_words;

    auto start = std::chrono::high_resolution_clock::now();

    try {
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Error: The file " + filename + " is not found.");
        }

        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());

        std::string word;
        for (char& ch : content) {
            if (std::isalpha(ch)) {
                word += std::tolower(ch);
            } else if (!word.empty()) {
                word = clean_word(word);
                word_count[word]++;
                word.clear();
            }
        }
        if (!word.empty()) {
            word = clean_word(word);
            word_count[word]++;
        }
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return;
    }

    // Convert word count map to vector of pairs
    word_count_pairs.reserve(word_count.size());
    for (const auto& pair : word_count) {
        word_count_pairs.push_back(pair);
    }

    // Sort the word-count pairs by frequency and alphabetically
    std::sort(word_count_pairs.begin(), word_count_pairs.end(), compare);

    std::cout << "\nFirst 10 words sorted by frequency and alphabetically:" << std::endl;
    for (size_t i = 0; i < 10 && i < word_count_pairs.size(); i++) {
        std::cout << "The word: " << word_count_pairs[i].first << " occurs " << word_count_pairs[i].second << " times." << std::endl;
    }

    std::cout << "\nLast 10 words sorted by frequency and alphabetically:" << std::endl;
    for (size_t i = (word_count_pairs.size() > 10 ? word_count_pairs.size() - 10 : 0); i < word_count_pairs.size(); i++) {
        std::cout << "The word: " << word_count_pairs[i].first << " occurs " << word_count_pairs[i].second << " times." << std::endl;
    }

    // Collect unique words
    for (const auto& pair : word_count_pairs) {
        if (pair.second == 1) {
            unique_words_list.push_back(pair.first);
        }
    }

    // Sort unique words alphabetically
    std::sort(unique_words_list.begin(), unique_words_list.end());

    for (const auto& word : unique_words_list) {
        unique_words.push(word);
    }

    std::cout << "\nUnique words sorted alphabetically:" << std::endl;
    while (!unique_words.is_empty()) {
        std::cout << "The word: " << unique_words.pop() << " occurs 1 time." << std::endl;
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Processing time: " << elapsed.count() * 1000 << " milliseconds" << std::endl;
}

int main() {
    try {
        process_file();
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
    return 0;
}
