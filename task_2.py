from trie import Trie


class Homework(Trie):

    def __init__(self):
        super().__init__()
        self.suffix_trie = Trie()

    def put(self, key, value=None):
        super().put(key, value)
        reversed_key = key[::-1]
        self.suffix_trie.put(reversed_key, value)

    def count_words_with_suffix(self, pattern) -> int:
        reversed_pattern = pattern[::-1]
        return len(self.suffix_trie.keys_with_prefix(reversed_pattern))

    def has_prefix(self, prefix) -> bool:
        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        return True


if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    # Перевірка кількості слів, що закінчуються на заданий суфікс
    assert trie.count_words_with_suffix("e") == 1  # apple
    assert trie.count_words_with_suffix("ion") == 1  # application
    assert trie.count_words_with_suffix("a") == 1  # banana
    assert trie.count_words_with_suffix("at") == 1  # cat

    # Перевірка наявності префікса
    assert trie.has_prefix("app") == True  # apple, application
    assert trie.has_prefix("bat") == False
    assert trie.has_prefix("ban") == True  # banana
    assert trie.has_prefix("ca") == True  # cat
