#!/usr/bin/env python3
"""news-image-20261122 v1 entrypoint (standard library only).

Copies the pre-rendered entry.png into the output directory and checks
the copy byte for byte. The grading container runs Python with the
standard library alone, so this file imports nothing else.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    with open(src, "rb") as f:
        want = f.read()
    with open(dst, "rb") as f:
        got = f.read()
    if want != got:
        print("copy mismatch: %d bytes vs %d bytes" % (len(want), len(got)),
              file=sys.stderr)
        return 1
    print("entry.png copied: %d bytes" % len(got))
    return 0


if __name__ == "__main__":
    sys.exit(main())
