class Stack:  # Last in - first out LIFO
    def __init__(self):
        self.items = []

    @property
    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def pop_pos(self, pos: int):
        return self.items.pop(pos)

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Queue:  # First in - first out FIFO
    def __init__(self):
        self.items = []

    @property
    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def is_element(self, item):
        return item in self.items

    def size(self):
        return len(self.items)