# PIXEL ABYSS — Complete Level Generation Prompt
### For use with any AI / code generator, no source files needed

---

## 1. WHAT YOU ARE MAKING

You are generating **JSON level files** for **PIXEL ABYSS**, a 4-player Pygame platformer by BLEMAC.

Each level is a **single JSON array** saved as `levels/{N}.json`.  
The engine loads the array, iterates every object, and places it into a 64×64px world grid that spans **x: -2000 to +2000, y: -2000 to +2000** (grid origin is `0,0`; **positive Y is down**).

The output must be **pure JSON** — no code, no comments, just the array.

---

## 2. THE COORDINATE SYSTEM

```
          negative Y (up)
               |
  negative X --+-- positive X (right)
               |
          positive Y (down)
```

- **All block x/y values must be exact multiples of 64.**
- Non-block objects (enemies, decos, treesa) can use non-multiples.
- World grid was created with `block_size = 64`, `width = height = 2000`.
- Safe usable range: **x: -2048 to +1984, y: -2000 to +1984**.

---

## 3. REQUIRED ARRAY STRUCTURE

Every level array **must** start with these two objects in this order, then all world objects follow:

### 3.1 Entity Settings (always index 0)
```json
{
  "type": "entity settings",
  "Torch":   { "acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 50,  "attack_power": 4, "health": 80  },
  "Pawn":    { "acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 40,  "attack_power": 5, "health": 70  },
  "Warrior": { "acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 50,  "attack_power": 6, "health": 90  },
  "TNT":     { "acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 300, "attack_down": 300, "attack_range": 600, "attack_power": 8, "health": 100 },
  "Archer":  { "acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 300, "attack_down": 300, "attack_range": 600, "attack_power": 7, "health": 100 }
}
```

### 3.2 Start Point (always index 1)
This is where players spawn. Use a location above solid ground.
```json
{ "x": 0, "y": -128, "width": 64, "height": 64, "type": "start" }
```

---

## 4. ALL OBJECT TYPES — FULL SCHEMAS

### 4.1 BLOCK (solid terrain)
```json
{
  "x": 0,
  "y": 512,
  "width": 64,
  "height": 64,
  "type": "block",
  "name": "stone",
  "size": "big"
}

{
  "x": 0,
  "y": 64,
  "width": 64,
  "height": 64,
  "type": "block",
  "name": "box1",
  "size": "big"
}


```
- `x`, `y` — **must be multiples of 64**
- `width`, `height` — always `64` for `"big"`, `32` for `"small"`
- `size` — `"big"` or `"small"`
- `name` — see Section 5 (block names & palette system)
- `perspective` — **omit for foreground** (solid, collidable). Add `"perspective": "back"` for background decoration (semi-transparent, not collidable)

**Background block:**
```json
{
  "x": 64, "y": -576, "width": 64, "height": 64,
  "type": "block", "name": "stone_left_side", "size": "big",
  "perspective": "back"
}
```
```json
{
  "x": 0,
  "y": 128,
  "width": 64,
  "height": 64,
  "type": "block",
  "name": "box4",
  "size": "big",
  "perspective": "back"
}
```

### 4.2 ENEMY
```json
{
  "x": -1408, "y": -704,
  "width": 42, "height": 64,
  "type": "enemy",
  "name": "Archer",
  "color": "Yellow"
}
```
- `name` — `"Pawn"` | `"Warrior"` | `"Archer"` | `"TNT"` | `"Torch"`
- `color` — `"Red"` | `"Blue"` | `"Yellow"` | `"Purple"` |
- Typical sizes: Pawn `32×52`, Warrior `40×58`, Archer `42×64`, TNT `40×58`, Torch `42×64`
- Place enemies **above solid ground**, not inside blocks

### 4.3 SPAWN POINT (continuous enemy spawner)
```json
{
  "x": 960, "y": -64,
  "width": 64, "height": 64,
  "interval": 4,
  "limit": 12,
  "type": "spawn_point",
  "entities": [
    ["Archer", "Red"],
    ["TNT", "Red"]
  ]
}
```
- `interval` — seconds between spawns
- `limit` — max enemies alive from this spawner at once
- `entities` — list of `[name, color]` pairs, one is chosen randomly each spawn

### 4.4 TREE
```json
{
  "x": -640, "y": 256,
  "width": 50, "height": 50,
  "type": "tree",
  "name": "tree",
  "size": "big"
}
```
- Place on top of terrain (y = terrain_top_y - 50 or so)
- Trees are damageable / destructible

### 4.5 DECO (decorative props, damageable)
```json
{
  "x": -64, "y": 448,
  "width": 50, "height": 50,
  "type": "deco",
  "name": "arrow",
  "size": "big"
}
```
Available deco `name` values:
`"arrow"`, `"bone"`, `"box1"`, `"box4"`, `"exit"`, `"grass1"`, `"grass2"`,
`"pumpkin1"`, `"pumpkin2"`, `"scare_crow"`, `"shroom1"`, `"shroom2"`, `"shroom3"`,
`"shrub1"`, `"shrub2"`, `"shrub3"`, `"window"`, `"sand"`, `"mud"`

### 4.6 TREASURE
```json
{
  "x": -640, "y": -576,
  "width": 64, "height": 64,
  "type": "treasure",
  "name": "red"
}
```
- `name` — `"red"` | `"pink"` | `"green"` | `"yellow"` (chest color)
- Place on solid surfaces, not inside blocks

### 4.7 WATER ZONE
```json
{
  "x": -1216, "y": 1728,
  "width": 64, "height": 64,
  "type": "water",
  "water_type": "lava",
  "color": [255, 80, 0],
  "flow": 1,
  "rise": true
}
```
- `water_type` — `"normal"` | `"current"` | `"healing"` | `"toxic"` | `"lava"`
- `color` — RGB array `[R, G, B]`
- `flow` — current strength (int, 0 = still)
- `rise` — `true` if water level rises over time, `false` if static
- Water zones **can overlap with other water zones** (only water is exempt from the water blacklist)
- Water zones **cannot** overlap with `block_fore`
- Width/height can be any size (not restricted to 64×64) — use large rectangles for lakes/oceans

**Suggested colors by type:**
| Type | Color |
|------|-------|
| normal water | `[30, 100, 200]` |
| healing pool | `[60, 180, 120]` |
| current stream | `[80, 130, 200]` |
| toxic | `[60, 180, 30]` or `[40, 16, 80]` |
| lava | `[255, 80, 0]` |

### 4.8 MOVING PLATFORM
```json
{
  "x": 1600, "y": 64,
  "width": 100, "height": 20,
  "moving": true,
  "direction": [-1, 1],
  "type": "moving_platform",
  "speed": 100,
  "dest_x": [768, 1664],
  "dest_y": [64, 128],
  "min_x": 768,
  "max_x": 1664,
  "path": [[0, 0]],
  "color": [50, 50, 255]
}
```
- `dest_x` — `[min_x, max_x]` bounds of horizontal travel
- `dest_y` — `[start_y, end_y]` bounds of vertical travel
- `min_x` / `max_x` — same as `dest_x` values
- `color` — RGB array for platform color
- `speed` — pixels per second
- `direction` — `[-1, 1]` (starts moving left then right), `[1, -1]` (right then left)

---

## 5. BLOCK NAMES & THE PALETTE SYSTEM

### 5.1 Base block sprite names (no palette suffix)
These are the raw tile names. They follow a **naming convention** that describes the block's visual role:

**Stone family:**
```
stone                   ← solid interior fill
stone_inside            ← interior variant/plain interior
stone_inside_1          ← interior variant 1
stone_top               ← top-facing surface
stone_top_2             ← alternate top
stone_bottom            ← bottom edge
stone_bottom_2          ← alternate bottom/different pallete
stone_left_side         ← left vertical edge
stone_right_side        ← right vertical edge
stone_top_left_corner   ← top-left corner piece
stone_top_right_corner  ← top-right corner piece
stone_bottom_left_corner ← bottom-left corner piece
stone_bottom_right_corner ← bottom-right corner piece
stone_bottom_left_corner_2
stone_bottom_right_corner_2
stone_top_left_corner_2
stone_top_right_corner_2
stone_left_side_2
stone_right_side_2
stone_2                 ← alternate solid
stone_3                 ← alternate solid
stone_small             ← small variant (use size "small")
```

**Grass family:**
```
grass_top               ← grassy top surface
grass_top_2             ← alternate grass top
grass_inside            ← grass-tinted interior fill
grass_inside_1
grass_inside_2
grass_inside_5
grass_small_2
grass_left_side_2
grass_right_side_2
grass_right_side
grass_top_left_corner
grass_top_right_corner
grass_top_left_corner_2
grass_top_right_corner_2
grass_bottom_2
grass_bottom_left_corner_2
grass_bottom_right_corner_2
```

**Brick / special:**
```
brick                   ← base brick (red default)
window                  ← window decoration block
box1                    ← crate
box4                    ← crate variant
sand                    ← sandy block
mud                     ← muddy block
ice                         < iccy block
```

### 5.2 Palette suffix system
The palette system recolors entire block families using pixel-swap. To use a non-default theme, **append `_N`** (where N = 2–8) to the block base name:

```
stone        → stone_2, stone_3, stone_4, stone_5, stone_6, stone_7, stone_8
stone_inside → stone_inside_2, stone_inside_3, ... stone_inside_8
grass_top    → grass_top_2, grass_top_3, ... grass_top_8
brick        → brick_2, brick_3, ... brick_8
```

**The suffix applies to the WHOLE name before the first `_` group:**
- `stone` → add `_N` → `stone_N` ✓
- `stone_inside` → add `_N` → `stone_inside_N` ✓
- `grass_top_left_corner` → add `_N` → `grass_top_left_corner_N` ✓
- `brick` → add `_N` → `brick_N` ✓

### 5.3 Palette themes (N = palette number)
| N | Theme | Description |
|---|-------|-------------|
| 1 | Default | Original colors (no suffix needed) |
| 2 | Dark purple-navy | Deep purple dungeon |
| 3 | Sandy warm | Desert / sandy ruins |
| 4 | Mossy | Overgrown jungle green |
| 5 | Snow / ice | Frozen arctic blue-white |
| 6 | Nether / scorched | Hellfire red-black |
| 7 | Obsidian / void | Deep purple-black void |
| 8 | Autumn | Orange-brown harvest |

**Rule:** All blocks in a level should use the **same palette number** for visual consistency. Mix stone_N, grass_top_N, brick_N from the same N.

**Examples by theme:**
- Snow level → `"stone_5"`, `"grass_top_5"`, `"grass_inside_5"`, `"stone_inside_5"`, `"brick_5"`
- Nether level → `"stone_6"`, `"brick_6"`, `"stone_inside_6"`
- Mossy ruins → `"stone_4"`, `"grass_top_4"`, `"grass_inside_4"`
- Autumn forest → `"stone_8"`, `"grass_top_8"`, `"grass_inside_8"`

---

## 6. COEXISTENCE / BLACKLIST RULES

The engine uses a per-grid-cell tag set to prevent illegal overlaps. Here are the rules:

| Object type | Cannot share cell with |
|-------------|----------------------|
| `block` (fore) | `block_fore`, `block_back`, `entities`, `deco`, `platforms` |
| `block` (back) | `block_fore`, `block_back` (two back-blocks can't share a cell either) |
| `enemy` | `block_fore`, `entities`, `platforms` |
| `spawn_point` | `block_fore`, `entities`, `platforms` |
| `deco` | `block_fore`, `deco`, `platforms`, `treasure` |
| `tree` | `block_fore`, `deco`, `platforms`, `treasure` |
| `treasure` | `block_fore`, `deco`, `platforms`, `block_back`, `treasure` |
| `water` | only `water` (water can coexist with most, only blocked by another water at same cell) |
| `moving_platform` | `platforms` |

**Critical implication:** Foreground blocks own their grid cell completely — nothing else (enemies, decos, trees) can occupy the same 64×64 cell. Place enemies/decos **above** terrain, not inside it.

**Background blocks** (`"perspective": "back"`) are semi-transparent, non-collidable, and good for cave wall depth. They cannot share a cell with any other block.

---

## 7. HOW TO BUILD A GOOD LEVEL

### 7.1 Layer order for terrain sections
A proper terrain slice (left to right) uses these block roles:
Make sure you use most of this
```
[top_left_corner] [top] [top] [top] [top_right_corner]
[left_side]     [inside] [inside] [inside] [right_side]
[left_side]     [inside] [inside] [inside] [right_side]
[bottom_left]   [bottom] [bottom] [bottom] [bottom_right]
```

For a flat ground slab (simplest approach), just use:
- `grass_top_N` for the surface row
- `stone_N` (or `stone_inside_N`) for rows below

### 7.2 Scale & spacing
- Level width is typically **-2048 to +1984** (128 blocks wide)
- Level height range typically **-768 to +640** for the playable area
- Platforms should be at least **3 blocks wide** (192px) to be jumpable
- Leave **gaps of 128–320px** between platforms for jumping challenges
- Underground caves: carve into the ground 3–5 blocks deep

### 7.3 What makes a level "big"
A big level should have:
- **800+ total objects** (400+ blocks minimum)
- Terrain spanning near the full x range (-2048 to +1984)
- At least **3 vertical layers** (ground + platforms + upper area)
- **Multiple landmark structures** (towers, caves, bridges, arenas)
- **10+ enemy placements** or spawn points
- **3+ moving platforms**
- **1–300 water zones** depends on what youre building maybe its a sea or river,, whatever
- **15+ treasures**
- **Decorations** scattered throughout

### 7.4 Vertical layout suggestions
```
y = -768 to -512 : upper sky / tower tops / aerial platforms
y = -512 to -192 : mid-air platforms / castle walls / cliff faces  
y = -192 to   64 : main traversal height (players spend most time here)
y =  64  to  384 : ground level area
y =  384 to  512 : ground surface (grass_top row here)
y =  512 to  640 : underground entrance / shallow cave
y =  640 to  896 : deep underground / cave network
y =  896+        : deep void / lava pit/ deep sea, crazy current
```

---

## 8. PYTHON GENERATION PATTERN (recommended approach)

Generate levels using Python helper functions and output JSON. This avoids manually typing thousands of objects:

```python
import json

BS = 64  # block size

# ---- helper functions ----

def block(x, y, name, size="big", perspective="fore"):
    b = {"x": x, "y": y, "width": 64, "height": 64,
         "type": "block", "name": name, "size": size}
    if perspective == "back":
        b["perspective"] = "back"
    return b

def enemy(x, y, name, color):
    return {"x": x, "y": y, "width": 42, "height": 64,
            "type": "enemy", "name": name, "color": color}

def spawn(x, y, entities, interval=4, limit=10):
    return {"x": x, "y": y, "width": 64, "height": 64,
            "interval": interval, "limit": limit,
            "type": "spawn_point", "entities": entities}

def water(x, y, w, h, wtype, color, flow=1, rise=False):
    return {"x": x, "y": y, "width": w, "height": h,
            "type": "water", "water_type": wtype,
            "color": color, "flow": flow, "rise": rise}

def platform(x, y, dest_x, dest_y, speed=80, color=[80, 80, 255]):
    return {"x": x, "y": y, "width": 100, "height": 20,
            "moving": True, "direction": [-1, 1],
            "type": "moving_platform", "speed": speed,
            "dest_x": dest_x, "dest_y": dest_y,
            "min_x": dest_x[0], "max_x": dest_x[1],
            "path": [[0, 0]], "color": color}

def deco(x, y, name):
    return {"x": x, "y": y, "width": 50, "height": 50,
            "type": "deco", "name": name, "size": "big"}

def tree(x, y):
    return {"x": x, "y": y, "width": 50, "height": 50,
            "type": "tree", "name": "tree", "size": "big"}

def treasure(x, y, name="red"):
    return {"x": x, "y": y, "width": 64, "height": 64,
            "type": "treasure", "name": name}

def start(x, y):
    return {"x": x, "y": y, "width": 64, "height": 64, "type": "start"}

ENTITY_SETTINGS = {
    "type": "entity settings",
    "Torch":   {"acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 50,  "attack_power": 4, "health": 80},
    "Pawn":    {"acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 40,  "attack_power": 5, "health": 70},
    "Warrior": {"acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 50,  "attack_down": 50,  "attack_range": 50,  "attack_power": 6, "health": 90},
    "TNT":     {"acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 300, "attack_down": 300, "attack_range": 600, "attack_power": 8, "health": 100},
    "Archer":  {"acquire_range": 1000, "acquire_down": 500, "acquire_up": 500, "attack_up": 300, "attack_down": 300, "attack_range": 600, "attack_power": 7, "health": 100}
}

# ---- level generator ----

def gen_level():
    items = [ENTITY_SETTINGS, start(0, -128)]
    ground_y = 512
    PAL = "stone_5"   # ← change palette suffix here
    GRASS = "grass_top_5"

    # Wide ground
    for x in range(-2048, 1984, 64):
        items.append(block(x, ground_y, PAL))
        items.append(block(x, ground_y - 64, GRASS))

    # ... add structures, platforms, enemies etc.

    return items

data = gen_level()
with open("levels/10.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"Generated {len(data)} items")
```

---

## 9. VALIDATION CHECKLIST

Before saving any level JSON, verify:

- [ ] First object is `"type": "entity settings"` with all 5 enemy types
- [ ] Second object is `"type": "start"` with valid x/y above ground
- [ ] All `"type": "block"` objects have x/y as **multiples of 64**
- [ ] No foreground block (`perspective` omitted or `"fore"`) occupies the same x/y as another foreground block
- [ ] No background block shares x/y with any other block
- [ ] Enemies/decos/trees are placed **above** terrain, not inside blocks
- [ ] Water zones do not overlap with foreground blocks
- [ ] Every moving platform has both `dest_x` and `dest_y` defined and `min_x`/`max_x` matching `dest_x`
- [ ] At least one `"type": "spawn_point"` or multiple `"type": "enemy"` entries exist
- [ ] The level has a `"type": "start"` entry

---

## 10. COMPLETE MINIMAL LEVEL EXAMPLE

This is a minimal but valid level (snow palette, small castle):

```json
[
  {
    "type": "entity settings",
    "Torch": {
      "acquire_range": 1000,
      "acquire_down": 500,
      "acquire_up": 500,
      "attack_up": 50,
      "attack_down": 50,
      "attack_range": 50,
      "attack_power": 4,
      "health": 80
    },
    "Pawn": {
      "acquire_range": 1000,
      "acquire_down": 500,
      "acquire_up": 500,
      "attack_up": 50,
      "attack_down": 50,
      "attack_range": 40,
      "attack_power": 5,
      "health": 70
    },
    "Warrior": {
      "acquire_range": 1000,
      "acquire_down": 500,
      "acquire_up": 500,
      "attack_up": 50,
      "attack_down": 50,
      "attack_range": 50,
      "attack_power": 6,
      "health": 90
    },
    "TNT": {
      "acquire_range": 1000,
      "acquire_down": 500,
      "acquire_up": 500,
      "attack_up": 300,
      "attack_down": 300,
      "attack_range": 600,
      "attack_power": 8,
      "health": 100
    },
    "Archer": {
      "acquire_range": 1000,
      "acquire_down": 500,
      "acquire_up": 500,
      "attack_up": 300,
      "attack_down": 300,
      "attack_range": 600,
      "attack_power": 7,
      "health": 100
    }
  },
  {
    "x": 128,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 0,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 64,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -640,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -64,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -128,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -192,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -640,
    "y": 256,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": -64,
    "y": 256,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": -448,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -512,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -576,
    "y": 192,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": -384,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -320,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -448,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -320,
    "y": 256,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": 64,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_3",
    "size": "big"
  },
  {
    "x": 128,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 128,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -448,
    "y": -192,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": -64,
    "y": 448,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "arrow",
    "size": "big"
  },
  {
    "x": -384,
    "y": 192,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "shroom1",
    "size": "big"
  },
  {
    "x": -256,
    "y": 256,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "shroom3",
    "size": "big"
  },
  {
    "x": -320,
    "y": -192,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "exit",
    "size": "big"
  },
  {
    "x": -832,
    "y": 256,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "scare_crow",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 384,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "pumpkin1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 192,
    "width": 50,
    "height": 50,
    "type": "tree",
    "name": "tree",
    "size": "big"
  },
  {
    "x": 320,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -320,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "mud",
    "size": "big"
  },
  {
    "x": -256,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "mud",
    "size": "big"
  },
  {
    "x": -1152,
    "y": -640,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "exit",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -448,
    "width": 50,
    "height": 50,
    "type": "deco",
    "name": "bone",
    "size": "big"
  },
  {
    "x": -576,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 0,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 64,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -512,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": -1408,
    "y": -704,
    "width": 42,
    "height": 64,
    "type": "enemy",
    "name": "Archer",
    "color": "Yellow"
  },
  {
    "x": 320,
    "y": -64,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Blue"
  },
  {
    "x": -320,
    "y": 192,
    "width": 32,
    "height": 52,
    "type": "enemy",
    "name": "Pawn",
    "color": "Yellow"
  },
  {
    "x": 1856,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_2",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1728,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1664,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1600,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1600,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1664,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1728,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1728,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1664,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1600,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": -1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1920,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1856,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1920,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -2048,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -2048,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1984,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1088,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1152,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1088,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_2",
    "size": "big"
  },
  {
    "x": -1600,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1664,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1216,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1280,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1280,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1216,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1344,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1152,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1088,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1024,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1024,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1088,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1152,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1152,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1088,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1024,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -960,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -896,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -832,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -768,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -704,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -640,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -576,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -512,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -576,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -640,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -768,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -832,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -896,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -896,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -960,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -960,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -832,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -768,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -704,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -640,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -576,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -704,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -640,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -576,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -512,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -512,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -448,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -384,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -320,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -384,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -192,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -64,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 0,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 64,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 128,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -128,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -256,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -320,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -448,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -448,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -512,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -384,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -320,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -256,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -192,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -128,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -64,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 0,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 64,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 128,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 192,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 256,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 320,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 384,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 448,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 512,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 512,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 576,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 640,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 704,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 768,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 832,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 896,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 448,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 448,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 384,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 320,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 256,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 192,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 128,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 64,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 0,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -64,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -192,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -128,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -256,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 64,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 192,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 256,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 320,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 384,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 128,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 192,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 512,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 384,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 320,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 256,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 512,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 448,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 576,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 576,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 640,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 704,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 768,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 832,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 896,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 960,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 960,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 640,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 576,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 640,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 704,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 768,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 832,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 768,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 704,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 832,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1408,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1344,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1280,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1344,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1408,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1472,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1600,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1536,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1536,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1472,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1408,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1280,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1344,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1472,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1664,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 64,
    "width": 100,
    "height": 20,
    "moving": true,
    "direction": [
      -1,
      1
    ],
    "type": "moving_platform",
    "speed": 100,
    "dest_x": [
      768,
      1664
    ],
    "dest_y": [
      64,
      128
    ],
    "min_x": 768,
    "max_x": 1664,
    "path": [
      [
        0,
        0
      ]
    ],
    "color": [
      50,
      50,
      255
    ]
  },
  {
    "x": 256,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": -384,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -320,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -256,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -192,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -128,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -64,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 0,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 64,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -320,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -256,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -192,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -128,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -64,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 0,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 64,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 128,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 192,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 192,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 256,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 128,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 128,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 192,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 256,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 320,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 384,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 448,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 512,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 576,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 640,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 768,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big"
  },
  {
    "x": 768,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big"
  },
  {
    "x": -384,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": -384,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": -384,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": -320,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 448,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 512,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 576,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 640,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 768,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": -384,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 768,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 832,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 832,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 832,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 832,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -640,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 448,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 384,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 576,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 704,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 768,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -704,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -768,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 256,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 192,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 320,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 384,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 448,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 512,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": 192,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 256,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 320,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 128,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": -512,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": -576,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": -768,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 192,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 384,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner",
    "size": "big"
  },
  {
    "x": -192,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -128,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -64,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": 0,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -256,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -640,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -384,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner",
    "size": "big"
  },
  {
    "x": -704,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 320,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 256,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 448,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 512,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 576,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 640,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 768,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": 832,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top",
    "size": "big"
  },
  {
    "x": -192,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side",
    "size": "big"
  },
  {
    "x": 1600,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1536,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1472,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1344,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1280,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 320,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 640,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 576,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1216,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1152,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 640,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 832,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 896,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 64,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -448,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -512,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": 448,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": 384,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": 960,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": 1408,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -704,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -512,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -512,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -512,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -576,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -576,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -576,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -512,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -448,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -384,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -320,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -256,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -192,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -128,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -64,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -64,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": -128,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -576,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -512,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -448,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -384,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -320,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -256,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -192,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -64,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 0,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -512,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -320,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -640,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": -704,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": -768,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": -832,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -832,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -768,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -704,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -768,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -640,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -640,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -704,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -576,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 896,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1728,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 512,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 576,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 640,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 640,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 704,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 768,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 832,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 896,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": -1408,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 320,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -256,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -320,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -384,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -448,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 704,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 896,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1088,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 896,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 960,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1024,
    "y": 1792,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1088,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1152,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1216,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": 1280,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "water",
    "water_type": "lava",
    "color": [
      255,
      80,
      0
    ],
    "flow": 1,
    "rise": true
  },
  {
    "x": -1344,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -960,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -896,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -832,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -768,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -704,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -640,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -512,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -576,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -192,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -128,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": -64,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 0,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 64,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 128,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 192,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 256,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 512,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 576,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 640,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 448,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 384,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 768,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 832,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1600,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1536,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1472,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1408,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1344,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1280,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1216,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1152,
    "y": 1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 896,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 512,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 576,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 1792,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 1344,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 1280,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "tree",
    "name": "tree"
  },
  {
    "x": 896,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass1"
  },
  {
    "x": 960,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass1"
  },
  {
    "x": 1024,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass1"
  },
  {
    "x": 1088,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass1"
  },
  {
    "x": 1152,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass1"
  },
  {
    "x": 1024,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass2"
  },
  {
    "x": 1600,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "grass2"
  },
  {
    "x": 192,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "shrub3"
  },
  {
    "x": 320,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "shroom3"
  },
  {
    "x": -512,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "bone"
  },
  {
    "x": -576,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "deco",
    "name": "bone"
  },
  {
    "x": -1920,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1728,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1792,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -896,
    "y": 832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -896,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -960,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -960,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -896,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -832,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -768,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -832,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -896,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -960,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -768,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -832,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -896,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -768,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -704,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1920,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1856,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_1",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box4",
    "size": "big"
  },
  {
    "x": -1792,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box4",
    "size": "big"
  },
  {
    "x": -1728,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box4",
    "size": "big"
  },
  {
    "x": 0,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -640,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -576,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -576,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -512,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -448,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -384,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -1216,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "box1",
    "size": "big"
  },
  {
    "x": 960,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 640,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 960,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_left_corner",
    "size": "big"
  },
  {
    "x": 704,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 768,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 896,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 832,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 576,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 64,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 128,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": 256,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -320,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -704,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -640,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -576,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom",
    "size": "big"
  },
  {
    "x": -448,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 704,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 768,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 832,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 896,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top",
    "size": "big"
  },
  {
    "x": 576,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -704,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -640,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": -576,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner",
    "size": "big"
  },
  {
    "x": 640,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 960,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1024,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_right_corner",
    "size": "big"
  },
  {
    "x": 1088,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 512,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -768,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 320,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner",
    "size": "big"
  },
  {
    "x": 1664,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 1664,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 320,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 320,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 384,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -832,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1600,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 1856,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1856,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1856,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1664,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1728,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1792,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1856,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1920,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1920,
    "y": -1984,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big"
  },
  {
    "x": 1792,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 1664,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": 1856,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone",
    "size": "big"
  },
  {
    "x": -256,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside",
    "size": "big"
  },
  {
    "x": 832,
    "y": 1088,
    "width": 100,
    "height": 20,
    "moving": true,
    "direction": [
      1,
      1
    ],
    "type": "moving_platform",
    "speed": 100,
    "dest_x": [
      832,
      896
    ],
    "dest_y": [
      1088,
      1664
    ],
    "min_x": 832,
    "max_x": 896,
    "path": [
      [
        0,
        0
      ]
    ],
    "color": [
      50,
      50,
      255
    ]
  },
  {
    "x": 960,
    "y": -1088,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Yellow"
  },
  {
    "x": 640,
    "y": -1152,
    "width": 32,
    "height": 52,
    "type": "enemy",
    "name": "Pawn",
    "color": "Yellow"
  },
  {
    "x": 1216,
    "y": -832,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Warrior",
    "color": "Yellow"
  },
  {
    "x": 1408,
    "y": -704,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Torch",
    "color": "Yellow"
  },
  {
    "x": 1024,
    "y": -640,
    "width": 42,
    "height": 58,
    "type": "enemy",
    "name": "Archer",
    "color": "Yellow"
  },
  {
    "x": -1600,
    "y": -256,
    "width": 32,
    "height": 52,
    "type": "enemy",
    "name": "Pawn",
    "color": "Yellow"
  },
  {
    "x": -1408,
    "y": -256,
    "width": 32,
    "height": 52,
    "type": "enemy",
    "name": "Pawn",
    "color": "Yellow"
  },
  {
    "x": -1216,
    "y": 448,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Warrior",
    "color": "Yellow"
  },
  {
    "x": -1408,
    "y": 384,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Warrior",
    "color": "Yellow"
  },
  {
    "x": -384,
    "y": 896,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Torch",
    "color": "Yellow"
  },
  {
    "x": -320,
    "y": 896,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "Torch",
    "color": "Yellow"
  },
  {
    "x": 192,
    "y": 0,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Blue"
  },
  {
    "x": 256,
    "y": 0,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Blue"
  },
  {
    "x": 0,
    "y": -256,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Blue"
  },
  {
    "x": -1600,
    "y": 1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -832,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -576,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -704,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_left_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -640,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -640,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -576,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_left_side_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_left_side_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_left_side_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_left_side_2",
    "size": "big"
  },
  {
    "x": -704,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_left_side_2",
    "size": "big"
  },
  {
    "x": -832,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": 576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 192,
    "width": 32,
    "height": 32,
    "type": "block",
    "name": "grass_small_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1280,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_2",
    "size": "big"
  },
  {
    "x": -704,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": 384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -896,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1344,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1472,
    "y": 128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1536,
    "y": 256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1216,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_2",
    "size": "big"
  },
  {
    "x": -1408,
    "y": 448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1088,
    "y": 64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1152,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -832,
    "y": 320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_2",
    "size": "big"
  },
  {
    "x": -1024,
    "y": 512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_2",
    "size": "big"
  },
  {
    "x": -960,
    "y": 640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_bottom_right_corner_2",
    "size": "big"
  },
  {
    "x": -320,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": -256,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": -192,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": -128,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": -64,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": 64,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": 128,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": 64,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": 192,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big"
  },
  {
    "x": -64,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": -128,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": -192,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": -256,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": -320,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": -384,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big"
  },
  {
    "x": 256,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big"
  },
  {
    "x": 192,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big"
  },
  {
    "x": 64,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big"
  },
  {
    "x": 128,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big"
  },
  {
    "x": 0,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big"
  },
  {
    "x": -64,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -256,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -192,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -128,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": -64,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 128,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 0,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside",
    "size": "big"
  },
  {
    "x": 64,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 64,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 704,
    "y": -128,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 704,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 704,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 768,
    "y": -64,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 768,
    "y": 0,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -256,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -320,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -704,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -704,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -704,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -704,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -640,
    "y": -448,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -640,
    "y": -384,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -640,
    "y": -320,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -640,
    "y": -256,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": -640,
    "y": -192,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -512,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -896,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 896,
    "y": -576,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 960,
    "y": -832,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 960,
    "y": -768,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 960,
    "y": -704,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 960,
    "y": -640,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1024,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -960,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 576,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 576,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 640,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 704,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 768,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 768,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 832,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 896,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 960,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 960,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 896,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 832,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 768,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 704,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 640,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 1024,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 576,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1024,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_left_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 640,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 1088,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 512,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 512,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 576,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 448,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 384,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 320,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 192,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 320,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_inside_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 256,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 256,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 128,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_top_left_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 384,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 320,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": -1216,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_bottom_right_corner_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -1152,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 192,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "stone_right_side_5",
    "size": "big",
    "perspective": "back"
  },
  {
    "x": 256,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 320,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 384,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 448,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 640,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 704,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 832,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 896,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 960,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 192,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 576,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 512,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 1088,
    "y": -1472,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 1024,
    "y": -1536,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 768,
    "y": -1600,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_right_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 128,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_top_left_corner_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 192,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 704,
    "y": -1408,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 704,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 512,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 448,
    "y": -1344,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 512,
    "y": -1280,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_inside_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 128,
    "y": -1088,
    "width": 64,
    "height": 64,
    "type": "block",
    "name": "grass_right_side_5",
    "size": "big",
    "perspective": "fore"
  },
  {
    "x": 320,
    "y": 256,
    "width": 40,
    "height": 58,
    "type": "enemy",
    "name": "TNT",
    "color": "Blue"
  }
]
```

---

## 11. QUICK REFERENCE CARD

### Enemy names (exact casing):
`"Pawn"` `"Warrior"` `"Archer"` `"TNT"` `"Torch"`

### Enemy/entity colors (exact casing):
`"Red"` `"Blue"` `"Yellow"` `"Purple"`

### Treasure names:
`"red"` `"pink"` `"green"` `"yellow"`

### Water types:
`"normal"` `"current"` `"healing"` `"toxic"` `"lava"`

### Block size keywords:
`"big"` (64×64) | `"small"` (32×32)

### Perspective values:
omit (foreground, solid) | `"back"` (background, semi-transparent, decorative)

### Palette numbers and themes:
`2`=purple-navy | `3`=sandy | `4`=mossy | `5`=snow | `6`=nether | `7`=void | `8`=autumn

### All object `"type"` values:
`"entity settings"` `"start"` `"block"` `"enemy"` `"spawn_point"` `"tree"` `"deco"` `"treasure"` `"water"` `"moving_platform"`

---

## 12. EXAMPLE TASK PHRASING

When sending this prompt to another AI, append your specific request at the end, for example:

> *"Using all the rules above, generate a Python script that writes `levels/10.json` — a large Autumn Forest theme level (palette 8) with a ruined temple in the center, two waterfalls, dense trees, and heavy enemy presence. Output the script only, no explanations."*

Or:

> *"Generate `levels/11.json` directly as a JSON array — Nether/Scorched theme (palette 6), massive lava sea, two fortresses, flying platforms, and underground cave. The level should have at least 800 objects."*

---

*Prompt authored for PIXEL ABYSS v38 by BLEMAC | blemac.dev | github.com/tech-with-blessing*
