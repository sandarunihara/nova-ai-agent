"""
src/tools/math_solver.py
Safe expression evaluator and math expression extraction engine for NOVA.
"""

import ast
import operator
import re

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr: str):
    """Evaluates a restricted arithmetic expression safely using AST (no eval())."""
    try:
        expr = expr.strip().replace("=", "").strip()
        node = ast.parse(expr, mode="eval").body
        
        def _eval(n):
            if isinstance(n, ast.BinOp):
                return _ALLOWED_OPS[type(n.op)](_eval(n.left), _eval(n.right))
            if isinstance(n, ast.UnaryOp):
                return _ALLOWED_OPS[type(n.op)](_eval(n.operand))
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("Disallowed expression structure")
            
        return _eval(node)
    except Exception as e:
        raise ValueError(f"Invalid math expression: {e}")


def extract_and_solve_math(user_query: str, llm_client) -> tuple[str, float | None]:
    """
    Asks the LLM to extract a clean Python math expression from a word problem,
    safely evaluates it, and returns both the expression and the exact computed number.
    """
    extraction_prompt = [
        {
            "role": "system",
            "content": (
                "You are a precision math assistant. Read the user's math word problem "
                "and output ONLY a valid Python mathematical expression to solve it. "
                "For compound interest use: Principal * (1 + rate/quarters)**(quarters * years). "
                "Do not include text, markdown fences, words, or explanations — ONLY the raw expression (e.g., 10000 * (1 + 0.06/4)**(4*3))."
            )
        },
        {"role": "user", "content": user_query}
    ]
    
    messages = extraction_prompt
    raw_expr = llm_client.generate(messages, is_factual_rag=True)
    
    # Clean up expression text
    clean_expr = re.sub(r'[^0-9+\-*/().*+\s]', '', raw_expr).strip()
    
    try:
        result = safe_eval(clean_expr)
        return clean_expr, result
    except Exception:
        match = re.search(r'([\d\s+\-*/().*]+)', raw_expr)
        if match:
            try:
                fallback_expr = match.group(1).strip()
                result = safe_eval(fallback_expr)
                return fallback_expr, result
            except Exception:
                pass
        return raw_expr, None