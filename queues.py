from linkedlist import LinkedList


class Queue:
    """First in, first out (FIFO). Items enter at the rear and leave from the front."""

    def __init__(self):
        self.items = LinkedList()

    def enqueue(self, data):
        # add a new node at the rear (the tail of the linked list)
        self.items.insert_at_end(data)

    def dequeue(self):
        # remove the front node (the head) and return its data, None if the queue is empty
        return self.items.remove_beginning()

    def is_empty(self):
        return self.items.head is None

    def clear(self):
        self.items.clear()

    def to_list(self):
        return self.items.to_list()

    def __len__(self):
        return len(self.items)


class Deque:
    """Double-ended queue. Items can be added and removed at BOTH ends."""

    def __init__(self):
        self.items = LinkedList()

    def addFront(self, data):
        # Insert at front
        self.items.insert_at_beginning(data)

    def addRear(self, data):
        # Insert at rear
        self.items.insert_at_end(data)

    def removeFront(self):
        # Delete from front, return its data (None if empty)
        return self.items.remove_beginning()

    def removeRear(self):
        # Delete from rear, return its data (None if empty)
        return self.items.remove_at_end()

    def is_empty(self):
        return self.items.head is None

    def clear(self):
        self.items.clear()

    def to_list(self):
        return self.items.to_list()

    def __len__(self):
        return len(self.items)


if __name__ == "__main__":
    q = Queue()
    for value in ["A", "B", "C"]:
        q.enqueue(value)
    print(q.dequeue(), q.to_list())      # A ['B', 'C']

    d = Deque()
    d.addRear("B")
    d.addFront("A")
    d.addRear("C")
    print(d.removeRear(), d.removeFront(), d.to_list())   # C A ['B']