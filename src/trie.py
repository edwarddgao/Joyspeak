class TrieNode:
    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode("")  # Root node has no character

    def insert(self, word):
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node
        node.is_end_of_word = True

    def is_word(self, word):
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False
        return node.is_end_of_word

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return False
        return True

    # Get next characters with prefix
    def next_chars(self, prefix):
        node = self.root
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return []
        return list(node.children.keys())

    # Get next duplicate chars with prefix
    def next_dup_chars(self, prefix):
        node = self.root
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return []
        return [
            next_char
            for next_char in node.children
            if next_char in node.children[next_char].children
        ]
