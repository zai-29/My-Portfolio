class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_beginning(self, data):
        new_node = Node(data)
        if self.head:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        else:
            self.head = new_node
            self.tail = new_node

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.head:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        else:
            self.tail = new_node
            self.head = new_node

    def search(self, data):
        current_node = self.head
        while current_node:
            if current_node.data == data:
                return True
            current_node = current_node.next
        return False

    def printLinkedList(self):
        current_node = self.head
        while current_node:
            print(current_node.data)
            current_node = current_node.next

    def printBackward(self):
        current_node = self.tail
        while current_node:
            print(current_node.data)
            current_node = current_node.prev

    # remove the FIRST node and return its data (not the Node).
    # If the list is empty, return None.
    def remove_beginning(self):
        if self.head is None:
            return None

        removed_node = self.head
        self.head = self.head.next

        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None

        return removed_node.data

    # remove the LAST node and return its data (not the Node).
    # If the list is empty, return None.
    # No loop needed: the tail already knows the node before it (prev).
    def remove_at_end(self):
        if self.head is None:
            return None

        removed_node = self.tail
        self.tail = self.tail.prev

        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None

        return removed_node.data

    # remove the first node holding `data` and return its data.
    # If no node holds `data`, return None and leave the list unchanged.
    def remove_at(self, data):
        if self.head is None:
            return None

        if self.head.data == data:
            return self.remove_beginning()

        current_node = self.head
        while current_node.next:
            if current_node.next.data == data:
                removed_node = current_node.next
                current_node.next = removed_node.next

                if removed_node == self.tail:
                    self.tail = current_node
                else:
                    removed_node.next.prev = current_node

                return removed_node.data

            current_node = current_node.next

        return None

    # insert a new node holding `data` right after the first node
    # holding `nodedata`. Returns the inserted data.
    # If no node holds `nodedata`, return None and leave the list unchanged.
    def insert_after(self, nodedata, data):
        current_node = self.head
        while current_node:
            if current_node.data == nodedata:
                new_node = Node(data)
                new_node.next = current_node.next
                new_node.prev = current_node

                if current_node == self.tail:
                    self.tail = new_node
                else:
                    current_node.next.prev = new_node

                current_node.next = new_node
                return data

            current_node = current_node.next

        return None

    # ---------- extra methods used by the website ----------
    def __len__(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count

    def to_list(self):
        items = []
        current_node = self.head
        while current_node:
            items.append(current_node.data)
            current_node = current_node.next
        return items

    def to_list_backward(self):
        items = []
        current_node = self.tail
        while current_node:
            items.append(current_node.data)
            current_node = current_node.prev
        return items

    def index_of(self, data):
        index = 0
        current_node = self.head
        while current_node:
            if current_node.data == data:
                return index
            current_node = current_node.next
            index += 1
        return -1

    def insert_at(self, index, data):
        if index < 0 or index > len(self):
            return False

        if index == 0:
            self.insert_at_beginning(data)
        elif index == len(self):
            self.insert_at_end(data)
        else:
            current_node = self.head
            for _ in range(index - 1):
                current_node = current_node.next

            new_node = Node(data)
            new_node.prev = current_node
            new_node.next = current_node.next
            current_node.next.prev = new_node
            current_node.next = new_node

        return True

    def reverse(self):
        current_node = self.head
        while current_node:
            current_node.prev, current_node.next = current_node.next, current_node.prev
            current_node = current_node.prev
        self.head, self.tail = self.tail, self.head

    def clear(self):
        self.head = None
        self.tail = None


if __name__ == "__main__":
    ll = LinkedList()
    for value in [10, 20, 30]:
        ll.insert_at_end(value)
    ll.printLinkedList()