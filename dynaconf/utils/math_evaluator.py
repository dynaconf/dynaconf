import math
import operator

_add, _sub, _mul = operator.add, operator.sub, operator.mul
_truediv, _pow, _sqrt = operator.truediv, operator.pow, math.sqrt
_sin, _cos, _tan, _radians = math.sin, math.cos, math.tan, math.radians
_asin, _acos, _atan = math.asin, math.acos, math.atan
_degrees, _log, _log10 = math.degrees, math.log, math.log10
_e, _pi = math.e, math.pi
_ops = {
    "+": (2, _add),
    "-": (2, _sub),
    "*": (2, _mul),
    "/": (2, _truediv),
    "**": (2, _pow),
    "sin": (1, _sin),
    "cos": (1, _cos),
    "tan": (1, _tan),
    "asin": (1, _asin),
    "acos": (1, _acos),
    "atan": (1, _atan),
    "sqrt": (1, _sqrt),
    "rad": (1, _radians),
    "deg": (1, _degrees),
    "ln": (1, _log),
    "log": (1, _log10),
}
_okeys = tuple(_ops.keys())
_consts = {"e": _e, "pi": _pi}
_ckeys = tuple(_consts.keys())


def matheval(expression):
    return postfix(infix_to_postfix(expression))


def postfix(expression):
    """
    Evaluate a postfix expression.
    Arguments:
        expression: The expression to evaluate. Should be a string or a
                    sequence of strings. In a string numbers and operators
                    should be separated by whitespace
    Returns:
        The result of the expression.
    """
    if isinstance(expression, str):
        expression = expression.split()
    stack = []
    for val in expression:
        if val in _okeys:
            n, op = _ops[val]
            if n > len(stack):
                raise ValueError(f"{expression} is not a valid postfix exp")
            args = stack[-n:]
            stack[-n:] = [op(*args)]
        elif val in _ckeys:
            stack.append(_consts[val])
        else:
            stack.append(float(val))
    return stack[-1]


class Stack:
    def __init__(self):
        self.items = []
        self.length = 0

    def push(self, val):
        self.items.append(val)
        self.length += 1

    def pop(self):
        if self.empty():  # pragma: no cover
            return None
        self.length -= 1
        return self.items.pop()

    def peek(self):
        if self.empty():  # pragma: no cover
            return None
        return self.items[0]

    def empty(self):
        return self.length == 0


precedence = {"*": 3, "/": 3, "+": 2, "-": 2, "(": 1}


def infix_to_postfix(tokens):
    if isinstance(tokens, str):
        tokens = tokens.split()

    postfix = []
    opstack = Stack()

    for token in tokens:
        if token.isidentifier() or token.isdigit():
            postfix.append(token)
        elif token == "(":
            opstack.push(token)
        elif token == ")":
            while True:
                temp = opstack.pop()
                if temp is None or temp == "(":
                    break
                elif not temp.isidentifier():
                    postfix.append(temp)
        elif token in _ops:
            if not opstack.empty():
                temp = opstack.peek()

                while (
                    not opstack.empty()
                    and precedence[temp] >= precedence[token]
                    and token.isidentifier()
                ):  # pragma: no cover
                    postfix.append(opstack.pop())
                    temp = opstack.peek()
            opstack.push(token)
        else:
            raise ValueError(
                f"{token} is invalid, "
                f"tip: white space between tokens `( 9` instead of (9"
            )

    while not opstack.empty():
        postfix.append(opstack.pop())

    return postfix
