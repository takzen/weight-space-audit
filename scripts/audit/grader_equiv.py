"""Shows how the authors' grader treats answers that are mathematically equal but written differently."""
import sys

sys.path.insert(0, "/mnt/c/projects/art/qwen-sampling-control/scripts")
import mathgrade as Q  # noqa: E402

B = chr(92)
CASES = [("5", "5"), ("5", "6"), (B + "frac{1}{2}", "0.5"), ("0.5", B + "frac{1}{2}"), (B + "frac12", B + "frac{1}{2}"),
         ("x=5", "5"), ("5" + B + "text{ cm}", "5"), ("50" + B + "%", "50"), ("3.0", "3"), ("1,000", "1000"),
         (B + "dfrac{1}{2}", B + "frac{1}{2}"), ("(1,2)", "(1, 2)"), (B + "pi", "3.14159265")]
for pred, gold in CASES:
    print(f"pred {pred!r:28} gold {gold!r:22} -> {Q.is_correct(pred, gold)}")
