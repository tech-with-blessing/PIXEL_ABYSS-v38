# Feature Suggester Report
Generated: 2026-04-26 12:00
PIXEL ABYSS — v0.0.0
---

### 1. New Powerups or Items
*   **Speed Boots:** Increases `current_speed` and `walk_speed` by 50% for 10 seconds.
    *   *Implementation:* Add a `buffs` list to the `Entity` class and a timer in `update_sprite` to revert values.
*   **Shield Bubble:** Grants a one-time damage negation.
    *   *Implementation:* New `Object` in `objects.py`. When collected, set `player.shielded = True`. Modify `hit()` in `entity_utils.py` to check this flag.
*   **Triple Shot:** Modifies Archer/TNT to fire three projectiles in a spread.
    *   *Implementation:* Update `shoot_arrow` and `bomb` methods to loop three times with small angle offsets.

### 2. New Game Modes
*   **Team Battle (2v2):** 4 players split into two teams (Red vs Blue).
    *   *Implementation:* Utilize the existing `color` attribute in `Player` to determine teams. Modify `attack` logic in `objects.py` (Bombs/Arrows) to ignore same-colored entities.
*   **Last Man Standing:** Survival mode where health does not regenerate between rounds.
    *   *Implementation:* Modify the game loop in `main.py` to check for `len([p for p in self.players if not p.dead]) == 1`.
*   **Gem Rush (Timed):** Players compete to collect the most gems in 2 minutes.
    *   *Implementation:* Add a global `timer` in `Game.update_game_logic`. Track `total_gems` per player.

### 3. New Mechanics
*   **Wall Jumping:** Players can kick off walls to reach higher areas.
    *   *Implementation:* In `physics.py`, detect horizontal collisions while in the air. If true and jump button is pressed, apply a diagonal impulse (opposite `x_vel` and positive `y_vel`).
*   **Grappling Hook:** A new tool for rapid horizontal movement.
    *   *Implementation:* Extend `Arrow` class to a `Grapple` class. On collision with a `Block`, apply a force to the `owner` toward the hook's `rect.center`.
*   **Wind Zones:** Areas that push players in a specific direction.
    *   *Implementation:* Similar to `WaterZone` but without the speed penalty. Use `apply_current` in `physics.py` to apply force.

### 4. Progression or Unlockables
*   **Class Masteries:** Accumulating gems unlocks "Elite" versions of classes (e.g., *Shadow Archer* with faster fire rate).
    *   *Implementation:* Add a `progression.json` file to track total gems. Update `Player.personalise` to scale stats based on mastery level.
*   **Cosmetic Skins:** Color palettes for characters unlocked via achievements.

### 5. Visual/Audio Polish
*   **Particle Systems:** Emit "dust" particles when landing from a high fall or dashing.
    *   *Implementation:* Create a `Particle` class in `objects.py` and trigger it in `land` and `dash` events.
*   **Dynamic Audio:** Fade music volume based on player health or intensity of nearby combat.
*   **Screen Flash:** Subtle red flash on the player's viewport when taking heavy damage.

### 6. Quality of Life (QoL)
*   **Haptic Feedback:** Rumble support for controllers during explosions.
    *   *Implementation:* Call `joystick.rumble()` in the `Bomb.destroy()` method.
*   **Quick-Select Menu:** A radial menu for switching between items if multiple are held.
*   **Death Replay/Kill Cam:** Briefly show the entity that dealt the final blow.
