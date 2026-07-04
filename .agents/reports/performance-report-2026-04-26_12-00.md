# Performance Optimisation Report
Generated: 2026-04-26 12:00
PIXEL ABYSS — v0.0.0
---

## 1. Game Loop & Delta Time
**Analysis:**
- Delta time (`self.dt`) is calculated using `self.clock.tick(self.FPS) / 1000.0`.
- The FPS cap is set to 60 (`Settings.FPS = 60`), which is appropriate for a pixel art game.
- `self.dt` is clamped to a maximum of `0.1` and rounded to 3 decimal places. While clamping is good for preventing massive jumps during lag spikes, rounding can introduce micro-stuttering in movement physics.
- The `game_speed` multiplier is applied to `dt`, allowing for slow-motion or fast-forward effects.

**Issues:**
- **Rounding `dt`:** `self.dt = round(..., 3)` can cause jitter. Physics engines prefer high-precision floats.
- **Redundant Logic:** `update_game_logic` is called, and then `self.exec(self.update)` is called, which iterates over all objects again.

**Fix:**
Remove rounding from `dt` and consolidate update loops.
```python
# In server.py / windows.py
raw_dt = self.clock.tick(self.FPS) / 1000.0
self.dt = min(0.1, raw_dt * self.game_speed) # Remove round()
```

## 2. Sprite Rendering
**Analysis:**
- The game uses a custom `draw_list` and manual iteration for rendering instead of Pygame's `LayeredUpdates` or `Group`.
- **Culling:** `self.hide(obj)` is used to skip drawing off-screen objects, which is good.
- **Redrawing:** The entire screen is cleared with `self.window.fill(self.bg_color)` every frame.

**Issues:**
- **Manual Hide Checks:** Every object in the game is checked against `hide()` every frame. For large levels, this O(N) check becomes expensive.
- **Full Screen Redraw:** Using `pygame.display.update()` without arguments or `flip()` forces a full-screen refresh. In Pygame, updating only changed areas (dirty rects) is significantly faster.

**Fix:**
Use `pygame.sprite.LayeredUpdates` for automated z-order rendering and implement a more efficient culling system based on the chunk map.

## 3. Surface Caching
**Analysis:**
- Images are loaded once in `Assets.py` and converted using `.convert()` or `.convert_alpha()`.
- A custom `cache_img` and `create_cache_img` system is used to store scaled/color-swapped versions of sprites.

**Issues:**
- **UI Redraw Waste:** `RPGButton.draw` calls `pygame.draw.rect` on a cached surface EVERY frame. Since the surface is cached and shared by size, multiple buttons of the same size are fighting to draw on the same surface, and the drawing operation itself is redundant if the button state hasn't changed.
- **Cache Bloat:** The cache management in `server.main` simply clears dictionaries when they get too large. This causes massive stutters when the cache is emptied and rebuilt mid-game.

**Fix:**
Implement an LRU (Least Recently Used) cache or only redraw UI elements when their state (hover, click, text) changes.

## 4. Collision Detection
**Analysis:**
- The game uses a chunk-based map (`self.game.map`) for blocks and a `SpatialGrid` for entities.

**Issues:**
- **Inefficient Chunk Lookup:** `PHYSICS.get_objects` iterates over **ALL** chunks in the dictionary:
  ```python
  for pos, obs in map.items(): # Iterates EVERY chunk
      if obs[0].colliderect(rect):
          # ... filter objects ...
  ```
  This defeats the purpose of chunking. It should only calculate which chunks the `rect` overlaps and look up those specific keys.
- **Brute Force Filtering:** Inside each chunk, it uses `list(filter(...))` which creates a new list every frame for every entity.

**Fix:**
Calculate chunk coordinates directly:
```python
# Optimized get_objects
def get_objects_optimized(game_map, rect, chunk_size):
    cx_start = rect.left // chunk_size
    cx_end = rect.right // chunk_size
    cy_start = rect.top // chunk_size
    cy_end = rect.bottom // chunk_size
    
    nearby = []
    for x in range(cx_start, cx_end + 1):
        for y in range(cy_start, cy_end + 1):
            chunk = game_map.get((x, y))
            if chunk:
                nearby.extend(chunk[1])
    return nearby
```

## 5. Memory Usage
**Analysis:**
- Surfaces are converted correctly (`.convert()`, `.convert_alpha()`).
- Backgrounds are scaled to screen size once.

**Issues:**
- **Surface Leaks:** `parallax_bg` creates new glow surfaces via `glow_img` if they aren't in the cache. While cached, the `bg_particles` list grows and shrinks dynamically.
- **Large Particle Counts:** `parallax_bg` can handle up to 200 particles, each doing multiple blits and `set_at` calls.

**Fix:**
Pre-generate a set of particle surfaces and avoid `window.set_at`. Use `window.blits()` for batch rendering particles.

## 6. Asset Loading
**Analysis:**
- Assets are loaded at startup.
- Node creation and world prep are threaded, preventing startup hangs.

**Issues:**
- **Mid-game Stutters:** Cache clearing in `server.main` (e.g., `if len(CACHED_IMAGES) > 150: CACHED_IMAGES.clear()`) causes a significant frame drop while the game re-generates and re-scales surfaces.

**Fix:**
Increase cache limits or use a more surgical removal process (remove oldest 10% instead of `clear()`).

## 7. Python-Specific Inefficiencies
**Issues:**
- **`window.set_at`:** Used in `parallax_bg`. This is the slowest way to manipulate pixels in Pygame.
- **`pygame.font.render` every frame:** `Windows.get_fps` renders "FPS: XX" every frame.
- **Reverse List Popping:** `Game.update` uses `sorted(enumerate(objects), reverse=True)` and `pop()`. While popping from the end is O(1), sorting the enumerate is O(N log N).

**Fix:**
- Use a surface for particles instead of `set_at`.
- Cache rendered text surfaces (e.g., only update FPS text every 0.5 seconds).
- Use a simple `[obj for obj in objects if not obj.dead]` list comprehension for updating.

---
**Summary of Recommendations:**
1. **Surgically fix `PHYSICS.get_objects`** to look up specific chunks by key instead of iterating the whole map.
2. **Optimise `parallax_bg`** by removing `set_at` and reducing the number of blits per particle.
3. **Fix UI Caching** in `RPGButton` to stop redrawing on cached surfaces every frame.
4. **Throttle FPS Text Rendering** to once every 30-60 frames.
