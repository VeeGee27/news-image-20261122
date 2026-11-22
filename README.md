# The World in One Day — Sunday 22 November 2026

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/VeeGee27/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/VeeGee27/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A one-page newspaper front page for **Sunday 22 November 2026**: 39
verified stories across 8 regions, 3 hero stories, 13 illustrated cards,
a numbered world map, and a DATE CHECK box that keeps near-miss stories
from other days out of the record.

Every story is dated Sunday 22 November 2026 (UTC) and carries a
verification tag — CONFIRMED or REPORTED — with its source.

## Files

- `draw.py` — renders `entry.png` (1024×1024) with Pillow. Deterministic:
  two runs produce a byte-identical file.
- `entry.png` — the front page.
- `main.py` — entrypoint (stdlib only). Copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR` (or `/output`) and verifies the copy byte-for-byte.

## Build

```bash
python3 draw.py        # writes entry.png
python3 main.py        # copies entry.png to $MAKEFUN_OUTPUT_DIR or /output
```
