import math
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session

from linkedlist import LinkedList

from infix import infixToPostfix, validate_infix

app = Flask(__name__)
app.secret_key = "gc-portfolio-8f3k29xqLm4vT7pZ"

PROFILE = {
    "name": "Gabriel Carl S. Calasang",
    "course": "BSCpE 2-3",
    "subject": "Data Structures and Algorithms",
    "motto": "Live the Best Story of Your Life.",
    "email": "gabrielcarlcalasang@gmail.com",
    "phone": "+63 935 115 6394",
    "location": "Imus City, Cavite, Philippines",
    "github": "github.com/zai-29",
}

WORKS = [
    {"title": "String Methods", "desc": "Run one text through upper, lower, replace, count and more.", "url": "works"},
    {"title": "Area of a Circle", "desc": "Pick a unit and watch a 3D cylinder resize.", "url": "acircle"},
    {"title": "Area of a Triangle", "desc": "Pick a unit and watch a 3D prism resize.", "url": "atriangle"},
    {"title": "Doubly Linked List", "desc": "Add, insert, search, delete and reverse nodes.", "url": "linkedlist"},
    {"title": "Infix to Postfix", "desc": "Convert an expression with a stack. Invalid input is detected.", "url": "postfix"},
]

# ---------- Units (metres per unit) ----------
UNITS = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048}


def fmt(x):
    """Readable number: thousands separators, no trailing zeros, scientific if extreme."""
    if x != 0 and (abs(x) >= 1e9 or abs(x) < 1e-4):
        return f"{x:.4e}"
    return f"{x:,.4f}".rstrip("0").rstrip(".")


def to_positive_float(raw):
    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None
    return number if number > 0 and math.isfinite(number) else None


def read_units():
    unit_in = request.form.get("unit", "cm")
    unit_out = request.form.get("out_unit", "same")
    if unit_out == "same":
        unit_out = unit_in
    if unit_in not in UNITS or unit_out not in UNITS:
        return None, None
    return unit_in, unit_out


# ---------- History (kept per visitor in the session cookie) ----------
HISTORY_LIMIT = 15


def get_history(key):
    return session.get("history", {}).get(key, [])


def add_history(key, text):
    history = session.get("history", {})
    entries = history.get(key, [])
    entries.insert(0, {"t": datetime.now().strftime("%H:%M"), "text": text})
    history[key] = entries[:HISTORY_LIMIT]
    session["history"] = history


def history_html(key):
    return render_template("_history.html", entries=get_history(key), work=key)


@app.route("/history/<work>/clear", methods=["POST"])
def clear_history(work):
    history = session.get("history", {})
    history[work] = []
    session["history"] = history
    return jsonify(ok=True, history=history_html(work))


# ---------- Pages ----------
@app.route("/")
def index():
    return render_template("index.html", works=WORKS, profile=PROFILE)


@app.route("/profile")
def profile():
    return render_template("profile.html", profile=PROFILE)


@app.route("/contact")
def contact():
    return render_template("contact.html", profile=PROFILE)


# ---------- String methods ----------
# key: (label, [argument labels], function)
STRING_METHODS = {
    "upper": ("upper()", [], lambda s: s.upper()),
    "lower": ("lower()", [], lambda s: s.lower()),
    "title": ("title()", [], lambda s: s.title()),
    "capitalize": ("capitalize()", [], lambda s: s.capitalize()),
    "swapcase": ("swapcase()", [], lambda s: s.swapcase()),
    "strip": ("strip()", [], lambda s: s.strip()),
    "reverse": ("reverse", [], lambda s: s[::-1]),
    "length": ("len()", [], lambda s: len(s)),
    "words": ("word count", [], lambda s: len(s.split())),
    "vowels": ("vowel count", [], lambda s: sum(c in "aeiouAEIOU" for c in s)),
    "palindrome": ("is palindrome", [],
                   lambda s: (lambda t: t == t[::-1])("".join(c.lower() for c in s if c.isalnum()))),
    "isalpha": ("isalpha()", [], lambda s: s.isalpha()),
    "isdigit": ("isdigit()", [], lambda s: s.isdigit()),
    "isalnum": ("isalnum()", [], lambda s: s.isalnum()),
    "count": ("count(sub)", ["Text to count"], lambda s, a: s.count(a)),
    "find": ("find(sub)", ["Text to find"], lambda s, a: s.find(a)),
    "startswith": ("startswith()", ["Prefix"], lambda s, a: s.startswith(a)),
    "endswith": ("endswith()", ["Suffix"], lambda s, a: s.endswith(a)),
    "replace": ("replace(old, new)", ["Old text", "New text"], lambda s, a, b: s.replace(a, b)),
    "split": ("split(sep)", ["Separator (blank = spaces)"],
              lambda s, a: s.split(a) if a else s.split()),
}


@app.route("/works")
def works():
    methods = [{"key": k, "label": v[0], "args": v[1]} for k, v in STRING_METHODS.items()]
    return render_template("touppercase.html", methods=methods,
                           entries=get_history("strings"), work="strings")


@app.route("/works/run", methods=["POST"])
def run_string_method():
    text = request.form.get("text", "")
    key = request.form.get("method", "")
    if key not in STRING_METHODS:
        return jsonify(ok=False, error="Pick a method."), 400
    label, arg_labels, func = STRING_METHODS[key]
    args = [request.form.get(f"arg{i + 1}", "") for i in range(len(arg_labels))]
    if arg_labels and key != "split" and not args[0]:
        return jsonify(ok=False, error=f"Enter a value for: {arg_labels[0].lower()}."), 400
    if not text:
        return jsonify(ok=False, error="Enter some text first."), 400

    result = str(func(text, *args))
    shown = result if result != "" else "(empty)"
    arg_text = ", ".join(f"'{a}'" for a in args)
    add_history("strings", f"{label} on '{text}'" + (f" with {arg_text}" if args else "") + f"  →  {shown}")
    return jsonify(ok=True, result=shown, history=history_html("strings"))


# ---------- Areas ----------
@app.route("/works/area/circle")
def acircle():
    return render_template("circle.html", units=list(UNITS), entries=get_history("circle"), work="circle")


@app.route("/works/area/circle/compute", methods=["POST"])
def compute_circle():
    unit_in, unit_out = read_units()
    radius = to_positive_float(request.form.get("radius", ""))
    if unit_in is None:
        return jsonify(ok=False, error="Pick a valid unit."), 400
    if radius is None:
        return jsonify(ok=False, error="Enter a radius greater than 0."), 400

    area_m2 = math.pi * (radius * UNITS[unit_in]) ** 2
    area = area_m2 / UNITS[unit_out] ** 2
    result = f"{fmt(area)} {unit_out}²"
    detail = f"r = {fmt(radius)} {unit_in}, A = πr²"
    add_history("circle", f"r = {fmt(radius)} {unit_in}  →  {result}")
    return jsonify(ok=True, result=result, detail=detail, history=history_html("circle"))


@app.route("/works/area/triangle")
def atriangle():
    return render_template("triangle.html", units=list(UNITS), entries=get_history("triangle"), work="triangle")


@app.route("/works/area/triangle/compute", methods=["POST"])
def compute_triangle():
    unit_in, unit_out = read_units()
    base = to_positive_float(request.form.get("base", ""))
    height = to_positive_float(request.form.get("height", ""))
    if unit_in is None:
        return jsonify(ok=False, error="Pick a valid unit."), 400
    if base is None or height is None:
        return jsonify(ok=False, error="Enter a base and a height greater than 0."), 400

    area_m2 = 0.5 * (base * UNITS[unit_in]) * (height * UNITS[unit_in])
    area = area_m2 / UNITS[unit_out] ** 2
    result = f"{fmt(area)} {unit_out}²"
    detail = f"b = {fmt(base)} {unit_in}, h = {fmt(height)} {unit_in}, A = ½bh"
    add_history("triangle", f"b = {fmt(base)}, h = {fmt(height)} {unit_in}  →  {result}")
    return jsonify(ok=True, result=result, detail=detail, history=history_html("triangle"))

# ---------- Infix to postfix ----------
@app.route("/works/postfix")
def postfix():
    return render_template("postfix.html", entries=get_history("postfix"), work="postfix")


@app.route("/works/postfix/convert", methods=["POST"])
def convert_postfix():
    expression = request.form.get("expression", "").strip()
    error = validate_infix(expression)
    if error:
        return jsonify(ok=False, error=error), 400

    cleaned = "".join(expression.split())
    steps = []
    result = infixToPostfix(cleaned, steps)
    add_history("postfix", f"{expression}  →  {result}")
    return jsonify(ok=True, result=result, detail=f"Infix: {expression}", history=history_html("postfix"),
                   steps=steps, tokens=list(cleaned))

# ---------- Doubly linked list ----------
my_list = LinkedList()
for _value in ("A", "B", "C"):
    my_list.insert_at_end(_value)


def chain_html(found=None, new=None):
    return render_template("_chain.html", items=my_list.to_list(), backward=my_list.to_list_backward(),
                           size=len(my_list), found=found, new=new)


@app.route("/works/linkedlist")
def linkedlist():
    return render_template("linkedlist.html", chain=chain_html())


@app.route("/works/linkedlist/action", methods=["POST"])
def linkedlist_action():
    action = request.form.get("action", "")
    value = request.form.get("value", "").strip()
    after = request.form.get("after", "").strip()
    message, ok, found, new = "", True, None, None

    if action == "reverse":
        my_list.reverse()
        message = "List reversed."
    elif action == "clear":
        my_list.clear()
        message = "List cleared."
    elif action == "pop_front":
        removed = my_list.remove_beginning()
        ok = removed is not None
        message = f"Removed {removed} from the front." if ok else "The list is empty."
    elif action == "pop_back":
        removed = my_list.remove_at_end()
        ok = removed is not None
        message = f"Removed {removed} from the end." if ok else "The list is empty."
    elif not value:
        ok, message = False, "Enter a value first."
    elif action == "append":
        my_list.insert_at_end(value)
        new, message = len(my_list) - 1, f"Added {value} to the end."
    elif action == "prepend":
        my_list.insert_at_beginning(value)
        new, message = 0, f"Added {value} to the front."
    elif action == "insert":
        try:
            index = int(request.form.get("index", ""))
        except ValueError:
            index = -1
        if my_list.insert_at(index, value):
            new, message = index, f"Inserted {value} at position {index}."
        else:
            ok, message = False, f"Position must be a whole number from 0 to {len(my_list)}."
    elif action == "insert_after":
        if my_list.insert_after(after, value) is None:
            ok, message = False, f"{after} is not in the list."
        else:
            new, message = my_list.index_of(after) + 1, f"Inserted {value} after {after}."
    elif action == "delete":
        removed = my_list.remove_at(value)
        ok = removed is not None
        message = f"Deleted {removed}." if ok else f"{value} is not in the list."
    elif action == "search":
        if my_list.search(value):
            found = my_list.index_of(value)
            message = f"Found {value} at position {found}."
        else:
            ok, message = False, f"{value} is not in the list."
    else:
        ok, message = False, "Unknown action."

    return jsonify(ok=ok, message=message, html=chain_html(found=found, new=new))


if __name__ == "__main__":
    app.run(debug=True)
