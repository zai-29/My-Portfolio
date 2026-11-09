class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    def __init__(self, value=None):
        self.root = Node(value) if value is not None else None

    # ---------- Adding (from the slides) ----------
    def insert_left(self, current_node, value):
        if current_node.left is None:
            current_node.left = Node(value)
        else:
            new_node = Node(value)
            new_node.left = current_node.left
            current_node.left = new_node

    def insert_right(self, current_node, value):
        if current_node.right is None:
            current_node.right = Node(value)
        else:
            new_node = Node(value)
            new_node.right = current_node.right
            current_node.right = new_node

    # ---------- Adding to a binary SEARCH tree ----------
    # smaller values go to the left, bigger values go to the right
    def insert(self, root, value):
        if root is None:
            return Node(value)
        if value < root.value:
            root.left = self.insert(root.left, value)
        elif value > root.value:
            root.right = self.insert(root.right, value)
        return root

    # ---------- Traversal ----------
    def inorder_traversal(self, start, traversal):
        if start:
            traversal = self.inorder_traversal(start.left, traversal)
            traversal += (str(start.value) + '-')
            traversal = self.inorder_traversal(start.right, traversal)
        return traversal

    def preorder_traversal(self, start, traversal):
        if start:
            traversal += (str(start.value) + " ")
            traversal = self.preorder_traversal(start.left, traversal)
            traversal = self.preorder_traversal(start.right, traversal)
        return traversal

    # LAB: left subtree, right subtree, then the root node
    def post_traversal(self, start, traversal):
        if start:
            traversal = self.post_traversal(start.left, traversal)
            traversal = self.post_traversal(start.right, traversal)
            traversal += (str(start.value) + " ")
        return traversal

    # ---------- Searching ----------
    # LAB: return the node that holds `key`, or None if it is not in the tree.
    # In a binary search tree we only need to go one way at every node.
    def search(self, root, key):
        if root is None or root.value == key:
            return root
        if key < root.value:
            return self.search(root.left, key)
        return self.search(root.right, key)

    # ---------- Deleting ----------
    # the smallest value of a subtree is its left-most node
    def min_value_node(self, node):
        current_node = node
        while current_node.left is not None:
            current_node = current_node.left
        return current_node

    # LAB: remove the node that holds `key` and return the (new) root of this subtree.
    # If `key` is not in the tree, nothing changes.
    def delete_node(self, root, key):
        if root is None:
            return root                              # key not found

        if key < root.value:
            root.left = self.delete_node(root.left, key)
        elif key > root.value:
            root.right = self.delete_node(root.right, key)
        else:
            # this is the node to delete
            if root.left is None:                    # no children, or only a right child
                return root.right
            if root.right is None:                   # only a left child
                return root.left

            # two children: copy the inorder successor (the smallest value
            # in the right subtree) here, then delete that successor
            successor = self.min_value_node(root.right)
            root.value = successor.value
            root.right = self.delete_node(root.right, successor.value)
        return root


if __name__ == "__main__":
    # the tree from the slides (built with insert_left / insert_right)
    tree = BinaryTree("R")
    tree.insert_left(tree.root, "A")
    tree.insert_right(tree.root, "B")
    tree.insert_left(tree.root.left, "C")
    tree.insert_right(tree.root.left, "D")
    tree.insert_left(tree.root.right, "E")
    tree.insert_right(tree.root.right, "F")
    tree.insert_left(tree.root.right.right, "G")
    print(tree.preorder_traversal(tree.root, ""))    # R A C D B E F G
    print(tree.inorder_traversal(tree.root, ""))     # C-A-D-R-E-B-G-F-
    print(tree.post_traversal(tree.root, ""))        # C D A E G F B R

    # a binary search tree of numbers
    bst = BinaryTree()
    for number in [50, 30, 70, 20, 40, 60, 80]:
        bst.root = bst.insert(bst.root, number)
    print(bst.search(bst.root, 60) is not None)      # True
    print(bst.search(bst.root, 65) is not None)      # False
    bst.root = bst.delete_node(bst.root, 50)         # a node with two children
    print(bst.inorder_traversal(bst.root, ""))       # 20-30-40-60-70-80-