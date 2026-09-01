class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]

    def __hash_function(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self.__hash_function(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))

    def get(self, key):
        index = self.__hash_function(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None

    def remove(self, key):
        index = self.__hash_function(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                del self.table[index][i]
                return True
        return False

    def __str__(self):
        return str(self.table)
    


def tests():
    ht = HashTable()
    ht.insert("apple", 1)
    ht.insert("banana", 2)
    ht.insert("orange", 3)

    assert ht.get("apple") == 1
    assert ht.get("banana") == 2
    assert ht.get("orange") == 3
    assert ht.get("grape") is None

    ht.insert("apple", 10)
    assert ht.get("apple") == 10

    assert ht.remove("banana") is True
    assert ht.get("banana") is None
    assert ht.remove("banana") is False

    print("All tests passed!")


tests()

    