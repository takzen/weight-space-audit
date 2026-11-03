"""Prints the 0.8B column of the benchmark tables in the saved model card. Parses text only; runs nothing from the card."""
import re
import sys
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")


class T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell, self.in_cell, self.span = [], None, "", False, 1

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        if tag in ("td", "th"):
            self.in_cell, self.cell = True, ""
            self.span = int(dict(attrs).get("colspan", 1))

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None:
            self.row += [self.cell.strip()] * self.span
            self.in_cell = False
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.in_cell:
            self.cell += data


def show(a, b):
    text = "\n".join(lines[a:b])
    for i, m in enumerate(re.finditer(r"<table.*?</table>", text, re.S)):
        p = T()
        p.feed(m.group(0))
        rows = [r for r in p.rows if r]
        if not rows:
            continue
        print(f"--- table {i} near line {a + text[:m.start()].count(chr(10)) + 1}: {len(rows)} rows")
        for r in rows[:2]:
            print("HEAD", r[:12])
        heads = [j for j, h in enumerate(rows[0]) if "0.8B" in h]
        for r in rows:
            if heads and len(r) > max(heads):
                print(r[0][:44], "|", [r[j] for j in heads])


show(60, 300)
