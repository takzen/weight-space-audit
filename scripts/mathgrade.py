"""Prompt building and answer grading, copied from the authors' exp8_math/code/mathqa.py
(github.com/RikiyaT/lm_understand-logs, their scripts are MIT licensed) so that scores are directly comparable.
The functions below are unchanged apart from removing the path handling for math-verify.
"""
import functools
import re
import threading

import math_verify

INSTRUCTION = "Please reason step by step, and put your final answer within \\boxed{}."


def build_prompt(problem):
    """The user turn: the problem, a newline, Qwen's math instruction."""
    return problem + "\n" + INSTRUCTION


def answer_text(text):
    """The text the extraction reads: a stray reasoning block cut off (up to the last '</think>')."""
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    return text


_BOX_FORMS = re.compile(r"\\boxed|\\fbox")


def _box_at(text, idx):
    """the content of the box that starts at text[idx] ('\\boxed' or '\\fbox'), or None."""
    key = "\\boxed" if text.startswith("\\boxed", idx) else "\\fbox"
    rest = text[idx + len(key):]
    r = rest.lstrip()
    if r.startswith("{"):   # brace matched, as last_boxed_only_string
        depth = 0
        for k, ch in enumerate(r):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    out = r[1:k].strip()
                    return out or None
        return None          # not closed (e.g. a response cut inside the box)
    if key == "\\boxed" and rest.startswith(" "):   # '\\boxed 5': up to the next '$' or line end (Qwen's reading)
        out = rest.strip().split("$")[0].split("\n")[0].strip()
        return out or None
    return None


def last_boxed(text):
    """The content of the last box of a text, or None."""
    idx = text.rfind("\\boxed")
    if idx < 0:
        idx = text.rfind("\\fbox")
        if idx < 0:
            return None
    return _box_at(text, idx)


def extract(text):
    """(answer or None, number of boxes in the text)."""
    t = answer_text(text)
    return last_boxed(t), len(_BOX_FORMS.findall(t))


def _timeouts():
    """math-verify's timeouts use signal.alarm, which works only in the main thread."""
    return 5 if threading.current_thread() is threading.main_thread() else None


@functools.lru_cache(maxsize=1 << 16)
def _parsed(s, to):
    return math_verify.parse("\\boxed{" + s + "}", parsing_timeout=to)


def is_correct(pred, gold):
    """math-verify equivalence of a boxed answer and the gold answer (False for no answer / unparseable gold)."""
    if pred is None or gold is None:
        return False
    to = _timeouts()
    g, p = _parsed(gold, to), _parsed(pred, to)
    if not g or not p:
        return False
    try:
        return bool(math_verify.verify(g, p, timeout_seconds=to))
    except Exception:  # noqa: BLE001
        return False
