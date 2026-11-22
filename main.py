#!/usr/bin/env python3
"""news-image-20261122 — entrypoint.

The front page is pre-rendered by draw.py at build time (entry.png,
1024x1024, deterministic). This entrypoint only moves that file into
the directory the runner provides and proves the copy is identical.

Stdlib only: os, shutil, sys, hashlib.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(SRC):
        print("missing entry.png next to main.py", file=sys.stderr)
        return 1
    shutil.copyfile(SRC, dst)
    src_hash, dst_hash = _sha256(SRC), _sha256(dst)
    if src_hash != dst_hash:
        print("byte-for-byte verification FAILED", file=sys.stderr)
        return 1
    size = os.path.getsize(dst)
    print("entry.png -> %s (%d bytes, sha256 %s)" % (dst, size, dst_hash))
    return 0


if __name__ == "__main__":
    sys.exit(main())
