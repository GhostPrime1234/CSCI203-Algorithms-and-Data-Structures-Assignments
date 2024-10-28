#include <iostream>
#include <fstream>

#include <cctype>

//#include <cstring>

using namespace std;

const int POOL_SIZE = 500000;
const int MAX_WORD_COUNT = 50000;
char pool[POOL_SIZE];
int wordStart[MAX_WORD_COUNT];
int wordEnd[MAX_WORD_COUNT];
int wordCount[MAX_WORD_COUNT];

int treeLeft[MAX_WORD_COUNT] = {0};
int treeRight[MAX_WORD_COUNT] = {0};
int treeHeight[MAX_WORD_COUNT] = {-1};
int numChars = 0;
int numWords = 0;
int root = 0;

int AVLinsert(int, char[], int);

int compareWord(int, char[], int);

int rotate_right(int);

int rotate_left(int);

int double_right(int);

int double_left(int);

void inOrder(int);

void mergeSort(int, int);

void merge(int, int, int, int);

void printWord(int);

int main() {

    char filename[20];
    ifstream fin;

    const int WORD_SIZE = 100;
    char word[WORD_SIZE];

    cerr << "Please enter the name of the input file: ";
    cin >> filename;
    fin.open(filename);

    if (!fin) {
        cerr << "Error opening file " << filename << ". Program will exit." << endl;
        return 0;
    }

    int wordLen = 0;
    char inChar;
    while (fin) {
        fin.get(inChar);

        if (isalpha(inChar)) {
            word[++wordLen] = tolower(inChar);
        } else if (isspace(inChar)) {
            if (wordLen > 0) {
                root = AVLinsert(root, word, wordLen);
                wordLen = 0;
            }
        }

    }

    inOrder(root);
    mergeSort(1, numWords);

    cout << endl;

    cout << "The first 10 words sorted alphabetically within frequency:" << endl;
    for (int i = 1; i <= 10; i++) printWord(i);
    cout << endl;

    cout << "The last 10 words sorted alphabetically within frequency:" << endl;
    for (int i = numWords - 9; i <= numWords; i++) printWord(i);



    fin.close();

    return 0;
}

int AVLinsert(int node, char word[], int length) {

    if (node == 0) {

        node = ++numWords;
        wordStart[node] = numChars + 1;
        wordEnd[node] = numChars + length;
        wordCount[node] = 1;
        treeLeft[node] = 0;
        treeRight[node] = 0;
        treeHeight[node] = 0;

        for (int i = 1; i <= length; i++) pool[numChars + i] = word[i];

        numChars += length;

        return node;
    }

    int test = compareWord(node, word, length);

    if (test < 0) {
        treeLeft[node] = AVLinsert(treeLeft[node], word, length);

        if ((treeHeight[treeLeft[node]] - treeHeight[treeRight[node]]) == 2) {
            int test = compareWord(treeLeft[node], word, length);
            if (test < 0) node = rotate_right(node);
            else node = double_right(node);
        }

    } else if (test > 0) {
        treeRight[node] = AVLinsert(treeRight[node], word, length);

        if ((treeHeight[treeRight[node]] - treeHeight[treeLeft[node]]) == 2) {
            int test = compareWord(treeRight[node], word, length);
            if (test < 0) node = double_left(node);
            else node = rotate_left(node);
        }

    } else {
        wordCount[node]++;
    }

    treeHeight[node] = max(treeHeight[treeLeft[node]], treeHeight[treeRight[node]]) + 1;

    return node;
}

int compareWord(int current, char word[], int length) {

    int clen = wordEnd[current] - wordStart[current] + 1;
    int shorter = min(clen, length);
    int offset = wordStart[current] - 1;

    for (int i = 1; i <= shorter; i++)
        if (word[i] < pool[offset + i]) return -1;
        else if (word[i] > pool[offset + i]) return 1;

    if (clen > length) return -1;
    else if (clen < length) return 1;

    return 0;
}

int rotate_right(int node) {
    int k1 = treeLeft[node];    // set k1 to the index of the currrent node’s left child

    treeLeft[node] = treeRight[k1];    // move the right child of k1 to be the left child of node
    treeRight[k1] = node;    // now attach the old root as the right child of k1

    treeHeight[node] = max(treeHeight[treeLeft[node]], treeHeight[treeRight[node]]) + 1;
    treeHeight[k1] = max(treeHeight[treeLeft[k1]], treeHeight[treeRight[k1]]) + 1;

    return k1;    // link the left child back up the tree.
}

int rotate_left(int node) {

    int k1 = treeRight[node];

    treeRight[node] = treeLeft[k1];
    treeLeft[k1] = node;

    treeHeight[node] = max(treeHeight[treeLeft[node]], treeHeight[treeRight[node]]) + 1;
    treeHeight[k1] = max(treeHeight[treeLeft[k1]], treeHeight[treeRight[k1]]) + 1;

    return k1;
}

int double_right(int node) {

    treeLeft[node] = rotate_left(treeLeft[node]);
    node = rotate_right(node);

    return node;
}

int double_left(int node) {

    treeRight[node] = rotate_right(treeRight[node]);
    node = rotate_left(node);

    return node;
}

void inOrder(int node) {

    static int index = 0;

    if (node == 0) return;

    inOrder(treeLeft[node]);
    treeHeight[++index] = node;
    inOrder(treeRight[node]);
}

void mergeSort(int left, int right) {

    if (left < right) {
        int mid = (left + right) / 2;
        mergeSort(left, mid);
        mergeSort(mid + 1, right);
        merge(left, mid, mid + 1, right);
    }
}

void merge(int l1, int l2, int r1, int r2) {

    int apos = l1;
    int bpos = r1;
    int cpos = l1;

    while (apos <= l2 && bpos <= r2)
        if (wordCount[treeHeight[apos]] >= wordCount[treeHeight[bpos]])
            treeLeft[cpos++] = treeHeight[apos++];
        else treeLeft[cpos++] = treeHeight[bpos++];

    while (apos <= l2) treeLeft[cpos++] = treeHeight[apos++];

    while (bpos <= r2) treeLeft[cpos++] = treeHeight[bpos++];

    for (cpos = l1; cpos <= r2; cpos++) treeHeight[cpos] = treeLeft[cpos];
}

void printWord(int word) {

    word = treeHeight[word];

    cout << "The word: ";
    for (int i = wordStart[word]; i <= wordEnd[word]; i++) cout << pool[i];

    cout << " occurs ";
    cout << wordCount[word] << " times." << endl;
}
