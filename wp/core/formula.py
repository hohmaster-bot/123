"""Small SAFE expression evaluator (RULES/buffs.md "Formulas", package 14 C). No eval / exec.

Grammar: numbers (whole or decimal), variables, + - * / with the usual precedence, unary minus,
parentheses, functions min(a, b, ...), max(a, b, ...), floor(x).
  - + - * are exact (fractions);
  - / is INTEGER division rounding DOWN (towards minus infinity): 7 / 2 = 3, -7 / 2 = -4;
  - the final result is rounded DOWN to a whole number (floor): 2.5 -> 2, -2.5 -> -3.
Variables (VARIABLES): level (also lvl), str_mod, dex_mod, con_mod, int_mod, wis_mod, cha_mod, bab.
validate(expr) raises FormulaError with a clear reason; evaluate(expr, values) returns an int.
"""
import math
from fractions import Fraction

VARIABLES = ("level", "lvl", "str_mod", "dex_mod", "con_mod", "int_mod", "wis_mod", "cha_mod", "bab")
FUNCTIONS = ("min", "max", "floor")
MAX_LENGTH = 200


class FormulaError(ValueError):
    pass


def _tokens(text):
    out = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == "."):
                j += 1
            num = text[i:j]
            if num.count(".") > 1 or num == ".":
                raise FormulaError("bad number %r" % num)
            out.append(("num", Fraction(num)))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            out.append(("name", text[i:j]))
            i = j
        elif c in "+-*/(),":
            out.append(("op", c))
            i += 1
        else:
            raise FormulaError("character %r is not allowed" % c)
    return out


class _Parser:
    def __init__(self, tokens, values):
        self.t = tokens
        self.i = 0
        self.values = values

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self, kind=None, val=None):
        tok = self.peek()
        if tok[0] is None or (kind and tok[0] != kind) or (val and tok[1] != val):
            raise FormulaError("expected %s" % (val or kind or "more"))
        self.i += 1
        return tok

    def expr(self):
        v = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            r = self.term()
            v = v + r if op == "+" else v - r
        return v

    def term(self):
        v = self.unary()
        while self.peek() in (("op", "*"), ("op", "/")):
            op = self.take()[1]
            r = self.unary()
            if op == "*":
                v = v * r
            else:
                if r == 0:
                    raise FormulaError("division by zero")
                v = Fraction(math.floor(v / r))
        return v

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take()
            return -self.unary()
        if self.peek() == ("op", "+"):
            self.take()
            return self.unary()
        return self.atom()

    def atom(self):
        kind, val = self.peek()
        if kind == "num":
            self.take()
            return val
        if kind == "op" and val == "(":
            self.take()
            v = self.expr()
            self.take("op", ")")
            return v
        if kind == "name":
            self.take()
            if self.peek() == ("op", "("):
                if val not in FUNCTIONS:
                    raise FormulaError("unknown function %r (allowed: %s)" % (val, ", ".join(FUNCTIONS)))
                self.take()
                args = [self.expr()]
                while self.peek() == ("op", ","):
                    self.take()
                    args.append(self.expr())
                self.take("op", ")")
                if val == "floor":
                    if len(args) != 1:
                        raise FormulaError("floor takes one value")
                    return Fraction(math.floor(args[0]))
                return min(args) if val == "min" else max(args)
            if val not in VARIABLES:
                raise FormulaError("unknown variable %r (allowed: %s)" % (val, ", ".join(VARIABLES)))
            return Fraction(int(self.values.get("level" if val == "lvl" else val, 0)))
        raise FormulaError("unexpected end" if kind is None else "unexpected %r" % (val,))


def evaluate(text, values=None):
    """The formula's value as an int (rounded down). values: {"level": 4, "con_mod": 3, ...}."""
    if not isinstance(text, str) or not text.strip():
        raise FormulaError("empty formula")
    if len(text) > MAX_LENGTH:
        raise FormulaError("formula too long (max %d characters)" % MAX_LENGTH)
    p = _Parser(_tokens(text), values or {})
    v = p.expr()
    if p.i != len(p.t):
        raise FormulaError("unexpected %r" % (p.t[p.i][1],))
    return int(math.floor(v))


def validate(text):
    """Raise FormulaError when the formula is not valid (all variables count as 0 for the check)."""
    evaluate(text, {name: 1 for name in VARIABLES})
