"""
src/tools/math_solver.py
Safe expression evaluator and math expression extraction engine for NOVA.
Supports arithmetic operators and whitelisted math.* functions.
"""

import ast
import math
import operator
import re

# --- Safe AST-based evaluator ---

_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_ALLOWED_UNARY_OPS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Whitelisted math functions
_ALLOWED_MATH_FUNCS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "radians": math.radians,
    "degrees": math.degrees,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "factorial": math.factorial,
    "ceil": math.ceil,
    "floor": math.floor,
    "abs": abs,
    "comb": math.comb,
    "perm": math.perm,
    # Aliases — the LLM may generate these longer names
    "combinations": math.comb,
    "permutations": math.perm,
}

# Whitelisted math constants
_ALLOWED_MATH_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def safe_eval(expr: str):
    """
    Evaluates a restricted arithmetic expression safely using AST.
    Supports: +, -, *, /, **, //, %, math.sqrt(), math.sin(), math.cos(),
    math.tan(), math.radians(), math.log(), math.factorial(), math.pi, math.e, abs().
    """
    try:
        expr = expr.strip().rstrip("=").strip()
        # Normalize: allow 'import math' lines or 'math.' prefix usage
        expr = expr.replace("import math", "").strip()
        # Handle multi-line — take the last non-empty line as the expression
        lines = [l.strip() for l in expr.split("\n") if l.strip()]
        if lines:
            expr = lines[-1]

        node = ast.parse(expr, mode="eval").body
        return _eval_node(node)
    except Exception as e:
        raise ValueError(f"Invalid math expression: {e}")


def _eval_node(node):
    """Recursively evaluate an AST node against the whitelist."""

    # Numeric constants: 42, 3.14
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    # Binary operations: a + b, a * b, a ** b
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BIN_OPS:
            raise ValueError(f"Disallowed binary operator: {op_type.__name__}")
        return _ALLOWED_BIN_OPS[op_type](_eval_node(node.left), _eval_node(node.right))

    # Unary operations: -x, +x
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPS:
            raise ValueError(f"Disallowed unary operator: {op_type.__name__}")
        return _ALLOWED_UNARY_OPS[op_type](_eval_node(node.operand))

    # Function calls: math.sqrt(x), abs(x), sqrt(x)
    if isinstance(node, ast.Call):
        func_name = _get_func_name(node.func)
        if func_name is None or func_name not in _ALLOWED_MATH_FUNCS:
            raise ValueError(f"Disallowed function: {func_name}")
        if len(node.args) < 1 or len(node.args) > 2:
            raise ValueError(f"Function {func_name} expects 1-2 arguments, got {len(node.args)}")
        args = [_eval_node(a) for a in node.args]
        return _ALLOWED_MATH_FUNCS[func_name](*args)

    # Attribute access for constants: math.pi, math.e
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "math":
            if node.attr in _ALLOWED_MATH_CONSTANTS:
                return _ALLOWED_MATH_CONSTANTS[node.attr]
            raise ValueError(f"Disallowed math constant: {node.attr}")
        raise ValueError(f"Disallowed attribute access")

    # Bare name for constants: pi, e (without math. prefix)
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_MATH_CONSTANTS:
            return _ALLOWED_MATH_CONSTANTS[node.id]
        if node.id in _ALLOWED_MATH_FUNCS:
            # This handles cases where the name is used without being called
            raise ValueError(f"Function '{node.id}' must be called with arguments")
        raise ValueError(f"Disallowed name: {node.id}")

    raise ValueError(f"Disallowed expression structure: {type(node).__name__}")


def _get_func_name(node) -> str | None:
    """Extract function name from a Call node (handles math.func and bare func)."""
    # math.sqrt(x)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == "math":
            return node.attr
        return None
    # sqrt(x), abs(x)
    if isinstance(node, ast.Name):
        return node.id
    return None


# --- Math expression extraction prompt ---

_EXTRACTION_SYSTEM_PROMPT = (
    "You are a precision math-to-code translator. "
    "Read the user's math word problem and output ONLY a single valid Python arithmetic expression that solves it. "
    "You may use: +, -, *, /, **, //, %, math.sqrt(), math.sin(), math.cos(), math.tan(), math.radians(), "
    "math.log(), math.factorial(), math.pi, math.e, abs().\n\n"
    "CRITICAL RULES:\n"
    "- Output ONLY the raw Python expression. No text, no markdown, no explanation, no variable names.\n"
    "- The expression must evaluate to the final numerical answer directly.\n"
    "- For trigonometric functions, always convert degrees to radians using math.radians().\n"
    "- For probability, use fractions (e.g., (7/20) * (6/19)).\n"
    "- For compound interest: P * (1 + r/n)**(n*t)\n"
    "- For exponential growth/decay: initial * rate**(time/period)\n"
    "- For work/rate problems: 1 / (1/a - 1/b) or 1 / (1/a + 1/b)\n\n"
    "EXAMPLES:\n\n"
    "Problem: If $10,000 is invested at 6% compounded quarterly for 3 years, what is the total?\n"
    "Expression: 10000 * (1 + 0.06/4)**(4*3)\n\n"
    "Problem: From 50 meters away, angle of elevation to top is 60 degrees. Height?\n"
    "Expression: 50 * math.tan(math.radians(60))\n\n"
    "Problem: A bag has 5 red, 7 blue, 8 green marbles. Two drawn without replacement. Probability both blue?\n"
    "Expression: (7/20) * (6/19)\n\n"
    "Problem: Bacteria starts at 500, triples every 4 hours. How many after 24 hours?\n"
    "Expression: 500 * 3**(24/4)\n\n"
    "Problem: Pipe A fills in 6 hours, Pipe B drains in 9 hours. Both open, how long to fill?\n"
    "Expression: 1 / (1/6 - 1/9)\n\n"
    "Problem: Ladder 25 feet, base 7 feet from wall. Height on wall?\n"
    "Expression: math.sqrt(25**2 - 7**2)\n\n"
    "Problem: Garden bounded by river, 100m fencing for 3 sides. Max area? (width=100-2*length, optimize)\n"
    "Expression: 25 * (100 - 2*25)\n\n"
    "Problem: What is 5 factorial?\n"
    "Expression: math.factorial(5)\n\n"
    "Problem: Find the hypotenuse of a right triangle with legs 3 and 4.\n"
    "Expression: math.sqrt(3**2 + 4**2)\n\n"
    "Problem: What is the area of a circle with radius 7?\n"
    "Expression: math.pi * 7**2\n\n"
    "Problem: A committee of 4 from 6 engineers and 5 scientists, exactly 2 of each. How many committees?\n"
    "Expression: math.comb(6, 2) * math.comb(5, 2)\n\n"
    "Problem: How many ways to arrange 5 books on a shelf?\n"
    "Expression: math.factorial(5)\n\n"
    "Problem: Carbon-14 half-life is 5730 years. An artifact lost 30% of its C-14 (70% remains). How old?\n"
    "Expression: math.log(0.7) / math.log(0.5) * 5730\n\n"
    "Now solve the following problem. Output ONLY the Python expression."
)


def extract_and_solve_math(user_query: str, llm_client) -> tuple[str, float | None]:
    """
    Asks the LLM to extract a clean Python math expression from a word problem,
    safely evaluates it, and returns both the expression and the exact computed number.
    Includes one retry with error feedback if the first extraction fails.
    """
    messages = [
        {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    raw_expr = llm_client.generate(messages, is_factual_rag=True)
    clean_expr = _clean_expression(raw_expr)

    # First attempt
    eval_error = None
    try:
        result = safe_eval(clean_expr)
        return clean_expr, result
    except Exception as e:
        eval_error = e

    # Retry: feed the error back to the LLM and ask it to fix the expression
    retry_messages = [
        {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": raw_expr},
        {
            "role": "user",
            "content": (
                f"ERROR: The expression '{clean_expr}' failed to evaluate: {eval_error}\n"
                "Please output a corrected, valid Python arithmetic expression. "
                "ONLY the expression, nothing else."
            )
        }
    ]

    retry_expr = llm_client.generate(retry_messages, is_factual_rag=True)
    clean_retry = _clean_expression(retry_expr)

    try:
        result = safe_eval(clean_retry)
        return clean_retry, result
    except Exception:
        pass

    # Final fallback: try to find any evaluable sub-expression in the original output
    match = re.search(r'([\d\s+\-*/().**]+)', raw_expr)
    if match:
        try:
            fallback_expr = match.group(1).strip()
            result = safe_eval(fallback_expr)
            return fallback_expr, result
        except Exception:
            pass

    return raw_expr, None


def _clean_expression(raw: str) -> str:
    """Clean LLM output to extract just the math expression."""
    # Remove markdown code fences
    raw = re.sub(r'```(?:python)?\s*', '', raw)
    raw = re.sub(r'```', '', raw)

    # Remove "Expression:" prefix if present
    raw = re.sub(r'^(?:Expression|Result|Answer|Output)\s*:\s*', '', raw.strip(), flags=re.IGNORECASE)

    # Take only the first non-empty line (LLM might add explanation after)
    lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
    if lines:
        raw = lines[0]

    # Remove any trailing text after the expression (e.g., "# comment")
    raw = re.sub(r'#.*$', '', raw).strip()

    # Remove any remaining non-math characters except allowed ones
    # Allow: digits, operators, parentheses, dots, spaces, 'math', function names
    # Don't aggressively strip — the AST parser will validate
    return raw.strip()