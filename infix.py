from linkedlist import LinkedList


def prec(c):
    if c == '^':
        return 3
    elif c == '/' or c == '*':
        return 2
    elif c == '+' or c == '-':
        return 1
    else:
        return -1


def isRightAssociative(c):
    return c == '^'


def infixToPostfix(s, steps=None):
    st = LinkedList()      # the operator stack: the TOP of the stack is the tail of the list
    res = LinkedList()     # the postfix result, built by adding nodes at the end

    # Writes down what the stack and the output look like (used by the animation).
    # The conversion works the same with or without it.
    def record(i, title, why, new_stack=None, new_output=None, popped=None):
        if steps is not None:
            steps.append({"i": i, "title": title, "why": why,
                          "stack": st.to_list(), "output": res.to_list(),
                          "new_stack": new_stack, "new_output": new_output, "popped": popped})

    record(-1, "Start", "The stack and the output are empty. Read the expression from left to right.")

    for i, c in enumerate(s):
        # If operand, add to result
        if isOperand(c):
            res.insert_at_end(c)
            record(i, f"Read '{c}'", "It is an operand, so it goes straight to the output.",
                   new_output=len(res) - 1)

        # If '(', push to stack
        elif c == '(':
            st.insert_at_end('(')
            record(i, "Push '('", "An opening parenthesis always goes on the stack.",
                   new_stack=len(st) - 1)

        # If ')', pop until '('
        elif c == ')':
            while st.tail and st.tail.data != '(':
                op = st.remove_at_end()
                res.insert_at_end(op)
                record(i, f"Pop '{op}' to output",
                       "Closing parenthesis: pop operators until '(' is found.",
                       new_output=len(res) - 1, popped=op)
            st.remove_at_end()
            record(i, "Discard '('", "Found the matching '('. Parentheses never appear in the output.",
                   popped='(')

        # If operator
        else:
            while st.tail and st.tail.data != '(' and \
                (prec(st.tail.data) > prec(c) or (prec(st.tail.data) == prec(c)
                                                  and not isRightAssociative(c))):
                top = st.tail.data
                if prec(top) > prec(c):
                    why = f"'{top}' has higher precedence than '{c}', so it comes out first."
                else:
                    why = f"'{top}' and '{c}' have equal precedence and '{c}' is left-associative, so '{top}' comes out first."
                st.remove_at_end()
                res.insert_at_end(top)
                record(i, f"Pop '{top}' to output", why, new_output=len(res) - 1, popped=top)

            top = st.tail.data if st.tail else None
            if top is None:
                why = "The stack is empty, so it is pushed."
            elif top == '(':
                why = "The top of the stack is '(', so it is pushed."
            elif prec(top) < prec(c):
                why = f"'{c}' has higher precedence than '{top}', so it goes on top of it."
            else:
                why = f"'{c}' is right-associative, so it waits on top of '{top}'."
            st.insert_at_end(c)
            record(i, f"Push '{c}'", why, new_stack=len(st) - 1)

    # Pop remaining operators
    while st.tail:
        op = st.remove_at_end()
        res.insert_at_end(op)
        record(len(s), f"Pop '{op}' to output", "End of the expression: pop everything left on the stack.",
               new_output=len(res) - 1, popped=op)

    result = ''.join(res.to_list())
    record(len(s), "Done", f"The postfix expression is {result}")
    return result


def isOperand(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')


def validate_infix(s):
    """Return None if the expression is valid, otherwise a message that says what is wrong."""
    if not s.strip():
        return "Type an expression first."

    expect_operand = True     # True: we need an operand or '(' next
    depth = 0                 # how many '(' are still open
    previous = ""             # the last character that was not a space

    for i, c in enumerate(s):
        if c.isspace():
            continue
        spot = f"position {i + 1}"

        if not (isOperand(c) or c in "+-*/^()"):
            return f"Invalid character '{c}' at {spot}. Use letters, digits, + - * / ^ and parentheses."

        if expect_operand:
            if isOperand(c):
                expect_operand = False
            elif c == '(':
                depth += 1
            elif c == ')':
                if previous == '(':
                    return f"Empty parentheses at {spot}."
                return f"Missing operand before ')' at {spot}."
            else:
                if previous == "":
                    return f"The expression cannot start with '{c}' (position 1)."
                if previous == '(':
                    return f"'{c}' at {spot} has no operand before it."
                return f"Two operators in a row at {spot}: '{previous}{c}'."
        else:
            if c == ')':
                depth -= 1
                if depth < 0:
                    return f"Unmatched ')' at {spot}."
            elif c in "+-*/^":
                expect_operand = True
            elif c == '(':
                return f"Missing operator before '(' at {spot}."
            else:
                return (f"Two operands in a row at {spot}. Put an operator between them. "
                        "Operands are single letters or digits.")
        previous = c

    if expect_operand:
        return f"The expression cannot end with '{previous}'."
    if depth > 0:
        return f"Missing {depth} closing parenthes{'is' if depth == 1 else 'es'} ')'."
    return None


if __name__ == '__main__':
    exp = "a*(b+c)/d"
    print(infixToPostfix(exp))