"""
Standalone unit tests for the enhanced safe_eval math evaluator.
No pytest required — uses plain assertions.
"""

import math
import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.math_solver import safe_eval

passed = 0
failed = 0
errors = []


def test(name, expression, expected, tolerance=1e-10):
    global passed, failed, errors
    try:
        result = safe_eval(expression)
        if abs(result - expected) < tolerance:
            passed += 1
            print(f"  ✅ {name}")
        else:
            failed += 1
            msg = f"  ❌ {name}: expected {expected}, got {result}"
            print(msg)
            errors.append(msg)
    except Exception as e:
        failed += 1
        msg = f"  ❌ {name}: EXCEPTION: {e}"
        print(msg)
        errors.append(msg)


def test_raises(name, expression):
    global passed, failed, errors
    try:
        safe_eval(expression)
        failed += 1
        msg = f"  ❌ {name}: expected ValueError but got no exception"
        print(msg)
        errors.append(msg)
    except ValueError:
        passed += 1
        print(f"  ✅ {name} (correctly blocked)")
    except Exception as e:
        failed += 1
        msg = f"  ❌ {name}: expected ValueError but got {type(e).__name__}: {e}"
        print(msg)
        errors.append(msg)


print("\n" + "=" * 60)
print("  NOVA Math Solver — Unit Tests")
print("=" * 60)

# --- Basic Arithmetic ---
print("\n📐 Basic Arithmetic:")
test("Addition", "2 + 3", 5)
test("Subtraction", "10 - 4", 6)
test("Multiplication", "6 * 7", 42)
test("Division", "15 / 3", 5.0)
test("Power", "2 ** 10", 1024)
test("Floor Division", "17 // 3", 5)
test("Modulo", "17 % 5", 2)
test("Negative", "-5 + 3", -2)
test("Nested Parens", "(2 + 3) * (4 - 1)", 15)

# --- Math Functions ---
print("\n📏 Math Functions:")
test("math.sqrt(144)", "math.sqrt(144)", 12.0)
test("sqrt(144) bare", "sqrt(144)", 12.0)
test("sin(30°)", "math.sin(math.radians(30))", 0.5)
test("cos(60°)", "math.cos(math.radians(60))", 0.5)
test("tan(45°)", "math.tan(math.radians(45))", 1.0)
test("50*tan(60°)", "50 * math.tan(math.radians(60))", 50 * math.sqrt(3))
test("log(e)", "math.log(math.e)", 1.0)
test("log10(1000)", "math.log10(1000)", 3.0)
test("factorial(5)", "math.factorial(5)", 120)
test("abs(-42)", "abs(-42)", 42)
test("pi * 7^2", "math.pi * 7**2", math.pi * 49)
test("e constant", "math.e", math.e)

# --- The 7 Word Problem Expressions ---
print("\n🎯 Word Problem Expressions (the 7 failing cases):")
test("Compound Interest", "10000 * (1 + 0.06/4)**(4*3)", 11956.1817, tolerance=0.01)
test("Angle of Elevation", "50 * math.tan(math.radians(60))", 86.6025, tolerance=0.01)
test("Probability (both blue)", "(7/20) * (6/19)", 42/380)
test("Bacterial Growth", "500 * 3**(24/4)", 500 * 3**6)
test("Pipe Work Rate", "1 / (1/6 - 1/9)", 18.0)
test("Ladder Pythagorean", "math.sqrt(25**2 - 7**2)", 24.0)
test("Max Garden Area", "25 * (100 - 2*25)", 1250)

# --- Security ---
print("\n🔒 Security (should be blocked):")
test_raises("Block __import__", "__import__('os').system('echo hacked')")
test_raises("Block open()", "open('/etc/passwd').read()")
test_raises("Block arbitrary names", "x + 1")
test_raises("Block eval()", "eval('1+1')")

# --- Edge Cases ---
print("\n🔧 Edge Cases:")
test("Trailing equals", "2 + 3 =", 5)
test("Multiline import+expr", "import math\n50 * math.tan(math.radians(60))", 50 * math.sqrt(3))

# --- Summary ---
print("\n" + "=" * 60)
total = passed + failed
print(f"  Results: {passed}/{total} passed, {failed} failed")
if errors:
    print("\n  Failures:")
    for e in errors:
        print(f"    {e}")
print("=" * 60 + "\n")

sys.exit(0 if failed == 0 else 1)
