#!/bin/bash
# Renders the image cards to PNG with headless Chrome, for the link preview and for posts: render_cards.sh <out_dir> [<results_dir>] [--final]
# Runs in Git Bash on Windows. Chrome uses the CPU here, so it doesn't compete with a measurement on the GPU.
set -u
OUT=$1; RESULTS=${2:-}; FINAL=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
TMP=$(mktemp -d)
mkdir -p "$OUT"
for kind in chart map; do
  for lang in en pl; do
    python "$(cygpath -w "$HERE/build_page.py")" "$(cygpath -w "$TMP/$kind-$lang.html")" ${RESULTS:+"$(cygpath -w "$RESULTS")"} $FINAL "--card=$kind" "--lang=$lang" > /dev/null || exit 1
    "$CHROME" --headless=new --disable-gpu --no-first-run --hide-scrollbars --user-data-dir="$(cygpath -w "$TMP/profile")" \
      --force-device-scale-factor=2 --window-size=1200,800 --virtual-time-budget=4000 \
      --screenshot="$(cygpath -w "$OUT/${kind}_$lang.png")" "file:///$(cygpath -m "$TMP/$kind-$lang.html")" > /dev/null 2>&1
  done
done
python "$(cygpath -w "$HERE/build_page.py")" "$(cygpath -w "$TMP/og.html")" ${RESULTS:+"$(cygpath -w "$RESULTS")"} $FINAL --card=og --lang=en > /dev/null || exit 1
"$CHROME" --headless=new --disable-gpu --no-first-run --hide-scrollbars --user-data-dir="$(cygpath -w "$TMP/profile")" \
  --force-device-scale-factor=2 --window-size=1200,630 --virtual-time-budget=4000 \
  --screenshot="$(cygpath -w "$OUT/og.png")" "file:///$(cygpath -m "$TMP/og.html")" > /dev/null 2>&1
rm -rf "$TMP" "$HERE/__pycache__"
ls -la "$OUT"
