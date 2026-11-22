# Sunday 22 November 2026: 36 stories, 8 regions — COP31 collapses, 186-drone barrage, Mar-a-Lago peace talks

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/VeeGee27/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/VeeGee27/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One image summing up the world's news of Sunday 22 November 2026: 36 dated
stories across 8 regions — COP31 collapses in Antalya, Russia fires 186
drones at Ukraine overnight, Trump hosts Zelenskyy at Mar-a-Lago.

## How it is built

- `draw.py` (Pillow, build time only) renders `entry.png` at 1024x1024:
  serif masthead, 6-number stat strip, region bar, 3 heroes + 10 illustrated
  mids (13 drawn stories), numbered world map, 23-brief list, red DATE CHECK
  box, verification tags on every hero and mid, warm newsprint background.
- `main.py` (standard library only) copies the pre-rendered `entry.png` to
  `$MAKEFUN_OUTPUT_DIR` (or `/output`) and verifies the copy byte for byte.

## Run it

```sh
python3 draw.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see LICENSE.
