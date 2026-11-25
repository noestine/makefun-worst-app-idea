"""The Worst App Idea Ever Pitched — make.fun entry.

Writes one sentence pitching the worst, most useless app imaginable to
/output/entry.txt, per the competition gate: UTF-8 text of 1-240 characters,
not only whitespace.

Standard library only. No network, no environment secrets, no randomness,
no arguments: the output is byte-identical on every run.
"""

import os
import sys

# The pitch: one clean sentence, a specific app, a deadpan founder's certainty,
# and a problem nobody on earth has (missing the exact moment a puddle dries up).
PITCH = (
    "PuddleWatch sends you a live alert the instant any puddle in your city "
    "dries up, so you never miss the exact moment a puddle stops being a puddle."
)

MIN_CHARS = 1
MAX_CHARS = 240
OUTPUT_DIR = "/output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "entry.txt")


def validate_entry(text):
    """Return True only if `text` passes the competition gate.

    The gate: a string of 1-240 characters, not only whitespace, on a single
    line, with no padding at either end. Anything else is rejected.
    """
    if not isinstance(text, str):
        return False
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        return False
    if not text.strip():
        return False
    if "\n" in text or "\r" in text:
        return False
    if text != text.strip():
        return False
    # One clean sentence, no padding: no doubled spaces inside, and the
    # sentence must actually end with a terminator. A pitch that trails off
    # or hides extra spacing reads as unfinished to the judge (criterion 4).
    if "  " in text:
        return False
    if text[-1] not in ".!?":
        return False
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def write_entry(output_dir=OUTPUT_DIR):
    """Validate the pitch and write it to <output_dir>/entry.txt.

    Returns the path written. Raises SystemExit(1) with a clear message on
    any failure instead of crashing with a bare traceback.
    """
    if not validate_entry(PITCH):
        print("error: pitch fails the entry gate (1-240 chars, one line)",
              file=sys.stderr)
        raise SystemExit(1)
    try:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "entry.txt")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(PITCH)
    except OSError as exc:
        print(f"error: cannot write entry: {exc}", file=sys.stderr)
        raise SystemExit(1)
    return path


def main():
    # MAKEFUN_OUTPUT_DIR exists only so the test suite can point the program
    # at a scratch directory; the graded sandbox runs with the default /output.
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", OUTPUT_DIR)
    path = write_entry(output_dir)
    print(f"wrote {path} ({len(PITCH)} chars)")


if __name__ == "__main__":
    main()
