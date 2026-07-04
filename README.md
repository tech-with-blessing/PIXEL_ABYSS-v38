# ⚔️ PIXEL ABYSS

> *Descend. Fight. Survive. Befriend the darkness — or be consumed by it.*

**PIXEL ABYSS** is a 2D pixel-art action platformer built with Python & Pygame,
featuring local multiplayer, a living world of enemies, collectibles, a built-in
level editor, and a whole lot of chaos — all wrapped in a dark, glowing abyss aesthetic.

Developed by **Blessing Machekeche** | **BLEMAC** | Zimbabwe 🇿🇼

---

![Version](https://img.shields.io/badge/version-v38-blueviolet?style=flat-square)
![Python](https://img.shields.io/badge/python-3.x-blue?style=flat-square&logo=python)
![Pygame](https://img.shields.io/badge/pygame-powered-green?style=flat-square)
![Status](https://img.shields.io/badge/status-in%20development-orange?style=flat-square)
![License](https://img.shields.io/badge/license-custom-red?style=flat-square)

---

## 🌑 WHAT IS PIXEL ABYSS?

You are dropped into a dark, sprawling pixel world crawling with enemies —
archers, skull creatures, giant beasts, and worse. Collect gems and coins,
fight or **befriend** entities, survive as long as you can, and explore
10 hand-crafted levels. Bring friends — up to **4 players** on one screen,
local co-op style.

Think: action platformer meets dungeon crawler meets chaos simulator.

---

## ✨ FEATURES

- 🗺️ **10 Levels** — hand-built, varied environments from stone dungeons to
  colourful overworlds
- 👥 **Local Multiplayer** — up to 4 players on the same screen with full
  split controls; joystick/gamepad supported
- 🤝 **Befriend System** — choose to befriend certain enemies instead of
  fighting them
- 📡 **Spectate & View Modes** — watch the battlefield from above or spectate
  another player mid-game
- 🗺️ **Minimap** — live minimap in the corner showing player and enemy positions
- 💎 **Collectibles** — coins, red gems, green gems, pink orbs — hoard everything
- ❤️ **Health System** — every entity has a visible health bar and named identity
- 🔭 **Entity Inspector** — inspect any enemy's name, type, colour, kills, and ID
- 🛠️ **Built-in Level Editor** — the dev level editor is integrated; build and
  test your own levels freely
- 🎮 **Gamepad Support** — up to 4 joysticks supported alongside keyboard play
- ⏱️ **Game Timer** — tracks your survival time per session

---

## 🎮 CONTROLS

PIXEL ABYSS supports up to 4 simultaneous local players — each with their own
keyboard region or a joystick.

### Player 1 — Left Side (Keyboard)

| Action | Key |
|--------|-----|
| Enter (Confirm) | `F` |
| Join Game | `Left Shift` |
| Ready | `Left Ctrl` |
| Move | `W` `A` `S` `D` |
| Attack | `Left Shift` |
| Dash | `Left Ctrl` |
| Zoom In | `Z` |
| Zoom Out | `X` |

---

### Player 2 — Right Side (Keyboard)

| Action | Key |
|--------|-----|
| Enter (Confirm) | `ENTER` (`RETURN`) |
| Join Game | `Right Shift` |
| Ready | `Right Ctrl` |
| Move | `↑` `←` `↓` `→` (`Arrow Keys`) |
| Attack | `Right Shift` |
| Dash | `Right Ctrl` |
| Zoom In | `N` |
| Zoom Out | `M` |

---

### 🕹️ Gamepad / Joystick
Plug in up to 4 controllers and they'll be auto-detected.
Standard joystick axes for movement; buttons map to dash and actions.

> **Note:** The networking layer is still in development. When complete,
> the player cap beyond 4 will expand. For now, all multiplayer is local.

---

## 📁 PROJECT STRUCTURE

```
PIXEL_ABYSS-v38/
│
├── pixaby.py          ← Entry point — run this to launch the game
│
├── game/              ← Core game engine and logic
│   ├── main.py        ← Game class and main loop
│   ├── settings.py    ← Global settings and version info
│   └── ...            ← Entities, physics, rendering, input, etc.
│
├── assets/            ← All sprites, tilesets, and visual resources
├── data/              ← Game data files (entity configs, etc.)
├── extras/            ← Extras and dev tools
├── levels/            ← Level files for all 10 levels
│
└── icon.ico           ← Game window icon
```

---

## 🚀 HOW TO RUN

### Requirements

- Python 3.x
- Pygame

### Install Dependencies

```bash
pip install pygame
```

### Launch the Game

```bash
python pixaby.py
```

That's it. You're in the abyss. 🌑

---

## 🗺️ LEVELS

PIXEL ABYSS currently features **10 levels** spanning multiple visual themes —
grey stone dungeons, earthy overworlds, brick ruins, and more. The game is
**still in active development**, and the integrated level editor means new
environments are always in progress.

The built-in level editor is accessible from within the game — feel free to
explore and build your own levels during development.

---

## 🤝 COLLABORATION

PIXEL ABYSS is developed and owned by **Blessing Machekeche / BLEMAC**.

Collaboration is welcome — but **by invitation/approval only**.
If you'd like to contribute, reach out first:

- 🐙 **GitHub:** [tech-with-blessing](https://github.com/tech-with-blessing)
- 📘 **Facebook:** [PythonProjects](https://www.facebook.com/profile.php?id=61578165867167)

> ⚠️ **Please read [`LICENSE.txt`](./LICENSE.txt) before forking or using any
> part of this project.** Redistribution and modification for distribution
> require explicit written permission.

---

## 🙏 CREDITS

Full credits are in [`CREDITS.md`](./CREDITS.md).

Quick shoutout:

| Creator | Contribution |
|---|---|
| **DaFluffyPotatoe** | Code implementations & associated assets |
| **PixelFrog** | Enemy sprites, blocks, tilesets & environment art |
| **TechWithTim** | Pygame platformer tutorial — the original foundation |
| **Cecil Sounds** | Sound design & audio |

---

## 📜 LICENSE

Copyright © 2024 Blessing Machekeche / BLEMAC

This project uses a **custom license** — read it fully in [`LICENSE.txt`](./LICENSE.txt).

**Short version:**
- ✅ You can view and study it
- ✅ You can run it locally
- ✅ You can collaborate — with permission
- ❌ You cannot redistribute or publish modified versions without consent

---

*Built from the ground up in Zimbabwe. Powered by Python, Pygame, and a lot of late nights. 🇿🇼*
