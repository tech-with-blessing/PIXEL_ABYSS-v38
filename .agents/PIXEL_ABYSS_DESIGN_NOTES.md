# PIXEL ABYSS — Master Level Design Reference
*Synthesized from studying levels 1, 2, 3, 4, 9, 10, 12*
*This file is the single source of truth — send it when requesting level generation*

---

## SECTION 1 — ENGINE RULES (non-negotiable)

### Coordinate system
- World: x **-2048 to +1920**, y **-2048 to +1920** (positive Y = down)
- All `block` x/y must be **exact multiples of 64**
- Non-block objects (enemies, decos, trees, water, platforms) can use non-multiples
- Block size is always `"size": "big"`, `"width": 64, "height": 64`

### Required header (always first two objects)
```json
{"type": "entity settings",
 "Torch":   {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":50, "attack_power":4,"health":80},
 "Pawn":    {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":40, "attack_power":5,"health":70},
 "Warrior": {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":50, "attack_power":6,"health":90},
 "TNT":     {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":300,"attack_down":300,"attack_range":600,"attack_power":8,"health":100},
 "Archer":  {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":300,"attack_down":300,"attack_range":600,"attack_power":7,"health":100}}

{"x":0,"y":-64,"points":[[0,64],[0,-64]],"width":64,"height":64,"type":"start"}
```

### Overlap rules
- Two foreground blocks **cannot share the same (x,y)** — always deduplicate before saving
- Background blocks (`"perspective":"back"`) cannot share coords with any other block
- Enemies/decos/trees must be placed **above** terrain, never inside fore blocks
- Water cannot overlap foreground blocks

### Solid bottom floor (mandatory)
Every level must have **two full-width rows** at or near max y with no gaps:
```python
for x in range(-2048, 1984, 64):
    items.append(blk(x, 1856, "stone"))
    items.append(blk(x, 1920, "stone"))
```

---

## SECTION 2 — ALL OBJECT SCHEMAS

### Block (foreground)
```json
{"x":0,"y":512,"width":64,"height":64,"type":"block","name":"stone","size":"big"}
```

### Block (background / decorative wall)
```json
{"x":64,"y":512,"width":64,"height":64,"type":"block","name":"stone_inside","size":"big","perspective":"back"}
```

### Enemy
```json
{"x":-512,"y":-64,"width":42,"height":58,"type":"enemy","name":"Archer","color":"Yellow"}
```
**Confirmed sizes from real levels:**
| Enemy | Width | Height |
|-------|-------|--------|
| Pawn | 32 | 52 |
| Warrior | 40 | 58 |
| Archer | 42 | 58 |
| TNT | 40 | 58 |
| Torch | 40 | 58 |

### Moving Platform — Horizontal (Schema A, most common)
```json
{"x":-448,"y":320,"width":100,"height":20,"moving":true,"direction":[-1,0],
 "type":"moving_platform","speed":100,"min_x":-1088,"max_x":-384,"path":[[0,0]],"color":[50,50,255]}
```

### Moving Platform — Horizontal with dest (Schema B, also valid)
```json
{"x":-192,"y":256,"width":100,"height":20,"moving":true,"direction":[-1,0],
 "type":"moving_platform","speed":150,"dest_x":[-1088,1024],"dest_y":[256,256],
 "min_x":-1088,"max_x":1024,"path":[[0,0]],"color":[50,50,255]}
```

### Moving Platform — Vertical (Schema C)
```json
{"x":1152,"y":-448,"width":100,"height":20,"moving":true,"direction":[1,1],
 "type":"moving_platform","speed":100,"dest_x":[1152,1216],"dest_y":[-448,192],
 "min_x":1152,"max_x":1216,"path":[[0,0]],"color":[50,50,255]}
```
- Speed range: 100 (default) to 200 (fast/dramatic)
- Color always `[50,50,255]` or `[50,50,200]`

### Water Tile (always 64×64 — never large rectangles)
```json
{"x":1088,"y":-832,"width":64,"height":64,"type":"water","water_type":"toxic",
 "color":[70,220,70],"flow":1,"rise":true}
```
**Water types and colors used in real levels:**
| Type | Color | Use |
|------|-------|-----|
| `lava` | `[255,80,0]` | Volcanic pits, deep zones |
| `healing` | `[0,200,100]` | Safe pools, reward areas |
| `normal` | `[50,50,255]` | Rivers, lakes, seas |
| `current` | `[80,130,200]` | Rivers with flow direction |
| `toxic` | `[70,220,70]` | Caves, swamps, dungeons |

### Spawn Point
```json
{"x":0,"y":-64,"width":64,"height":64,"interval":5,"limit":5,
 "type":"spawn_point","entities":[["Pawn","Red"]]}
```
- Rare (only levels 9 and 12 use them). Use for one specific respawn location.
- Keep `entities` to 1–2 types, `limit` 5–10, `interval` 4–6

### Tree
```json
{"x":-640,"y":-896,"width":50,"height":50,"type":"tree","name":"tree","size":"big"}
```
Place at `y = terrain_surface_y - 50` (just above ground).

### Deco
```json
{"x":-576,"y":-64,"width":50,"height":50,"type":"deco","name":"shrub1","size":"big"}
```
**Deco names confirmed across real levels:**
`bone`, `exit`, `arrow`, `grass1`, `grass2`, `shrub1`, `shrub2`, `shrub3`,
`shroom1`, `shroom2`, `shroom3`, `pumpkin1`, `pumpkin2`, `scare_crow`,
`mud`, `sand`, `window`, `box1`, `box4`

`exit` appears in almost every level — always include 1–2.

### Treasure
```json
{"x":1856,"y":-576,"width":64,"height":64,"type":"treasure","name":"red"}
```
Colors: `red`, `pink`, `green`, `yellow`
Place in clusters of 2–4 at landmark spots, not scattered randomly.

---

## SECTION 3 — BLOCK PALETTE SYSTEM

Append `_N` to any block base name to recolor it. All blocks in a section should share one palette number.

| N | Theme | Best for |
|---|-------|---------|
| (none) | Default green/brown | Forests, caves, jungles, overworld |
| 2 | Dark purple-navy | Underground dungeons, void zones |
| 3 | Sandy warm | Desert ruins, ancient temples |
| 5 | Snow/ice | Frozen peaks, tundra, arctic |
| 6 | Nether/scorched | Volcanoes, lava zones, hellfire |
| 7 | Obsidian/void | Deep abyss, end-game zones |
| 8 | Autumn orange | Forest ruins, harvest lands |

**Mixing palettes is valid and used in real levels:**
- Level 9: no palette (pure default) — raw cave feel
- Level 10: palette 3 + 5 + plain `ice` blocks
- Level 12: palette 8 dominant + palette 3 accent patches
- Level 1: palettes 1+2+3+5 all mixed

Rule: one dominant palette (80%+), one accent for contrast patches.

**Special blocks (no palette suffix):**
- `ice` — used as primary terrain in level 10 (424 blocks). Works as cave ceiling, walls, floors.
- `mud` — organic fill, heavy in level 9 cave (36 blocks), used alongside grass_inside
- `box1`, `box4` — crate blocks, used as mid-terrain obstacles
- `brick_small_6` — narrow brick variant, used as fill in palette 6 levels (471 in level 4)
- `sand` — desert/sandy block, used sparingly as accent

**Full stone block family (add _N for palette):**
```
stone                    stone_inside         stone_inside_1
stone_top                stone_top_2          stone_bottom        stone_bottom_2
stone_left_side          stone_right_side     stone_left_side_2   stone_right_side_2
stone_top_left_corner    stone_top_right_corner
stone_bottom_left_corner stone_bottom_right_corner
stone_top_left_corner_2  stone_top_right_corner_2
stone_bottom_left_corner_2  stone_bottom_right_corner_2
stone_2  stone_3  stone_small
```

**Full grass block family (add _N for palette):**
```
grass_top                grass_top_2
grass_inside             grass_inside_1      grass_inside_2      grass_inside_5
grass_top_left_corner    grass_top_right_corner
grass_top_left_corner_2  grass_top_right_corner_2
grass_left_side          grass_right_side
grass_left_side_2        grass_right_side_2
grass_bottom             grass_bottom_2
grass_bottom_left_corner grass_bottom_right_corner
grass_bottom_left_corner_2 grass_bottom_right_corner_2
grass_small_2
```

**Island/floating platform edge pattern:**
```
[grass_top_left_corner] [grass_top] ... [grass_top_right_corner]    ← top
[grass_left_side]       [grass_inside]  [grass_right_side]          ← middle
[grass_bottom_left_corner][grass_bottom] [grass_bottom_right_corner] ← bottom
```
Bottom edge tiles are critical — without them islands look cut off.

---

## SECTION 4 — LEVEL ANATOMY (from real level study)

### Object counts by level type

| Level | Theme | Total | Blocks | Water | Enemies | Platforms | Treasures | Trees | Spawner |
|-------|-------|-------|--------|-------|---------|-----------|-----------|-------|---------|
| 1 | Mountain/mixed | 1575 | 1373 | 141 | 18 | 2 | 0 | 21 | 0 |
| 2 | Underground sea | 1502 | 1293 | 150 | 18 | 5 | 8 | 4 | 0 |
| 3 | Sandy ruins | 1354 | 1233 | 71 | 18 | 3 | 9 | 9 | 0 |
| 4 | Volcano/flood | 2776 | 1837 | 909 | 9 | 2 | 1 | 0 | 0 |
| 9 | Cave/forest | 918 | 822 | 39 | 14 | 1 | 2 | 12 | 1 |
| 10 | Ice cave | 1713 | 1204 | 476 | 23 | 1 | 0 | 0 | 0 |
| 12 | Dungeon | 699 | 649 | 0 | 14 | 0 | 8 | 8 | 1 |

**Key ratios:**
- High water (400+) → fewer enemies (9–23 but usually ~10)
- Low water / no water → more enemies and treasures
- Minimal levels (700–900 objects) are complete and valid
- Trees only appear when there's a nature/overworld theme

### Vertical layout guide
```
y = -2048 to -1024 : extreme heights — sky peaks, aerial ruins, storm zone
y = -1024 to  -512 : upper zone — cave ceilings, cliff faces, aerial platforms
y =  -512 to  -128 : primary traversal height — most player movement here
y =  -128 to   256 : ground level — main action zone
y =   256 to   512 : underground entrance / shallow cave
y =   512 to   896 : deep underground / cave network / sea floor
y =   896 to  1792 : deep void — lava, toxic floods, death zone
y =  1856 to  1920 : solid bottom floor (ALWAYS)
```

---

## SECTION 5 — STRUCTURAL ARCHETYPES (how to build landmarks)

These are the actual building techniques observed in real levels. Use these as construction vocabulary.

### 🏔️ MOUNTAIN (Level 1 technique)
Layer terrain rows that narrow as y decreases. Each row 1–2 blocks narrower than the one below.
Top row: `ice` or `stone_5` (snow cap). Lower body: `stone_inside` or `grass_inside`.
```
y=-768:  ████          (4 wide)
y=-704: ██████         (6 wide)
y=-640: ████████       (8 wide)
y=-576: ██████████     (10 wide)
y=-512: ████████████   (12 wide — base merges into main ground)
```
Place trees and decos on mid-mountain shelves. Enemies patrol the ridgeline.

### 🌋 VOLCANO (Level 4 technique)
Same pyramid-widening logic but use `brick_6` or `stone_6`.
Add lava water tiles in the crater (top 2 rows) and stream tiles down both flanks.
Rising lava pool at y=1500+ with `rise=True` for time pressure.
Surround base with lava pits (clusters of 3×2 lava tiles with gaps between).
```
y=-640:    ██           (crater, 2 wide — fill with lava tiles)
y=-576:   ████
y=-512:  ██████
y=-448: ████████
y=-384: ██████████      (each row +2 blocks)
...
y= 192: ████████████████████████  (base, merges into main terrain)
```

### 🏰 DUNGEON / CASTLE (Level 12 technique)
Use `brick_8` or `brick_6` as main structural block. Interior fill: `grass_inside_8` or `stone_inside`.
Build:
- **Outer walls**: 2-block-wide vertical columns from ground to battlements
- **Floors**: horizontal slabs every 5–6 blocks of height (create multiple interior levels)
- **Gate gap**: leave 3–4 block gap at ground level in front wall
- **Battlements**: alternating raised/lowered blocks at top of towers
- Place treasure clusters inside (3–4 chests on each interior floor)
- Enemies patrol interior floors

### 🕳️ CAVE SYSTEM (Level 9 technique)
Level 9 is the cave master — NO palette suffix (raw default colours = dark earthy cave feel).
Key technique: **dense block mass in y=-1024 to -512 band**, with organic gaps (not rectangular).
- Use `stone` for raw cave walls and ceilings
- Use `grass_inside` + `mud` for floor sections (cave floor feels organic)
- Gaps between sections: 128–576px wide (irregular, not uniform)
- Toxic water pools in hard-to-reach corners (`[70,220,70]`, `rise=True`)
- Trees placed inside the cave (surreal underground forest feel)
- Decos: `shroom1/2/3`, `shrub1/2/3` (underground vegetation)
- One spawn_point in the cave heart for infinite respawns

**Cave ceiling construction:**
Top rows have large gaps (wide open air pockets). Lower rows fill in progressively.
```
y=-1216: 11 blocks  (sparse — 2 isolated roof sections)
y=-1152: 11 blocks
y=-1088: 12 blocks  (a few more roof fragments)
y=-1024: 19 blocks  (denser, stalactite-like)
y= -960: 25 blocks  ← cave starts filling in
y= -896: 32 blocks
y= -832: 46 blocks  ← main cave body, almost continuous
y= -768: 50 blocks
```

### 🌊 SEA / FLOODED WORLD (Level 4 technique)
Use healing or normal water. Paint tiles across ALL y layers — the world is submerged.
900 tiles creates a fully flooded feel. Layer:
- y=-384 to +256: healing water `[0,200,100]` (shallow zone, survivable)
- y=256 to 1600: normal water `[50,50,255]` (deep, current)
- Bottom: lava `[255,80,0]` rising with `rise=True` (death zone creeping up)
Use back blocks as reef/rock walls. Minimal enemies — water IS the hazard.

### 🌲 FOREST (Level 9 upper section + Level 1 technique)
No palette needed (default palette = green/brown = natural).
- Wide flat or gently rolling ground at y=0 to y=256
- Dense tree placement: every 128–256px along ground surface
- Decos: `shrub1/2/3`, `grass1/2`, `pumpkin1/2` scattered between trees
- `mud` blocks mixed into terrain for earthy feel
- Occasional raised platforms (cliff edges: `grass_top_left_corner` with `grass_left_side` column)
- Enemies: Archers in trees (place at y = tree_y - 58), Warriors patrolling ground

### 🧊 ICE CAVE / FROZEN WORLD (Level 10 technique)
Primary block: `ice` (no suffix) — 400+ tiles covering walls, floors, ceiling.
Mix with `stone_inside` (no suffix) for dark contrast and `grass_inside_5` for snow-blue tint.
Use `brick_5` for structural elements (platforms, walls).
Water: `normal` water tiles `[50,50,255]` pooling in low areas (underground lakes).
476 water tiles = a full subterranean sea. Place at y=128 to y=512.
Two-colour enemies: Blue base force + Purple elite squad.
Single vertical moving platform to cross large ice shafts.

### 🏜️ DESERT RUINS (Level 3 technique)
Palette 3 (sandy warm) throughout.
`stone` (no suffix, 630 blocks!) + `grass_inside_3` (421) = the entire level.
Solid wall columns at x=-2048 from top to bottom — bounded, enclosed world.
`window` tiles at tops of tall walls (y=-1152, y=-1088) — architectural detail.
`box1` blocks placed mid-terrain as ruined crate obstacles.
`sand` blocks as sparse accent patches on surfaces.
Lava pools in deep pits. Enemies all Yellow.

### 🌴 JUNGLE (design pattern — not yet in a real level)
Use default palette (no suffix) for blocks.
`grass_top` → `grass_inside` → `grass_inside_1` layering for lush canopy platforms.
Overhanging platforms: top row `grass_top_right_corner` at ledge edges pointing inward.
Toxic water `[70,220,70]` in jungle floor trenches.
Many trees (20+), decos: `shrub1/2/3`, `shroom1/2/3`.
Vines = vertical 1-block-wide columns of `grass_left_side` or `grass_right_side` hanging from above.
Enemies: Archers hiding on canopy, Torch enemies in jungle floor shadows.

### ⛏️ DEEP MINE / ABYSS (design pattern)
Palette 7 (obsidian/void) or palette 2 (dark navy).
Tight vertical shafts: 3–4 blocks wide tunnels going deep (y=500 to y=1800).
Minecart platforms: horizontal movers at speed 150–200 crossing shafts.
Lava at the very bottom (y=1700+), toxic pools mid-shaft.
Back blocks: `stone_inside_7` or `stone_inside_2` on 128px grid = deep tunnel walls.
Treasure clustered at shaft bottoms (high risk/high reward).

---

## SECTION 6 — VALIDATED PYTHON HELPERS

```python
import json
BS = 64

ENTITY_SETTINGS = {
    "type": "entity settings",
    "Torch":   {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":50, "attack_power":4,"health":80},
    "Pawn":    {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":40, "attack_power":5,"health":70},
    "Warrior": {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":50, "attack_down":50, "attack_range":50, "attack_power":6,"health":90},
    "TNT":     {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":300,"attack_down":300,"attack_range":600,"attack_power":8,"health":100},
    "Archer":  {"acquire_range":1000,"acquire_down":500,"acquire_up":500,"attack_up":300,"attack_down":300,"attack_range":600,"attack_power":7,"health":100},
}

def snap(v): return round(v / 64) * 64

def blk(x, y, name, back=False):
    b = {"x":snap(x),"y":snap(y),"width":64,"height":64,"type":"block","name":name,"size":"big"}
    if back: b["perspective"] = "back"
    return b

def enemy(x, y, name, color):
    sizes = {"Pawn":(32,52),"Warrior":(40,58),"Archer":(42,58),"TNT":(40,58),"Torch":(40,58)}
    w, h = sizes[name]
    return {"x":int(x),"y":int(y),"width":w,"height":h,"type":"enemy","name":name,"color":color}

def water_tile(x, y, wtype, color, flow=1, rise=True):
    return {"x":snap(x),"y":snap(y),"width":64,"height":64,"type":"water",
            "water_type":wtype,"color":color,"flow":flow,"rise":rise}

def water_pool(x, y, w_tiles, h_tiles, wtype, color, flow=1, rise=True):
    return [water_tile(x+dx*64, y+dy*64, wtype, color, flow, rise)
            for dx in range(w_tiles) for dy in range(h_tiles)]

def mplatform(x, y, min_x, max_x, direction=-1, speed=100, color=[50,50,255]):
    return {"x":snap(x),"y":snap(y),"width":100,"height":20,"moving":True,
            "direction":[direction,0],"type":"moving_platform","speed":speed,
            "min_x":snap(min_x),"max_x":snap(max_x),"path":[[0,0]],"color":color}

def vplatform(x, y, dest_y_top, dest_y_bot, speed=100, color=[50,50,255]):
    return {"x":snap(x),"y":snap(y),"width":100,"height":20,"moving":True,
            "direction":[1,1],"type":"moving_platform","speed":speed,
            "dest_x":[snap(x),snap(x)+64],"dest_y":[dest_y_top,dest_y_bot],
            "min_x":snap(x),"max_x":snap(x)+64,"path":[[0,0]],"color":color}

def deco(x, y, name):
    return {"x":int(x),"y":int(y),"width":50,"height":50,"type":"deco","name":name,"size":"big"}

def tree(x, y):
    return {"x":int(x),"y":int(y),"width":50,"height":50,"type":"tree","name":"tree","size":"big"}

def treasure(x, y, name="red"):
    return {"x":snap(x),"y":snap(y),"width":64,"height":64,"type":"treasure","name":name}

def start(x=0, y=-64):
    return {"x":snap(x),"y":int(y),"points":[[0,64],[0,-64]],"width":64,"height":64,"type":"start"}

def spawn_point(x, y, entities, interval=5, limit=5):
    return {"x":snap(x),"y":snap(y),"width":64,"height":64,"interval":interval,
            "limit":limit,"type":"spawn_point","entities":entities}

def floor_row(y, name="stone", x_min=-2048, x_max=1920):
    return [blk(x, y, name) for x in range(snap(x_min), snap(x_max)+64, 64)]

def back_fill(x_min, x_max, y_min, y_max, name):
    return [blk(x, y, name, back=True)
            for x in range(snap(x_min), snap(x_max)+64, 128)
            for y in range(snap(y_min), snap(y_max)+64, 128)]

def island(x, y, w, pal="", depth=2):
    p = f"_{pal}" if pal else ""
    TL=f"grass_top_left_corner{p}"; TR=f"grass_top_right_corner{p}"
    BL=f"grass_bottom_left_corner{p}"; BR=f"grass_bottom_right_corner{p}"
    TOP=f"grass_top{p}"; BOT=f"grass_bottom{p}"
    L=f"grass_left_side{p}"; R=f"grass_right_side{p}"; FILL=f"grass_inside{p}"
    items = []
    for i in range(w):
        bx = snap(x+i*64)
        items.append(blk(bx, snap(y), TL if i==0 else(TR if i==w-1 else TOP)))
        for d in range(1, depth):
            items.append(blk(bx, snap(y+d*64), L if i==0 else(R if i==w-1 else FILL)))
        items.append(blk(bx, snap(y+depth*64), BL if i==0 else(BR if i==w-1 else BOT)))
    return items

def mountain(x_centre, y_base, half_width_blocks, peak_y, pal="", cap_name=None):
    """Builds a mountain. Widens by 1 block per side every 64px downward."""
    items = []
    fill = f"stone_inside_{pal}" if pal else "stone_inside"
    cap = cap_name or ("ice" if not pal else f"stone_{pal}")
    total_rows = abs(y_base - peak_y) // 64
    for row in range(total_rows + 1):
        y = peak_y + row * 64
        half = row  # 0 at peak, grows down
        x_left = x_centre - half * 64
        for bx in range(x_left, x_centre + half * 64 + 64, 64):
            name = cap if row == 0 else fill
            items.append(blk(snap(bx), snap(y), name))
    return items

def volcano(x_centre, y_base, base_half_w, peak_y, pal="6"):
    """Builds a volcano with lava crater."""
    items = []
    fill = f"brick_{pal}"
    total_rows = abs(y_base - peak_y) // 64
    for row in range(total_rows + 1):
        y = peak_y + row * 64
        half = total_rows - row  # wide at base, narrow at peak
        cur_half = max(1, half * base_half_w // total_rows)
        x_left = x_centre - cur_half * 64
        for bx in range(x_left, x_centre + cur_half * 64, 64):
            items.append(blk(snap(bx), snap(y), fill))
    # Lava crater
    crater_w = max(2, base_half_w // 4)
    items += water_pool(x_centre - crater_w*32, peak_y, crater_w, 1,
                        "lava", [255,80,0], flow=0, rise=False)
    # Lava streams down flanks
    for side in [-1, 1]:
        for r in range(1, min(6, total_rows)):
            sx = x_centre + side * (total_rows - r + 1) * base_half_w // total_rows * 64
            items += [water_tile(snap(sx), peak_y + r*64, "lava", [255,70,0], flow=0, rise=False)]
    return items

def dedup(items):
    """Remove duplicate foreground blocks. Always call before saving."""
    seen = set(); out = []
    for o in items:
        if o.get("type")=="block" and o.get("perspective")!="back":
            k = (o["x"],o["y"])
            if k in seen: continue
            seen.add(k)
        out.append(o)
    return out

def save_level(items, filename):
    items = dedup(items)
    with open(filename, "w") as f:
        json.dump(items, f, indent=2)
    counts = {}
    for o in items: counts[o.get("type","?")] = counts.get(o.get("type","?"),0)+1
    print(f"Saved {filename} — {len(items)} objects: {counts}")
```

---

## SECTION 7 — LEVEL THEMES & CREATIVE BRIEF

When generating a new level, pick a theme and follow its design language fully.

### 🏔️ Mountain Peak
- Palette: 5 (snow cap) + none (rock body)
- Structure: wide base tapering to narrow peak using `mountain()` helper
- Ice cap with `ice` blocks on top 3–4 rows, `stone_inside` body
- Terraces cut into mountainside as stepping platforms
- Waterfalls: vertical 1-wide columns of `normal` water down the flanks
- Trees on lower slopes, decos: `shrub1/2/3`, `bone`
- Enemies: Archers on ledges, Warriors on terraces

### 🌋 Volcanic Eruption
- Palette: 6 (scorched) throughout
- One central volcano using `volcano()` helper, lava crater, lava streams
- Lava pits at ground level (3×2 tile clusters) between platforms
- Rising lava at y=1500+ with `rise=True` — time pressure mechanic
- Back blocks as scorched cave walls (stone_inside_6 on 128px grid)
- Few enemies (9–12) — lava IS the danger
- Decos: `bone`, `pumpkin1`, `mud`

### 🕳️ Deep Cave System
- Palette: none (default) — raw earthy cave
- Dense block mass y=-1024 to -512, irregular gaps (not rectangular)
- `stone` walls, `grass_inside` + `mud` for floor texture
- Toxic pools in pockets (`[70,220,70]`, `rise=True`)
- Trees inside cave (surreal), shroom/shrub decos
- 1 spawn_point in the cave centre
- Vertical platforms to reach hidden upper chambers

### 🏰 Ancient Dungeon
- Palette: 8 (autumn) or 2 (dark navy) — dungeon brick
- `brick_8` or `brick_6` as main block (not just accent — it IS the terrain)
- Multiple interior floors with `grass_inside_8` fill
- Treasure clusters on each floor (3–4 chests each spot)
- Gate gap in front wall + battlements on towers
- Enemies: Warriors patrolling floors, Archers in towers
- Decos: `bone`, `scare_crow`, `arrow`, `exit`

### 🌊 Submerged Sea World
- Palette: 2 (deep navy) or none
- 500+ water tiles covering most of the world height
- Healing water in upper zone, normal in middle, lava/toxic at bottom
- Terrain as underwater rock shelves and coral formations
- Back blocks as seafloor texture
- Minimal enemies — water hazard is primary
- Moving platforms as wooden rafts crossing water surface

### 🌲 Ancient Forest
- Palette: none (default green) or 8 (autumn)
- Wide rolling ground terrain with elevation changes
- Dense tree placement (15–20+ trees along ground)
- `mud` mixed into ground blocks for earthy feel
- Cliff edges: `grass_top_right_corner` / `grass_left_side` column technique
- Decos: `shrub1/2/3`, `grass1/2`, `pumpkin1/2`, `exit`
- Archers hidden in tree canopy, Warriors patrolling ground

### 🌴 Dense Jungle
- Palette: none (default) — maximum green
- Overhanging canopy platforms (top surface with inward-pointing corners)
- Toxic trenches at floor level (`[70,220,70]`)
- Vines: vertical 1-wide `grass_left_side`/`grass_right_side` columns hanging from platforms
- 20+ trees, max deco density
- Spawn_point for infinite Pawn respawns in jungle undergrowth
- Enemies Archers high, Torches low

### 🏜️ Desert Ruins
- Palette: 3 (sandy warm)
- Solid boundary walls at x=-2048 using `stone` column (full y range)
- `stone` bulk + `grass_inside_3` fill
- `window` tiles at tall wall tops
- `sand` + `box1` accent blocks scattered on surfaces
- `brick_3` patches inside `stone` walls for contrast
- Lava in deep pits. Enemies all Yellow.

### 🧊 Frozen Abyss
- Palette: 5 (snow) + plain `ice` blocks as primary
- `ice` dominates (400+ tiles) — walls, floors, ceiling, everything
- Mix `stone_inside` (plain) for dark rock contrast
- Underground sea: 400+ normal water tiles at y=128–512
- Two-colour enemies: Blue base + Purple elite
- Single vertical platform crossing main ice shaft

### ⚡ Sky Citadel
- Palette: 5 (snow) or 2 (dark)
- Main ground high up (y=-200 to 0) — world floats in sky
- Solid void below (lava at y=500+)
- Full castle structure: towers, curtain wall, gate, multiple floors
- Aerial island chains leading to the castle
- Moving platforms as sky bridges
- Healing pools inside towers

---

## SECTION 8 — CHECKLIST (run before every save)

- [ ] `entity settings` at index 0
- [ ] `start` at index 1 with `"points":[[0,64],[0,-64]]`
- [ ] Two full-width solid rows at bottom (y=1856 + y=1920)
- [ ] All block x/y multiples of 64
- [ ] `dedup()` called before saving
- [ ] No enemies inside foreground blocks
- [ ] Water tiles are 64×64 (never large rectangles)
- [ ] Moving platforms use `min_x`/`max_x`; vertical ones use `dest_y`
- [ ] At least 7 decos including 1–2 `exit` decos
- [ ] Enemies placed with correct size (Pawn 32×52, Warrior 40×58, Archer 42×58, TNT 40×58, Torch 40×58)
- [ ] Island platforms have bottom edge tiles
- [ ] Theme is consistent (one dominant palette, one accent max)
