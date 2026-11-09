import random

from binary_tree import BinaryTree

MAX_NODES = 15
MIN_VALUE = 0
MAX_VALUE = 999
NOT_SET = object()


# ---------- Small helpers ----------
def tree_to_dict(node):
    """The tree as nested dictionaries, so the page can draw it."""
    if node is None:
        return None
    return {"value": node.value, "left": tree_to_dict(node.left), "right": tree_to_dict(node.right)}


def count_nodes(node):
    return 0 if node is None else 1 + count_nodes(node.left) + count_nodes(node.right)


def parse_value(text):
    text = (text or "").strip()
    if not text:
        return None, "Type a number first."
    try:
        value = int(text)
    except ValueError:
        return None, f"'{text}' is not a whole number from {MIN_VALUE} to {MAX_VALUE}."
    if value < MIN_VALUE or value > MAX_VALUE:
        return None, f"Use whole numbers from {MIN_VALUE} to {MAX_VALUE}."
    return value, None


def step(message, focus=(), found=(), remove=(), visited=(), output=None, new_tree=NOT_SET):
    """One frame of the animation.
    focus = amber, found = green, remove = coral, visited = blue.
    A step only carries a "tree" when the tree changes at that moment."""
    s = {"message": message, "focus": list(focus), "found": list(found), "remove": list(remove),
         "visited": list(visited), "output": None if output is None else list(output)}
    if new_tree is not NOT_SET:
        s["tree"] = new_tree
    return s


def result(title, message, before, tree, steps):
    return {"title": title, "message": message, "before": before, "after": tree_to_dict(tree.root),
            "steps": steps}, None


def walk_path(tree, key, steps):
    """Go down from the root looking for key, the same way search() does.
    Adds one step for every node it compares with.
    Returns (node or None, last node visited, side we fell off on, path)."""
    node, last, side, path = tree.root, None, None, []
    while node is not None:
        path.append(node.value)
        if key == node.value:
            steps.append(step(f"Compare {key} with {node.value}: they are equal. Found it!",
                              found=[node.value], output=path))
            return node, last, side, path
        if key < node.value:
            steps.append(step(f"Compare {key} with {node.value}: {key} < {node.value}, so go left.",
                              focus=[node.value], output=path))
            last, side, node = node, "left", node.left
        else:
            steps.append(step(f"Compare {key} with {node.value}: {key} > {node.value}, so go right.",
                              focus=[node.value], output=path))
            last, side, node = node, "right", node.right
    return None, last, side, path


# ---------- Operations ----------
def do_insert(tree, key):
    before = tree_to_dict(tree.root)
    if tree.search(tree.root, key) is not None:
        return None, f"{key} is already in the tree. A binary search tree keeps each number once."
    if count_nodes(tree.root) >= MAX_NODES:
        return None, f"The tree is full (maximum {MAX_NODES} numbers) so it stays easy to read."

    steps = []
    if tree.root is None:
        tree.root = tree.insert(tree.root, key)
        steps.append(step(f"The tree is empty, so {key} becomes the root.", found=[key],
                          output=[], new_tree=tree_to_dict(tree.root)))
        return result(f"Insert {key}", f"Inserted {key} as the root.", before, tree, steps)

    _, last, side, path = walk_path(tree, key, steps)
    tree.root = tree.insert(tree.root, key)
    steps.append(step(f"Found an empty spot on the {side} of {last.value}. Insert {key} there.",
                      found=[key], output=path, new_tree=tree_to_dict(tree.root)))
    return result(f"Insert {key}", f"Inserted {key} as the {side} child of {last.value}.", before, tree, steps)


def do_search(tree, key):
    before = tree_to_dict(tree.root)
    steps = []
    if tree.root is None:
        steps.append(step("The tree is empty, so there is nothing to find.", output=[]))
        return result(f"Search {key}", "The tree is empty.", before, tree, steps)

    _, last, _, path = walk_path(tree, key, steps)
    node = tree.search(tree.root, key)                # the lab method gives the answer
    if node is None:
        steps.append(step(f"Reached an empty spot, so {key} is not in the tree.",
                          focus=[last.value], output=path))
        return result(f"Search {key}", f"{key} is not in the tree.", before, tree, steps)
    return result(f"Search {key}", f"Found {key} after looking at {len(path)} "
                  f"node{'' if len(path) == 1 else 's'}.", before, tree, steps)


def do_delete(tree, key):
    before = tree_to_dict(tree.root)
    steps = []
    if tree.root is None:
        steps.append(step("The tree is empty, so there is nothing to delete.", output=[]))
        return result(f"Delete {key}", "The tree is empty.", before, tree, steps)

    node, last, _, path = walk_path(tree, key, steps)
    if node is None:
        steps.append(step(f"Reached an empty spot, so {key} is not in the tree. Nothing to delete.",
                          focus=[last.value], output=path))
        return result(f"Delete {key}", f"{key} is not in the tree, so nothing was deleted.", before, tree, steps)

    replacement = None
    if node.left is None and node.right is None:
        steps.append(step(f"{key} is a leaf (it has no children), so it can simply be removed.",
                          remove=[key], output=path))
    elif node.left is None or node.right is None:
        child = node.right if node.left is None else node.left
        replacement = child.value
        steps.append(step(f"{key} has one child, {child.value}. Remove {key} and put {child.value} in its place.",
                          remove=[key], found=[child.value], output=path))
    else:
        steps.append(step(f"{key} has two children. Replace it with its inorder successor: "
                          "the smallest value in its right subtree.", focus=[key], output=path))
        successor = node.right
        steps.append(step(f"Go to the right child, {successor.value}.",
                          focus=[successor.value], remove=[key], output=path))
        while successor.left is not None:
            successor = successor.left
            steps.append(step(f"Keep going left: {successor.value}.",
                              focus=[successor.value], remove=[key], output=path))
        replacement = successor.value
        steps.append(step(f"{successor.value} has no left child, so it is the smallest value on the right. "
                          "It is the successor.", found=[successor.value], remove=[key], output=path))
        steps.append(step(f"Copy {successor.value} into the place of {key}, then delete the original "
                          f"{successor.value} from the right subtree.",
                          found=[successor.value], remove=[key], output=path))

    tree.root = tree.delete_node(tree.root, key)      # the lab method does the real work
    steps.append(step(f"Deleted {key}. The tree is updated.",
                      found=[] if replacement is None else [replacement], output=path,
                      new_tree=tree_to_dict(tree.root)))
    return result(f"Delete {key}", f"Deleted {key}.", before, tree, steps)


TRAVERSALS = {
    "inorder": ("Inorder", "left, root, right"),
    "preorder": ("Preorder", "root, left, right"),
    "postorder": ("Postorder", "left, right, root"),
}


def do_traversal(tree, kind):
    before = tree_to_dict(tree.root)
    name, rule = TRAVERSALS[kind]
    if tree.root is None:
        return None, "The tree is empty. Insert some numbers first."

    # the order comes straight from the lab methods
    if kind == "inorder":
        order = [int(v) for v in tree.inorder_traversal(tree.root, "").split("-") if v]
    elif kind == "preorder":
        order = [int(v) for v in tree.preorder_traversal(tree.root, "").split()]
    else:
        order = [int(v) for v in tree.post_traversal(tree.root, "").split()]

    steps = [step(f"{name} traversal: visit {rule}.", output=[])]
    for i, value in enumerate(order):
        steps.append(step(f"Visit {value}.", focus=[value], visited=order[:i], output=order[:i + 1]))
    steps.append(step(f"Done. {name} order: {' '.join(str(v) for v in order)}",
                      visited=order, output=order))
    return result(f"{name} traversal", f"{name} order: {' '.join(str(v) for v in order)}",
                  before, tree, steps)


def do_random(tree):
    before = tree_to_dict(tree.root)
    tree.root = None
    values = random.sample(range(1, 100), 8)
    for value in values:
        tree.root = tree.insert(tree.root, value)
    return result("Random tree", f"Built a random tree from {len(values)} numbers: "
                  f"{', '.join(str(v) for v in values)}.", before, tree, [])


def do_clear(tree):
    before = tree_to_dict(tree.root)
    tree.root = None
    return result("Clear", "The tree is empty now.", before, tree, [])


def run_tree_action(tree, action, text):
    """Returns (result dictionary, None) or (None, error message)."""
    if action in ("insert", "search", "delete"):
        key, error = parse_value(text)
        if error:
            return None, error
        return {"insert": do_insert, "search": do_search, "delete": do_delete}[action](tree, key)
    if action in TRAVERSALS:
        return do_traversal(tree, action)
    if action == "random":
        return do_random(tree)
    if action == "clear":
        return do_clear(tree)
    return None, "Unknown action."


def sample_tree():
    tree = BinaryTree()
    for value in (50, 30, 70, 20, 40, 60, 80):
        tree.root = tree.insert(tree.root, value)
    return tree