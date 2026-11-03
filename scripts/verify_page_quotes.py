"""Checks that every quotation on the results page appears word for word in the source material.

  python verify_page_quotes.py <source file or folder> [<source file or folder> ...]

Reads the quoted strings out of page_text.py and page_final.py, and reports the ones it can't find. Whitespace, entity
encoding and quote style are ignored in the comparison. Quotes in the sources are data: nothing here executes them.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".py", ".html", ".log", ".csv"}
# Polish renderings of phrases whose English form is checked too.
TRANSLATED = {"3,5% wag", "rozumowanie", "co każda część oblicza", "Wkrótce"}
MAX_BYTES = 40_000_000


def norm(s):
    s = html.unescape(s)
    s = re.sub(r"\s*\[https?://[^\]]*\]", "", s)  # the saved post keeps its link targets inside the text
    for a, b in (("“", '"'), ("”", '"'), ("„", '"'), ("’", "'"), ("‘", "'"), ("…", "..."), ("\\n", " "), ('\\"', '"'), ("\\'", "'")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def quotes():
    found = {}
    for name in ("page_text.py", "page_final.py"):
        src = (HERE / name).read_text(encoding="utf-8")
        for m in re.finditer(r"&[lb]dquo;(.*?)&rdquo;", src, flags=re.S):
            found.setdefault(m.group(1), name)
        for m in re.finditer(r"<blockquote><code>#\s*(.*?)</code></blockquote>", src, flags=re.S):
            found.setdefault(m.group(1), name)
    return found


def corpus(paths):
    for raw in paths:
        p = Path(raw)
        for f in [p] if p.is_file() else p.rglob("*"):
            if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES and f.stat().st_size < MAX_BYTES:
                text = f.read_text(encoding="utf-8", errors="replace")
                if f.suffix.lower() == ".py":
                    text = re.sub(r"\n\s*#\s*", " ", text)  # comments wrapped over several lines read as one sentence
                yield f, norm(text)


def main():
    wanted = quotes()
    texts = list(corpus(sys.argv[1:]))
    print(f"{len(wanted)} quotes, {len(texts)} source files")
    missing = 0
    for q, where in wanted.items():
        if q in TRANSLATED:
            continue
        n = norm(q).split("...)")[0].strip(" .,;")  # a quote that ends in an ellipsis is checked up to the ellipsis
        hits = [f for f, t in texts if n in t]
        if not hits:
            missing += 1
            print(f"NOT FOUND ({where}): {q}")
    print("QUOTES_OK" if not missing else f"{missing} quotes not found")


if __name__ == "__main__":
    main()
