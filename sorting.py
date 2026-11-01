import math
import re

MAX_ITEMS = 20
MAX_ABS = 99999


# ---------- Reading the user's numbers ----------
def parse_numbers(text):
    """Return (list of numbers, None) or (None, error message)."""
    tokens = [t for t in re.split(r"[,\s]+", text.strip()) if t]
    if not tokens:
        return None, "Type some numbers first, for example 5, 2, 9, 1, 7."

    values = []
    for token in tokens:
        try:
            number = int(token)
        except ValueError:
            try:
                number = float(token)
            except ValueError:
                return None, f"'{token}' is not a number. Separate the numbers with commas."
        if not math.isfinite(number) or abs(number) > MAX_ABS:
            return None, f"Use numbers between -{MAX_ABS} and {MAX_ABS}."
        values.append(number)

    if len(values) < 2:
        return None, "Enter at least 2 numbers."
    if len(values) > MAX_ITEMS:
        return None, f"Enter at most {MAX_ITEMS} numbers so the bars stay readable."
    return values, None


def show(value):
    return str(int(value)) if float(value).is_integer() else str(value)


# ---------- Recording every step for the animation ----------
class Recorder:
    """Keeps the list being sorted and writes down what it looks like after every step."""

    def __init__(self, values):
        self.a = list(values)
        self.steps = []
        self.comparisons = 0
        self.moves = 0                 # swaps or writes
        self.done = set()              # positions that are in their final place

    def add(self, message, compare=(), moved=(), pivot=None, marker=None,
            key=None, hole=None, span=None, aux=None):
        array = list(self.a)
        if hole is not None:
            array[hole] = None         # insertion sort: the empty slot left by the key
        self.steps.append({
            "array": array, "compare": list(compare), "moved": list(moved),
            "sorted": sorted(self.done), "pivot": pivot, "marker": marker,
            "key": key, "hole": hole, "span": span, "aux": aux, "message": message,
            "comparisons": self.comparisons, "moves": self.moves,
        })

    def finish(self):
        self.done = set(range(len(self.a)))
        self.add("Done. The list is sorted.")


# ---------- The five algorithms (your code, with add() calls to record the steps) ----------
def bubble_sort(rec):
    a = rec.a
    n = len(a)
    rec.add("Start. Compare neighbors and swap them when they are out of order.")
    for i in range(n - 1):
        for j in range(n - 1 - i):
            rec.comparisons += 1
            if a[j] > a[j + 1]:
                rec.add(f"{show(a[j])} > {show(a[j + 1])}, so they are out of order.", compare=(j, j + 1))
                a[j], a[j + 1] = a[j + 1], a[j]
                rec.moves += 1
                rec.add(f"Swap them: {show(a[j])} goes left and {show(a[j + 1])} goes right.", moved=(j, j + 1))
            else:
                rec.add(f"{show(a[j])} <= {show(a[j + 1])}, they are already in order.", compare=(j, j + 1))
        # a[n-1-i] is now in place
        rec.done.add(n - 1 - i)
        rec.add(f"{show(a[n - 1 - i])} is now in its final place at the end.")
    rec.done.add(0)
    return a


def selection_sort(rec):
    a = rec.a
    n = len(a)
    rec.add("Start. Find the smallest item and put it first, then repeat for the rest.")
    for i in range(n - 1):
        m = i
        rec.add(f"Pass {i + 1}: assume {show(a[m])} (position {i}) is the smallest so far.", marker=m)
        for j in range(i + 1, n):
            rec.comparisons += 1
            if a[j] < a[m]:
                rec.add(f"{show(a[j])} < {show(a[m])}, so {show(a[j])} is the new smallest.",
                        compare=(j,), marker=m)
                m = j
            else:
                rec.add(f"{show(a[j])} >= {show(a[m])}, the smallest stays the same.",
                        compare=(j,), marker=m)
        a[i], a[m] = a[m], a[i]
        rec.done.add(i)
        if m != i:
            rec.moves += 1
            rec.add(f"Swap the smallest ({show(a[i])}) into position {i}.", moved=(i, m))
        else:
            rec.add(f"{show(a[i])} is already in position {i}.")
    rec.done.add(n - 1)
    return a


def insertion_sort(rec):
    a = rec.a
    rec.done.add(0)
    rec.add("Start. The first item alone is a sorted list. Insert the other items one by one.")
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        rec.add(f"Lift {show(key)} out as the key. Find where it belongs on the left.", key=key, hole=i)
        while j >= 0:
            rec.comparisons += 1
            if a[j] > key:
                rec.add(f"{show(a[j])} > {show(key)}: shift {show(a[j])} one place to the right.",
                        compare=(j,), key=key, hole=j + 1)
                a[j + 1] = a[j]
                rec.moves += 1
                rec.add(f"{show(a[j + 1])} moved right. The empty slot moves left.",
                        moved=(j + 1,), key=key, hole=j)
                j -= 1
            else:
                rec.add(f"{show(a[j])} <= {show(key)}: stop. The key belongs right after it.",
                        compare=(j,), key=key, hole=j + 1)
                break
        a[j + 1] = key
        rec.moves += 1
        rec.done = set(range(i + 1))
        rec.add(f"Insert {show(key)} at position {j + 1}.", moved=(j + 1,))
    return a


def merge(rec, lo, mid, hi):
    a = rec.a
    aux = a[lo:hi + 1]
    i, j, k = lo, mid + 1, lo
    final = lo == 0 and hi == len(a) - 1

    def aux_view():
        used = list(range(0, i - lo)) + list(range(mid + 1 - lo, j - lo))
        return {"lo": lo, "values": list(aux), "used": used,
                "i": i - lo if i <= mid else None, "j": j - lo if j <= hi else None}

    rec.add(f"Merge the sorted halves at positions {lo}-{mid} and {mid + 1}-{hi}. "
            "A copy of the range is kept below.", span=(lo, hi), aux=aux_view())
    while k <= hi:
        if i <= mid and j <= hi:
            rec.comparisons += 1
            side = "left" if aux[i - lo] <= aux[j - lo] else "right"
            rec.add(f"Compare {show(aux[i - lo])} (left) and {show(aux[j - lo])} (right): take the {side} one.",
                    span=(lo, hi), aux=aux_view())
        if j > hi or (i <= mid and
                      aux[i - lo] <= aux[j - lo]):
            a[k] = aux[i - lo]; i += 1
            source = "left"
        else:
            a[k] = aux[j - lo]; j += 1
            source = "right"
        rec.moves += 1
        if final:
            rec.done.add(k)
        rec.add(f"Write {show(a[k])} (from the {source} half) into position {k}.",
                moved=(k,), span=(lo, hi), aux=aux_view())
        k += 1


def merge_sort(rec, lo, hi):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    merge_sort(rec, lo, mid)
    merge_sort(rec, mid + 1, hi)
    merge(rec, lo, mid, hi)


def merge_sort_all(rec):
    rec.add("Start. Split the list into halves, sort each half, then merge the halves back together.")
    merge_sort(rec, 0, len(rec.a) - 1)
    return rec.a


def quicksort(rec, lo, hi):
    a = rec.a
    if lo >= hi:
        if lo == hi:
            rec.done.add(lo)
            rec.add(f"{show(a[lo])} is alone in its range, so it is in its final place.", span=(lo, hi))
        return
    pivot = a[hi]
    i = lo
    rec.add(f"Partition positions {lo}-{hi}. The last item, {show(pivot)}, is the pivot.",
            pivot=hi, marker=i, span=(lo, hi))
    for j in range(lo, hi):
        rec.comparisons += 1
        if a[j] < pivot:
            rec.add(f"{show(a[j])} < {show(pivot)}: it belongs on the left side (position {i}).",
                    compare=(j,), pivot=hi, marker=i, span=(lo, hi))
            a[i], a[j] = a[j], a[i]
            if i != j:
                rec.moves += 1
                rec.add(f"Swap positions {i} and {j}.", moved=(i, j), pivot=hi, marker=i, span=(lo, hi))
            i += 1
        else:
            rec.add(f"{show(a[j])} >= {show(pivot)}: it stays on the right side.",
                    compare=(j,), pivot=hi, marker=i, span=(lo, hi))
    a[i], a[hi] = a[hi], a[i]
    if i != hi:
        rec.moves += 1
    rec.done.add(i)
    rec.add(f"Put the pivot {show(pivot)} into its final place, position {i}.",
            moved=(i, hi), pivot=i, span=(lo, hi))
    quicksort(rec, lo, i - 1)
    quicksort(rec, i + 1, hi)


def quick_sort_all(rec):
    rec.add("Start. Pick a pivot, put smaller items on its left and bigger items on its right, then repeat on each side.")
    quicksort(rec, 0, len(rec.a) - 1)
    return rec.a


FUNCTIONS = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge": merge_sort_all,
    "quick": quick_sort_all,
}


def run_sort(algorithm, values):
    rec = Recorder(values)
    FUNCTIONS[algorithm](rec)
    rec.finish()
    return rec.steps


# ---------- Text shown on the page ----------
SORT_ORDER = ["bubble", "selection", "insertion", "merge", "quick"]

SORT_INFO = {
    "bubble": {
        "name": "Bubble sort",
        "description": "Compares neighbors and swaps them when they are out of order. After every pass the biggest remaining item has bubbled to the end.",
        "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "Yes",
        "code": '''def bubble_sort(a):
    n = len(a)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
        # a[n-1-i] is now in place
    return a''',
    },
    "selection": {
        "name": "Selection sort",
        "description": "Finds the smallest item in the unsorted part and swaps it to the front. The sorted part grows one item at a time.",
        "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "No",
        "code": '''def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
    return a''',
    },
    "insertion": {
        "name": "Insertion sort",
        "description": "Takes the next item (the key) and slides it left into its place among the items already sorted, like sorting playing cards in your hand.",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "Yes",
        "code": '''def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a''',
    },
    "merge": {
        "name": "Merge sort",
        "description": "Splits the list in halves, sorts each half, then merges the two sorted halves by always taking the smaller front item.",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)", "stable": "Yes",
        "code": '''def merge(a, lo, mid, hi):
    aux = a[lo:hi + 1]
    i, j, k = lo, mid + 1, lo
    while k <= hi:
        if j > hi or (i <= mid and
                      aux[i-lo] <= aux[j-lo]):
            a[k] = aux[i - lo]; i += 1
        else:
            a[k] = aux[j - lo]; j += 1
        k += 1

def merge_sort(a, lo, hi):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    merge_sort(a, lo, mid)
    merge_sort(a, mid + 1, hi)
    merge(a, lo, mid, hi)''',
    },
    "quick": {
        "name": "Quick sort",
        "description": "Picks the last item as the pivot, puts smaller items on its left and bigger items on its right, then sorts each side the same way.",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "space": "O(log n)", "stable": "No",
        "code": '''def quicksort(a, lo, hi):
    if lo >= hi: return
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    quicksort(a, lo, i-1); quicksort(a, i+1, hi)''',
    },
}