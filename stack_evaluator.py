import re
import sys



class Stack:


    def __init__(self):
        self._items = []

    def push(self, item):

        self._items.append(item)

    def pop(self):

        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):

        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)



PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "neg": 3}
BINARY_OPS = {"+", "-", "*", "/"}

TOKEN_PATTERN = re.compile(r"\s*(\d+\.\d*|\.\d+|\d+|[-+*/()])")


def tokenize(expression):

    tokens = []
    pos = 0
    expression = expression.strip()
    while pos < len(expression):
        match = TOKEN_PATTERN.match(expression, pos)
        if not match:
            raise ValueError(f"invalid character '{expression[pos:].strip()[0]}'")
        text = match.group(1)
        pos = match.end()

        if text in "+-*/()" and len(text) == 1:
            if text == "-":
                previous = tokens[-1] if tokens else None
                if previous is None or previous in BINARY_OPS or previous in ("(", "neg"):
                    text = "neg"
            tokens.append(text)
        else:
            tokens.append(float(text))
    return tokens


def apply_operator(operator, values):

    try:
        if operator == "neg":
            a = values.pop()
            values.push(-a)
            return
        b = values.pop()
        a = values.pop()
    except IndexError:
        raise ValueError("malformed expression (missing operand)")

    if operator == "+":
        values.push(a + b)
    elif operator == "-":
        values.push(a - b)
    elif operator == "*":
        values.push(a * b)
    elif operator == "/":
        if b == 0:
            raise ValueError("division by zero")
        values.push(a / b)


def evaluate(expression):

    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("empty expression")

    values = Stack()
    operators = Stack()

    for token in tokens:
        if isinstance(token, float):
            values.push(token)

        elif token == "(":
            operators.push(token)

        elif token == ")":
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators.pop(), values)
            if operators.is_empty():
                raise ValueError("mismatched parentheses")
            operators.pop()

        elif token == "neg":
            operators.push(token)

        else:
            while (not operators.is_empty()
                   and operators.peek() != "("
                   and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]):
                apply_operator(operators.pop(), values)
            operators.push(token)

    while not operators.is_empty():
        operator = operators.pop()
        if operator == "(":
            raise ValueError("mismatched parentheses")
        apply_operator(operator, values)

    if values.size() != 1:
        raise ValueError("malformed expression")
    return values.pop()


def format_result(number):

    if number == int(number):
        return str(int(number))
    return str(round(number, 6))



SEPARATOR = re.compile(r"^\s*-{3,}\s*$")

def process_file(input_path, output_path):

    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.read().splitlines()

    output_lines = []
    for line in lines:
        if SEPARATOR.match(line):
            output_lines.append(line.strip())
        elif line.strip() == "":
            continue
        else:
            try:
                output_lines.append(format_result(evaluate(line)))
            except ValueError as error:
                output_lines.append(f"Error: {error}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines) + "\n")

    return output_lines


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        process_file(input_path, output_path)
    except FileNotFoundError:
        print(f"Error: could not find '{input_path}'.")
        sys.exit(1)
    print(f"Done. Results written to '{output_path}'.")


if __name__ == "__main__":
    main()
