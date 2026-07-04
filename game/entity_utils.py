import random
import math
import heapq
import pygame
from typing import Tuple, Any
import time

from .objects import Arrow, Bomb, Fire, Splash, Bubble, Treasure
from .assets import Assets
from .settings import Settings
from .functions import playit, create_cache_img, cache_assets
from .physics import find_distance, get_degree

PATH_COOLDOWN        = 0.35   # seconds between forced recomputes
                               # Lower = more responsive but more CPU
                               # Higher = cheaper but path feels "late"
                               # 0.25–0.5 is the sweet spot for most games.

PATH_RECOMPUTE_DIST  = 80     # pixels the TARGET must move before we
                               # recompute regardless of the timer.
                               # Should be roughly 1–2 tile widths.

SPRITE_SHEET_ANGLES = {
    (155, -155): 'attack_270',
    (-20, 20): 'attack_90',
    (20, 70): 'attack_45',
    (70, 110): 'attack_0',
    (110, 155): 'attack_315',
    (-70, -20): 'attack_135',
    (-110, -70): 'attack_180',
    (-155, -110): 'attack_225'
}


# Platform graph node
class PlatformNode:
    def __init__(self, rect):
        self.rect = rect
        self.neighbors = []
        self.unwanted_neighbors = []

    def __lt__(self, other):
        return (self.rect.x, self.rect.y) < (other.rect.x, other.rect.y)


def heuristic(a, b):
    return abs(a.rect.centerx - b.rect.centerx) + abs(a.rect.centery - b.rect.centery)


def get_direction(from_node, to_node):
    dx = to_node.rect.x - from_node.rect.x
    dy = to_node.rect.y - from_node.rect.y
    if dy > 0:
        return "down"
    elif dy < 0:
        return "up"
    elif dx > 0:
        return "right"
    elif dx < 0:
        return "left"
    return "none"


# TARGET SYS CLASS
class TargetSystem:
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    SAFE_GREEN = (0, 255, 0)
    WARNING_YELLOW = (255, 255, 0)
    DANGER_RED = (255, 0, 0)
    GRAY = (200, 200, 200)

    def __init__(self, owner, pointer_length=60):
        self.owner = owner
        self.game = self.owner.game
        self.pointer_length = pointer_length

    def draw_pointers(self, window=None, cam=None, zoom=None):
        for enemy in self.game.enemy_list:
            if enemy.death or enemy.dead:
                continue

            distance, dx, dy, angle, pointer_x, pointer_y = find_distance(enemy.rect.centerx, enemy.rect.centery,
                                                                          self.owner.rect.centerx,
                                                                          self.owner.rect.centery,
                                                                          self.pointer_length)

            p_x = self.owner.rect.centerx + math.cos(angle) * (self.pointer_length - 15)
            p_y = self.owner.rect.centery + math.sin(angle) * (self.pointer_length - 15)

            # Adjust color based on distance
            if distance < 300 or ((enemy.name == "TNT" or enemy.name == "Archer") and distance < 600):
                pointer_color = self.DANGER_RED
            elif distance < 600 or ((enemy.name == "TNT" or enemy.name == "Archer") and distance < 900):
                pointer_color = self.WARNING_YELLOW
            else:
                pointer_color = self.SAFE_GREEN

            offset_x = cam.x
            offset_y = cam.y
            pygame.draw.line(window, pointer_color, ((p_x - offset_x) * zoom, (p_y - offset_y) * zoom),
                             ((pointer_x - offset_x) * zoom, (pointer_y - offset_y) * zoom), int(3 * zoom))
            pygame.draw.circle(window, pointer_color,
                               (int(pointer_x - offset_x) * zoom, int(pointer_y - offset_y) * zoom), int(5 * zoom))


class ACTIVITY:

    def acquire_target(self, target_list, target_list2=None):
        self.get_nearest(target_list, target_list2)

    def can_jump(self, obj_list, vel):
        # Check each object in the obj_list
        for obj in obj_list:
            # Check if there is any vertical overlap between the player and the object
            if self.rect.bottom > obj.rect.top and self.rect.top < obj.rect.bottom:
                # Check if player is moving horizontally and could collide with the object
                if (self.rect.right + vel > obj.rect.left and self.rect.left < obj.rect.right) or (
                        self.rect.left + vel < obj.rect.right and self.rect.right > obj.rect.left):
                    # Check if there is enough space for the player to jump
                    if self.rect.bottom + vel < obj.rect.top:
                        return True  # Player can jump over object

        return False  # Not enough space to jump over object

    def reset_dir(self):
        self.timer = 0
        self.time = 0
        self.x_vel = 0

    def patrol(self):
        if self.rect.x + self.x_vel > self.spawn_point + self.patrol_range:
            self.reset_dir()
            self.patrolling = True

        elif self.rect.x + self.x_vel < self.spawn_point - self.patrol_range:
            self.reset_dir()
            self.patrolling = True

        if self.rect.x > self.spawn_point + self.patrol_range:
            self.move_left(self.current_speed)
            self.patrolling = True

        elif self.rect.x < self.spawn_point - self.patrol_range:
            self.move_right(self.current_speed)
            self.patrolling = True

        else:
            self.patrolling = False

    def chase(self):
        """
        Makes the object chase the target within vertical and horizontal bounds.

        """
        # Check if the target is within the vertical bounds of the object

        if self.rect.top - self.acquire_up < self.target.rect.bottom and self.rect.bottom + self.acquire_down > self.target.rect.top:

            # If the target is to the right and outside the chase range

            if self.target.rect.right <= self.rect.left and self.target.rect.right - self.rect.left <= -self.chase_range:

                self.move_left(self.current_speed)  # Move right to chase the target
                self.chasing = True
                self.attacking = False
                self.evading = False

            # If the target is to the left and outside the chase range

            elif self.target.rect.left >= self.rect.right and self.target.rect.left - self.rect.right >= self.chase_range:

                self.move_right(self.current_speed)  # Move right to chase the target
                self.chasing = True
                self.attacking = False
                self.evading = False

            # If the target is within the chase range
            else:
                self.chasing = False  # Stop chasing (target is close enough)

        # If the target is not within the vertical bounds
        else:
            self.chasing = False  # Stop chasing

    def evade_2(self):
        self.attacking = False
        self.chasing = False
        self.evading = True

        if self.evade_time > self.evade_max_time:
            self.evade_max_time = random.randint(3, 10)
            self.evade_time = 0
            self.decision = random.choice(['left', 'right'])

        self.evade_time += self.game.dt

        if self.decision == 'left':
            self.move_left(self.current_speed)
        else:
            self.move_right(self.current_speed)

    def follow_path(self):
        if not self.path or not self.target or not self.game.env_ready:
            return
        self.chasing = True
        self.attacking = False
        self.evading = False
        next_node = self.path[0]
        dx = next_node.rect.centerx - self.rect.centerx
        dy = next_node.rect.top - self.rect.bottom

        if dx > 0:
            self.move_right(self.current_speed)
            self.state = "Walking Right"
        elif dx < 0:
            self.move_left(self.current_speed)
            self.state = "Walking Left"

        if dy < -64:
            if self.zone:
                self.swim_up()
                self.state = "Swimming_Up"

            elif self.jump_count < 1 or self.jump_count == 1 and self.fall_count > 0.1:
                self.jump()
                self.state = "Jumping"

        if next_node.rect.collidepoint(self.rect.centerx, self.rect.bottom):
            self.path.pop(0)
            self.completed_path += 1
        self.action = dx

    def evade(self):
        if self.rect.colliderect(self.target.rect):
            self.evade_2()

        elif self.evading:
            self.evade_2()
            self.evading = False
            self.evade_time = 0

    def hit(self, enemy, obj=None, type_=None):
        if type_ == 'fire':
            playit("scream", self)
            self.health -= obj.attack_power
        else:
            self.health -= enemy.attack_power

        playit('pain', self)
        if self.health <= 0 and not (self.death or self.dead):
            if obj in ['arrow', 'bomb'] and self.type == 'player':
                self.game.game_speed = 0
            enemy.kills += 1

        if not self.target:
            self.target = enemy

        # self.animation_count = 0
        self.hurt = True

    def attack(self):

        if self.type == 'player':
            self.attacking = True
            self.sprite_sheet = "attack_1"

        if not self.target:
            return

        if (
            self.rect.top - self.attack_up - self.clear_shot_up < self.target.rect.bottom and 
            self.rect.bottom + self.attack_down + self.clear_shot_down > self.target.rect.top or self.name == "TNT"
            ):
            if (
                    self.target.rect.right <= self.rect.left and self.target.rect.right - self.rect.left >= 
                    -(self.attack_range - self.clear_shot_range)
                ) or (
                    self.target.rect.left >= self.rect.right and self.target.rect.left - self.rect.right <= 
                    (self.attack_range - self.clear_shot_range)
                ):
                self.attacking = True
                self.sprite_sheet = "attack_1"

                if self.rect.centerx < self.target.rect.centerx:
                    self.direction = "right"
                elif self.rect.centerx > self.target.rect.centerx:
                    self.direction = "left"

                if self.sprite_index == self.attack_que:

                    if self.name == 'Torch':
                        if self.wait > self.attack_delay:
                            playit("throw_2", self)
                            self.fire(self.target)
                            return
                        else:
                            # Hit with fire stick
                            if self.target.type == "player":
                                self.target.shake_frames = max(self.target.shake_frames,
                                                               8)  # Apply shake for next few frames
                                self.target.shake_intensity = max(self.target.shake_intensity, 6)

                            self.target.hit(self)
                            if self.target.nature == 'entity':
                                self.knockback()

                    elif self.name == "TNT":
                        if self.wait > self.attack_delay:
                            mine = [bomb for bomb in self.game.bombs.list if bomb.owner == self]

                            if len(mine) <= self.bomb_limit:
                                playit("throw_2", self)
                                self.bomb()

                    elif self.name == "Archer":
                        if self.wait > self.attack_delay:
                            playit("throw_2", self)
                            self.shoot_arrow()

                    else:
                        if self.wait > self.attack_delay:
                            if self.target.nature == 'damageable_object' and self.name == "Pawn":
                                self.sprite_sheet = 'attack_2'
                                playit("hit_2", self)
                                self.target.hit(self)
                                return

                            if self.target.type == "player":
                                self.target.shake_frames = max(self.target.shake_frames,
                                                               8)  # Apply shake for next few frames
                                self.target.shake_intensity = max(self.target.shake_intensity, 4)

                            if self.name == "Pawn":
                                playit("hit_2", self)
                            else:
                                playit('cut_2', self)

                            self.target.hit(self)
                            if self.target.nature == 'entity':
                                self.knockback()
            else:
                if not self.type == 'player':
                    self.attacking = False
        else:
            if not self.type == 'player':
                self.attacking = False

    def fire(self, target):

        fire_obj = Fire(target.rect.centerx, target.rect.bottom - 36, self)
        self.game.fire_list.append(fire_obj)
        self.game._draw_list_dirty = True
        self.wait = 0

    def bomb(self):

        bomb_obj = Bomb(self.rect.x, self.rect.y, self, self.game.sounds)
        bomb_obj.update_sprite()
        bomb_obj.rect.center = self.rect.center

        start_pos = self.rect.center
        target_pos = self.target.rect.center

        time_to_hit = 1
        bomb_obj.time = 0
        bomb_obj.gravity = self.current_gravity * bomb_obj.mass

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]

        bomb_obj.x_vel = dx / time_to_hit
        bomb_obj.y_vel = (dy - 0.5 * bomb_obj.gravity * time_to_hit ** 2) / time_to_hit

        '''
        bomb_obj.degree, _ = get_degree(bomb_obj.x_vel, bomb_obj.y_vel, bomb_obj.degree)
        '''
        self.game.bombs.list.append(bomb_obj)
        self.game._draw_list_dirty = True

        if self.type != 'player':
            self.wait = 0

    def shoot_arrow(self):

        arrow_obj = Arrow(100, -200, self, self.game.sounds)
        arrow_obj.rect.center = self.rect.midtop

        arrow_obj.update()
        arrow_obj.update_sprite()
        
        arrow_obj.rect.center = self.rect.center

        start_pos = self.rect.center
        target_pos = self.target.rect.center
        
        time_to_hit = 1
        arrow_obj.time = 0
        arrow_obj.gravity = self.current_gravity * arrow_obj.mass

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]

        arrow_obj.x_vel = dx / time_to_hit
        arrow_obj.y_vel = (dy - 0.5 * arrow_obj.gravity * time_to_hit ** 2) / time_to_hit

        arrow_obj.degree, _ = get_degree(arrow_obj.x_vel, arrow_obj.y_vel, arrow_obj.degree)
        
        self.game.bombs.list.append(arrow_obj)
        self.game._draw_list_dirty = True
        self.wait = 0

        playit("arrow_fly", self)


    def wander(self):

        self.wandering = True

        if self.timer >= self.time:
            self.choice = random.choice(sorted(self.activities))
            self.time = random.uniform(0.0, 1.5)
            self.timer = 0

        self.timer += self.game.dt

        if 'wl' in self.choice:
            self.move_left(self.walk_speed)

        elif 'wr' in self.choice:
            self.move_right(self.walk_speed)

        elif 'rl' in self.choice:
            self.move_left(self.current_speed)

        elif 'rr' in self.choice:
            self.move_right(self.current_speed)

        elif 'il' in self.choice:
            self.x_vel = 0
            self.direction = 'left'

        elif 'ir' in self.choice:
            self.x_vel = 0
            self.direction = 'right'

        elif 'j' in self.choice:
            self.jump_choice = random.choice(['single', 'double'])
            if self.zone:
                self.swim_up()
            elif self.jump_count < 2:
                self.jump()

        elif 'on' in self.choice:
            self.animation_name = 'on'

        elif 'off' in self.choice:
            self.animation_name = 'off'

        elif "laugh" in self.choice:
            playit("laugh", self)
            self.time = 0

        elif 'confused' in self.choice:
            self.feelings.add('confusion')
            self.time = 0

        elif 'chat' in self.choice:
            self.feelings.add('chat')
            self.time = 0

    def control(self):
        if self.control_type == "joystick":
            self.game.joybuttondown(self)

        elif self.control_type == "touch":
            if self.dead:
                if not self.game.done:
                    self.game.done = True
                if self.id == 0:
                    self.game.running = False

            self.game.handle_finger_movement()

        else:
            if self.game.keys:
                self.game.handle_keypress(self)
            if self.dead:
                if not self.game.done:
                    self.game.done = True

    def think(self):

        if self.auto and not self.death and not self.dead:
            if not self.stepping_on_platform and not self.dashing:
                self.x_vel = 0
            if self.has_target:
                if not self.evading and not self.attacking:  # and not self.finding_way
                    self.follow_path()  # self.chase()
                self.evade()
                if not self.evading:
                    self.attack()
                self.wandering = False
                self.patrolling = False

            else:
                if self.patroller:
                    self.patrol()
                else:
                    self.patrolling = False

                if not self.patrolling:
                    self.wander()

                self.chasing = False
                self.evading = False
                self.attacking = False
                self.finding_way = False

        elif self.type == 'player':
            if not self.stepping_on_platform and not self.dashing:
                self.x_vel = 0

            self.control()

            if self.auto_attack:
                self.attack()


# ENTITY CLASS
class Entity(ACTIVITY):
    GRAVITY = 800
    ANIMATION_DELAY = 1
    total = -1

    def __init__(self, x, y, width, height, name='TNT', color='Yellow', game='None', group=None):

        # Coordinates
        super().__init__()
        self.origin_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, 100, 100)
        self.a, self.b = (0, 0)
        self.the_height = self.rect.height
        self.spawn_point = x
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.kill_choice = 'kill my enemies with different color and players with different color'

        # Attributes
        self.name = name
        self.color = color

        # Current Sprite
        self.sprite = cache_assets((name, color, "idle_right"), index=0)
        self.mask = pygame.mask.from_surface(self.sprite)
        self.animation_count = 0
        self.sprite_sheet = 'run'

        self.feelings   = set()
        self.activities = {'wl', 'wr', 'rl', 'rr', 'il', 'ir', 'c', 'j'}

        self.image_index = 0

        # Speeds
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 200
        self.walk_speed = 100
        self.jump_vel = -400
        self.acceleration = 0.5
        self.duration = 0
        self.sprite_index = 0
        self.knocking_back = 0
        self.attack_delay = 1

        # Secondary Attributes
        self.patroller = False
        self.auto_attack = False
        self.avenger = False  # Deals with one player until dead or gone

        # Targets
        self.target_list = []
        self.targets_in_range = []
        self.friends = []
        self.target = None
        self.has_target = False
        self.group = None

        # Status
        self.dead = False
        self.death = False
        self.crouching = False
        self.hit_wall = False
        self.chasing = False
        self.attacking = False
        self.wandering = False
        self.evading = False
        self.patrolling = False
        self.patroller = False
        self.finding_way = False
        self.on_land = False
        self.bumb_head = False
        self.on_ground = False
        self.mad = False

        # Status Values
        self.kills = 0
        self.health = 100
        self.vitality = 1
        self.hit_count = 0
        self.count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit_wall_for = 0

        self.emerald_coins = 0
        self.gold_coins = 0
        self.ruby_coins = 0
        self.pearl_coins = 0

        # Strength
        self.knockback_power = 200
        self.attack_power = 20
        self.bomb_limit = 5

        # Times and Timers
        self.timer = 0
        self.time = 0
        self.evade_time = 0
        self.evade_max_time = 0

        self.initiate_ranges_and_limits()

        # Decisions
        self.direction = "left"
        self.sheet_name = self.sprite_sheet + "_" + self.direction
        self.decision = 'left'
        self.choice = 'wl'
        self.jump_choice = 'single'

        # Bombs
        self.bomb_limit = 5
        self.wait = 0

        self.game = game

        self.nature = 'entity'
        self.morex = 0
        self.morey = 0
        self.entity_id = 0
        self.is_there = False
        self.ignore_objects = False
        self.last = ''
        self.t = ''
        self.mass = 1
        self.time_accumulator = 0
        self.frame_duration = 0.1
        self.on_ground_for = 0
        self.in_air_for = 0

        self.action = ''

        self.current_speed = self.speed
        self.current_gravity = Settings.GRAVITY
        self.current_jump = self.jump_vel
        self.stepping_on_platform = False

        self.max_health = 100
        self.oxygen = 100
        self.max_oxygen = 100
        self.zone = None
    
        self.path              = []
        self._path_timer       = 0.0   # seconds since last A* call
        self._path_target_pos  = None  # (x, y) of target when path was computed
 
 
        # OPT-6: sprite direction cache
        # Stores (name, color, sheet_name) → sprite list so Assets is only
        # walked once per unique combination, not once per frame.
        self._sprite_cache    = {}
        # Last resolved key — if this matches the current key, skip the lookup.
        self._last_sheet_key  = None

        self.stuck = False

        self.swim_strength = 300
        self.dashing = False
        self.startx = 0
        self.starty = 0
        self.history = []

        self.history_zoom = 1
        self.see_through = {}
        self.zoom = 1

        self.missed = 0
        self.clear_shot_range = 0
        self.completed_path = 0
        self.value = 5
        self.clear_shot_up = 0
        self.clear_shot_down = 0

        self.in_screen = True
        self.teleport_x = True

    def initiate_ranges_and_limits(self):
        # Ranges
        self.patrol_range = 100
        self.chase_range = 10
        self.evade_range = 43
        self.attack_range = 50
        self.attack_que = 3

        # Limits
        self.chase_bottom = 50
        self.chase_top = 50

        self.acquire_up = 300
        self.acquire_down = 300
        self.acquire_range = 1000

        self.crouch_height = 40
        self.chase_space = 100

    def personalise(self, times=1):
        self.title = f'The {self.color} {self.name} number {self.entity_id}'
        self.rect = pygame.Rect(self.rect.x, self.rect.y, 43, 37)

        if self.type == "player":
            self.activities = {'wl', 'wr', 'rl', 'rr', 'il', 'ir', 'j'}

        elif self.type == "enemy":
            self.activities = {'wl', 'wr', 'rl', 'rr', 'il', 'ir', 'j', 'laugh', "confused"}

        if self.name == "Archer":
            if times == 1:
                self.health = 100

            self.acquire_up = 300
            self.acquire_down = 300
            self.acquire_range = 1000

            self.patrol_range = 1000
            self.chase_range = 500
            self.evade_range = 50

            self.attack_up = 300
            self.attack_down = 300
            self.attack_range = 600
            self.attack_que = 5
            self.attack_delay = 0.5
            
            self.chase_bottom = 500
            self.chase_top = 500
            self.chase_space = 100

        if self.name == "TNT":
            if times == 1:
                self.health = 100

            self.acquire_up = 300
            self.acquire_down = 300
            self.acquire_range = 1000

            self.patrol_range = 1000
            self.chase_range = 500
            self.evade_range = 50

            self.attack_up = 300
            self.attack_down = 300
            self.attack_range = 600
            self.attack_que = 2

            self.chase_bottom = 500
            self.chase_top = 500
            self.chase_space = 100

        elif self.name == "Warrior":
            if times == 1:
                self.health = 80
            self.initiate_ranges_and_limits()
            self.acquire_up = 300
            self.acquire_down = 300
            self.acquire_range = 1000

            self.attack_up = 50
            self.attack_down = 50
            if self.type == 'player':
                self.attack_power = 15
            else:
                self.attack_power = 4

            self.chase_range = 30

        elif self.name == "Pawn":
            if times == 1:
                self.health = 50
            self.initiate_ranges_and_limits()

            self.acquire_up = 300
            self.acquire_down = 300
            self.acquire_range = 1000

            if self.type == 'player':
                self.attack_power = 9
            else:
                self.attack_power = 2.5

            self.attack_up = 50
            self.attack_down = 50
            self.attack_range = 40

            self.chase_range = 20

        elif self.name == "Torch":
            if times == 1:
                self.health = 65
            self.initiate_ranges_and_limits()

            self.acquire_up = 300
            self.acquire_down = 300
            self.acquire_range = 1000

            self.attack_up = 50
            self.attack_down = 50

            if self.type == 'player':
                self.attack_power = 12
            else:
                self.attack_power = 3

            self.chase_range = 30

    def isnext(self, a, b, history):
        return len(history[history.index(a):history.index(b)]) == 2
        
    def find_path(self, start_node, end_node):
        self.blacklist = set()
        open_set = []
        heapq.heappush(open_set, (0, start_node, []))  # Add path history
        came_from = {}
        g_score = self.game.g_score.copy()
        g_score[start_node] = 0

        while open_set:
            _, current, history = heapq.heappop(open_set)

            if current == end_node:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in current.neighbors:
                direction = get_direction(current, neighbor)
                new_history = history[-2:] + [(direction, neighbor)]
                direction_history = [history[0] for history in new_history]
                neighbor_history = [history[1] for history in new_history]

                # Check for 3 consecutive vertical moves
                if direction_history == ["up", "up", "up"] or direction_history == ["down", "down", "down"]:
                    new_history = []
                    self.blacklist.add(neighbor_history[1])  # Save the last 3 nodes
                    continue

                # Skip if this sequence is blacklisted
                if neighbor in self.blacklist:
                    if self.game.debug.get('1', False):
                        self.blacklist.clear()
                        continue

                tentative_g = g_score[current] + heuristic(current, neighbor)

                if direction_history[-2:] == ["up", 'left'] or direction_history[-2:] == ["up", 'right']:
                    tentative_g += 20
                elif direction_history == ["up", "up", "left"] or direction_history == ["up", "up", "right"]:
                    tentative_g += 20

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    heapq.heappush(open_set, (tentative_g + heuristic(neighbor, end_node), neighbor, new_history))

        return []

    def get_closest_node(self, rect):
        closest = None
        min_dist = float('inf')
        for node in self.get_objects(self.game.node_map, rect, 128):
            dist = heuristic(node, PlatformNode(rect))
            if dist < min_dist:
                min_dist = dist
                closest = node

        return closest

    def update_sprite2(self):
        try:
            character_sprites = Assets.ENEMY_SPRITES[self.name][self.color]
            sprite_sheet_name = self.sprite_sheet + "_" + self.direction
            sprites = character_sprites[sprite_sheet_name]
            self.sprite = sprites[self.sprite_index]
        except Exception as e:
            print(e)
        self.update()

    def update(self) -> None:
        if not self.death:
            pass # sprite = Assets.ENEMY_RECT_SPRITES[self.name][self.sheet_name][self.sprite_index]
        else:
            sprite = self.sprite
        
        if 'attack_' in self.sprite_sheet and self.name == 'Archer':
            self.sprite_sheet = 'attack'

        image_key = (self.name, self.sprite_sheet)  # Round to avoid excessive keys
        
        # Use cached image if available
        if image_key in Assets.ENEMY_RECT_SPRITES:
            self.mask, rect = Assets.ENEMY_RECT_SPRITES[image_key]

        self.morex = 0
        self.morey = 70
        
        if self.name == 'Warrior':
            self.morex = 76

        elif self.name == 'Torch':
            self.morex = 76

        elif self.name == 'TNT':
            self.morex = 76

        elif self.name == 'Pawn':
            self.morex = 80

        elif self.name == 'Archer':
            self.morex = 75

        if self.death:
            self.morey = 0
            self.morex = 0

        if image_key in Assets.ENEMY_RECT_SPRITES:
            self.rect = pygame.Rect(self.rect.x, self.rect.y, rect[0], rect[1])
        else:
            self.rect = sprite.get_rect(topleft=self.rect.topleft)

        if image_key not in Assets.ENEMY_RECT_SPRITES:
                self.mask = pygame.mask.from_surface(sprite)
        
        if image_key not in Assets.ENEMY_RECT_SPRITES:
            Assets.ENEMY_RECT_SPRITES[image_key] = self.mask, self.rect.size

    def get_sprite_sheet_name(self) -> str:
        """Get sprite sheet name based on entity state."""
        # Check if entity is attacking
        if self.attacking:
            if self.type == 'player':
                self.attack()
                self.duration += 1

            # Handle Archer's attack
            if self.name == 'Archer':
                if self.sprite_index == 1:
                    playit("pull_bow_string", self)
                return self.get_archer_attack_sprite_sheet()
            
            # Handle Pawn's attack on damagable objects
            elif self.target and self.target.nature == 'damageable_object' and self.name == "Pawn":
                return 'attack_2'
            
            # Default attack sprite sheet
            else:
                return 'attack_1'
        
        # Check if entity is running
        elif self.x_vel != 0:
            if self.type == 'player':
                if self.x_vel > 0:
                    self.move_right(self.x_vel)
                else:
                    self.move_left(abs(self.x_vel))
            return 'run'
        
        # Default idle sprite sheet
        else:
            return 'idle'

    def get_archer_attack_sprite_sheet(self) -> str:
        """Get sprite sheet name for Archer's attack."""
        # Create a temporary Arrow object
        arrow_obj = Arrow(self.rect.x, self.rect.y, self, self.game.sounds)
        arrow_obj.rect.center = self.rect.center
        arrow_obj.update()
        arrow_obj.update_sprite()

        start_pos = (self.rect.x, self.rect.y)
        if self.target:
            target_pos = (self.target.rect.x, self.target.rect.y)
        else:
            self.feelings.add('what')

            return 'attack_270'
            direction = 1 if self.direction == 'right' else -1
            big = max(10 * direction, 100 * direction)
            small = min(10 * direction, 100 * direction)
            target_pos = (self.rect.x + random.randint(small, big), self.rect.y + random.randint(-100, 100))

        time_to_hit = 1
        arrow_obj.time = 0
        arrow_obj.gravity = self.current_gravity * arrow_obj.mass

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        
        true_distance = math.sqrt(dx ** 2 + dy ** 2)
        if true_distance == 0:
            # Handle division by zero
            return 'attack_270'
        
        arrow_obj.x_vel = dx / time_to_hit
        arrow_obj.y_vel = (dy - 0.5 * arrow_obj.gravity * time_to_hit ** 2) / time_to_hit

        # Calculate degree
        degree, _ = get_degree(arrow_obj.x_vel, arrow_obj.y_vel, arrow_obj.degree)

        del arrow_obj

        # Determine sprite sheet based on angle
        for angle_range, sprite_sheet in SPRITE_SHEET_ANGLES.items():
            if angle_range[0] > angle_range[1]:
                if degree > angle_range[0] or degree <= angle_range[1]:
                    return sprite_sheet
            elif angle_range[0] <= degree < angle_range[1]:
                return sprite_sheet

        # Default sprite sheet
        return 'attack_270'

    def zone_process(self):
        if random.random() < 0.05:
            if self.zone.water_type == "normal":
                self.game.bubbles.append(Bubble(self.rect.centerx, self.rect.bottom, game=self.game))
                self.game._draw_list_dirty = True
            elif self.zone.water_type == "toxic":
                self.game.bubbles.append(
                    Bubble(self.rect.centerx, self.rect.bottom, color=(100, 255, 100), game=self.game))
                self.game._draw_list_dirty = True
            elif self.zone.water_type == "healing":
                self.game.bubbles.append(
                    Bubble(self.rect.centerx, self.rect.bottom, color=(100, 255, 100), game=self.game))
                self.game._draw_list_dirty = True
            elif self.zone.water_type == "lava":
                self.game.bubbles.append(
                    Bubble(self.rect.centerx, self.rect.bottom, color=(255, 100, 0), game=self.game))
                self.game._draw_list_dirty = True

        if self.fall_count >= 0.3:
            splash_color = {
                "normal": (50, 50, 255, 180),
                "current": (100, 100, 255, 180),
                "toxic": (50, 155, 50, 180),
                "healing": (100, 255, 100, 180),
                "lava": (255, 75, 0, 180)
            }.get(self.zone.water_type, (180, 220, 255, 180))
            self.game.splashes.extend([Splash(self.rect.centerx, self.zone.rect.top, color=splash_color, game=self.game) for i in range(10)])
            playit("splash", self)
            self.game._draw_list_dirty = True


    def _manage_pathfinding(self) -> None:
        """
        Cached A* pathfinding.  Drop this method into the Entity class and
        call   self._manage_pathfinding()   in manage() instead of the raw
        find_path block.

        Recomputes the path only when:
        • PATH_COOLDOWN seconds have elapsed  (time-based throttle)
        • The target has moved >= PATH_RECOMPUTE_DIST pixels  (position check)
        • self.path is empty  (no path yet — covers first frame & path exhausted)

        self.game.dt must be correct (non-zero) for the timer to work.
        """

        # Nothing to do if there is no target or physics aren't ready
        if not self.target:
            self.path             = []
            self._path_timer      = 0.0
            self._path_target_pos = None
            return

        # Only pathfind when grounded (or in water) — same condition as before
        can_pathfind = (
            self.game.env_ready and
            ((self.in_air_for < 0.5 and self.jump_count == 0) or self.zone)
        )
        if not can_pathfind:
            return

        # ── Decide whether to recompute ─────────────────────────────────────
        target_pos    = (self.target.rect.centerx, self.target.rect.centery)
        timer_expired = self._path_timer <= 0.0
        path_empty    = not self.path

        target_moved  = False
        if self._path_target_pos is not None:
            dx = target_pos[0] - self._path_target_pos[0]
            dy = target_pos[1] - self._path_target_pos[1]
            # Use squared distance to avoid sqrt — compare against dist²
            target_moved = (dx * dx + dy * dy) > PATH_RECOMPUTE_DIST ** 2

        should_recompute = timer_expired or path_empty or target_moved

        if should_recompute:
            start = self.get_closest_node(self.rect)
            end   = self.get_closest_node(self.target.rect)

            if start and end:
                self.path = self.find_path(start, end)

            # Reset the timer and record where the target was
            self._path_timer      = PATH_COOLDOWN
            self._path_target_pos = target_pos

        else:
            # Just tick the cooldown timer down
            self._path_timer = max(0.0, self._path_timer - self.game.dt)


    def manage(self) -> None:
        self.current_speed = self.speed
        self.current_gravity = Settings.GRAVITY
        self.current_jump = self.jump_vel

        if self.zone:
            self.current_jump = self.swim_strength
            self.current_speed = self.swim_strength
            self.zone.affect(self)

        if self.health <= 0:
            self.health = 0
            self.death = True

        # if not self.stepping_on_platform:
        self.y_vel += (self.current_gravity * self.mass) * self.game.dt

        if self.rect.x > self.game.maxx:
            self.rect.x = self.game.minx
            self.x_vel = 32
            self.teleport_x = True

        elif self.rect.x < self.game.minx:
            self.rect.x = self.game.maxx
            self.x_vel = -32
            self.teleport_x = True
            
        self.collide()

        if self.rect.y > self.game.maxy:
            if self.type == "enemy":
                self.rect.x = 0
            self.rect.y = -200

        if not self.dead:
            self.target_list = self.game.all_entities
            nearby = self.game.spatial_grid.query(self.rect, self.acquire_range)
    
            if (self.name in ["Pawn", "TNT", "Torch", "Archer"]) and not self.ignore_objects:
                deco = list(filter(lambda target: target.nature == 'damageable_object', self.game.damageable_objects))
                self.acquire_target(nearby, deco)
            else:
                self.acquire_target(nearby)

        if self.death or self.dead or self.health <= 0:
            self.has_target = False
            self.target = None

        if self.zone:
            self.zone_process()
            self.fall_count = 0

        if not self.dead:
            if self.target:
                self._manage_pathfinding()

                if self.missed > 4:
                    self.clear_shot_range = min(self.attack_range - 64, 64 * (self.missed - 4))
                elif self.missed > 9:
                    self.clear_shot_up = min(self.attack_up - 64, 64 * (self.missed - 9))
                    self.clear_shot_down = min(self.attack_down - 64, 64 * (self.missed - 9))
            else:
                # Clear space
                self.path = []
                self._path_timer      = 0.0
                self._path_target_pos = None
                
                # To reset to a distance where he can get a shot
                self.clear_shot_range = 0
                self.clear_shot_up = 0
                self.clear_shot_down = 0
                self.missed = 0

            self.think()

    
    def _resolve_sprites(self, sheet_name: str):
        """
        Return the sprite list for (self.name, self.color, sheet_name).

        Checks self._sprite_cache first.  Only walks Assets.ENEMY_SPRITES on a
        cache miss — i.e. the first time this combination is seen.

        The cache lives on the entity instance so it is automatically garbage-
        collected when the entity is removed.  No manual invalidation needed
        because name and color never change mid-life for an entity.

        Parameters
        ----------
        sheet_name : the full key into character_sprites, e.g. 'run_right'

        Returns
        -------
        list of pygame.Surface
        """
        cache_key = (self.name, self.color, sheet_name)

        if cache_key not in self.game.entity_sprite_cache:
            # Cache miss — walk the Assets dict once and store the result.
            # This branch runs at most once per unique (name, color, sheet_name)
            # combination for the lifetime of the entity.
            try:
                self.game.entity_sprite_cache[cache_key] = (
                    cache_assets((self.name, self.color, sheet_name))
                )
            except KeyError:
                # Sheet doesn't exist — return empty list so caller can handle it
                # gracefully (same behaviour as before, but now explicit).
                 self.game.entity_sprite_cache[cache_key] = []

        return self.game.entity_sprite_cache[cache_key]


    def update_sprite(self) -> None:
        if not self.dead:
            if not self.death:
                if self.type == 'enemy':
                    if self.hit_wall_for > 20 and self.jump_count < 2 and self.chasing:
                        self.jump()

                """Update sprite sheet."""
                self.sprite_sheet = self.get_sprite_sheet_name()
                
                if not (self.name == 'Archer' and 'attack' in self.sprite_sheet):
                    # Try to get sprite sheet with direction
                    sheet_name = self.sprite_sheet + "_" + self.direction
                
                # Fallback for Archer
                else:
                    sheet_name = self.sprite_sheet
                
                # OPT-6: only resolve from Assets when the key actually changed
                if sheet_name != self._last_sheet_key:
                    self.sheet_name      = sheet_name
                    self.sprites         = self._resolve_sprites(sheet_name)
                    self._last_sheet_key = sheet_name
                
                if self.sprite_index >= len(self.sprites) - 1 and self.type == 'player':
                    self.duration = 0

            else:

                self.sheet_name = self.sprite_sheet + "_" + self.direction

                # PLAYER DEATH EVENT
                if not self.sprite_sheet == 'death' and not self.sprite_sheet == 'sink':
                    playit('death', self)
                    
                    # DROP COINS
                    self.game.treasure_list.extend(
                        [Treasure(self.rect.centerx - 20, self.rect.centery - 20, 'yellow', self.game, 'dropped') for i
                        in
                        range(self.value)])
                    self.game._draw_list_dirty = True

                    
                    self.value = 0
                    self.animation_count = 0
                    self.sprite_index = 0
                    self.sprite_sheet = 'death'
                    self.sheet_name = self.sprite_sheet + "_" + self.direction

                death_key = self.sheet_name   # already set earlier in this branch
                if death_key != self._last_sheet_key:
                    self.sprites         = Assets.DEAD_SPRITES[death_key]
                    self._last_sheet_key = death_key

                if self.sprite_index == len(self.sprites) - 1 and self.sprite_sheet == 'death':
                    self.sprite_sheet = 'sink'
                    self.animation_count = 0
                    self.sprite_index = 0
                
                if self.sprite_index == len(self.sprites) - 1 and self.sprite_sheet == 'sink':
                    if self.fall_count < 2 or self.rect.y >= 2000:
                        if not self.dead:
                            pass # self.game.dead_entities.append(self)
                        self.dead = True

                death_key = self.sheet_name   # already set earlier in this branch
                if death_key != self._last_sheet_key:
                    self.sprites         = Assets.DEAD_SPRITES[death_key]
                    self._last_sheet_key = death_key

            self.time_accumulator += self.game.dt
            
            if self.animation_count == 0 and self.sprite_index != 0:
                self.sprite_index = 0
                self.time_accumulator = 0
            
            if (self.in_screen or self.death or 'attack' in self.sprite_sheet) and self.time_accumulator >= self.frame_duration:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
                self.time_accumulator = 0
                self.animation_count += 1
    
            if self.sprite_index > len(self.sprites) - 1:
                self.sprite_index = 0
            
            self.sprite = self.sprites[self.sprite_index]
            self.image = self.sprite
            
            if self.attacking:
                self.wait += self.game.dt

            self.update()

        else:
            self.sheet_name = 'death_' + self.direction
            death_key = self.sheet_name   # already set earlier in this branch
            if death_key != self._last_sheet_key:
                    self.sprites         = Assets.DEAD_SPRITES[death_key]
                    self._last_sheet_key = death_key
            self.sprite = self.sprites[-1]
            self.update()

        if not self.dead:
            self.update_thoughts_and_feelings()

        
    def update_thoughts_and_feelings(self) -> None:

        self.is_there = False
        if self.friends and self.targets_in_range:
            for friend in self.friends:
                if friend in self.targets_in_range:
                    self.is_there = True
                    
                    self.activities.add('chat')

                    friend.activities.add('chat')
                    
                    if 'chat' in friend.feelings:
                        self.feelings.add('chat')

        if not self.is_there:
            self.activities.discard('chat')
            self.feelings.discard('chat')
            
        if self.health <= 25:
            self.feelings.add('tired')

        else:
            self.feelings.discard('tired')

        if self.fall_count > 0.75:
            self.feelings.add('huh')

        else:
            self.feelings.discard('huh')

        if self.target:
            self.feelings.add('kill')

            self.feelings.discard('confusion')
            self.feelings.discard('what')

        else:
            self.feelings.discard('kill')

        if self.chasing or self.evading:
            self.feelings.add('nerve')

        else:
            self.feelings.discard('nerve')

    def update_health_bar(self) -> tuple[int, Any]:

        bar = min(100, max(0, int(self.health)))

        # Health Bar
        if self.health <= 25:
            color = Settings.RED
        elif self.health <= 50:
            color = Settings.ORANGE
        elif self.health <= 75:
            color = Settings.YELLOW
        elif self.health <= 100:
            color = Settings.GREEN
        else:
            color = Settings.PURPLE

        return bar, color

    def draw_health_bar(self, win, offset_x, offset_y, zoom=None) -> pygame.Rect:

        bar, color = self.update_health_bar()

        health_bar_rect = pygame.Rect(self.rect.centerx - (bar / 2), self.rect.y - 20, bar, 10)

        pygame.draw.rect(win, color, (
            (health_bar_rect.x - offset_x) * zoom, (health_bar_rect.y - offset_y) * zoom,
            health_bar_rect.width * zoom,
            health_bar_rect.height * zoom), border_radius=20)

        text = Settings.health_font.render(f"Health {int(self.health)}", True, color)

        zoom_key = int(self.health)

        # Use cached image if available
        if zoom not in self.game.CACHED_ENTITY_ZOOM_IMAGES:
            self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom] = {}
        
        if zoom_key in self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom]:
            scaled_image = self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key]
        
        else:    
            width = text.get_width()
            height = text.get_height()
            scaled_size = (
                int(width * zoom),
                int(height * zoom)
            )
            scaled_image = pygame.transform.scale(text, scaled_size)
            self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key] = scaled_image

        win.blit(scaled_image,
                 ((self.rect.centerx - (bar / 2) - offset_x + bar + 5) * zoom, (self.rect.y - 20 - offset_y) * zoom))

        return health_bar_rect

    def show_thoughts_and_feelings(self, health_bar_rect, win, offset_x, offset_y, zoom=None) -> None:
        for i, feeling in enumerate(self.feelings):
            zoom_key = (feeling)

            # Use cached image if available
            if zoom not in self.game.CACHED_ENTITY_ZOOM_IMAGES:
                self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom] = {}
            
            if zoom_key in self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom]:
                scaled_image = self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key]
            
            else:
                sprite = Assets.EXPRESSION_SPRITES[feeling]
                width = sprite.get_width()
                height = sprite.get_height()
                scaled_size = (
                    int(width * zoom),
                    int(height * zoom)
                )
                scaled_image = pygame.transform.scale(sprite, scaled_size)
                self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key] = scaled_image

            win.blit(scaled_image,
                     ((health_bar_rect.x - offset_x - ((i + 1) * 20)) * zoom, (health_bar_rect.y - offset_y) * zoom))

    def draw(self, see_through=False, window=None, cam=(0, 0), zoom=None) -> None:
        zoom = self.game.zoom if not zoom else zoom
        zoom = round(zoom, 2)
        if self.type == 'enemy':
            self.zoom = zoom

        # Use game offset if None is provided
        if not cam:
            offset_x = self.game.offset_x
            offset_y = self.game.offset_y
        else:
            offset_x = cam[0]
            offset_y = cam[1]

        # Display on game window if None is provided
        if not window:
            window = self.game.window

        if not self.dead:
            if self.game.debug.get('path', False): 
                if self.path and self.target:
                    for path in self.blacklist:
                            scaled_rect = pygame.Rect(
                                int((path.rect.x - offset_x) * zoom),
                                int((path.rect.y - offset_y) * zoom),
                                int(path.rect.width * zoom),
                                int(path.rect.height * zoom)
                            )

                            pygame.draw.rect(window, (255, 244, 255), scaled_rect)
                    
                    for path in self.path:
                        scaled_rect = pygame.Rect(
                            int((path.rect.x - offset_x) * zoom),
                            int((path.rect.y - offset_y) * zoom),
                            int(path.rect.width * zoom),
                            int(path.rect.height * zoom)
                        )

                        pygame.draw.rect(window, self.color, scaled_rect)

                if self.type == 'player' and self.target and self.game.env_ready:
                    end = self.get_closest_node(self.target.rect)
                    if end:
                        scaled_rect = pygame.Rect(
                            int((end.rect.x - offset_x) * zoom),
                            int((end.rect.y - offset_y) * zoom),
                            int(end.rect.width * zoom),
                            int(end.rect.height * zoom)
                        )
                        pygame.draw.rect(window, (255, 0, 0), scaled_rect)

        '''
        # Scale player rect
        scaled_rect = pygame.Rect(
            int((self.rect.x - offset_x) * zoom),
            int((self.rect.y - offset_y) * zoom),
            int(self.rect.width * zoom),
            int(self.rect.height * zoom)
        )
        pygame.draw.rect(window, self.color, scaled_rect)'''
        
        if not self.dead and not self.death:
            zoom_key = (
                self.name, self.color, self.sprite_sheet,
                self.sprite_index, self.direction
            )
        else:
            zoom_key = (
                self.sprite_sheet, self.sprite_index,
                self.direction, self.death, self.dead,
            )
            
        # Use cached image if available
        if zoom not in self.game.CACHED_ENTITY_ZOOM_IMAGES:
            self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom] = {}
        
        if zoom_key in self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom]:
            scaled_image = self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key]
        else:
            scaled_size = (
                int(self.sprite.get_width() * zoom),
                int(self.sprite.get_height() * zoom)
            )
            scaled_image = pygame.transform.scale(self.sprite, scaled_size)
            self.game.CACHED_ENTITY_ZOOM_IMAGES[zoom][zoom_key] = scaled_image

        # Position centered on player
        draw_x = int((self.rect.x - offset_x - self.morex) * zoom)
        draw_y = int((self.rect.y - offset_y - self.morey) * zoom)

        if self.dashing:
            if self.x_vel == 0 or self.hit_wall_for > 0.05:
                self.dashing = False
                self.startx = self.rect.x
                self.history = []

            else:
                if abs(self.rect.x - self.startx) > self.rect.width / 2:
                    self.history.append(
                        {
                            "pos": self.rect.topleft,
                            "dir": self.direction,
                            "key": zoom_key,
                            1: self.sheet_name,
                            2: self.sprite_index,
                            3: (self.death or self.dead),
                            'name': self.name,
                            'color': self.color
                        }
                    )
                    self.startx = self.rect.x

                for i, dat in enumerate(self.history[::-1]):
                    if dat[3]:
                        image = Assets.DEAD_SPRITES[dat[1]][dat[2]]
                    else:
                        image = cache_assets((dat['name'], dat['color'], dat[1]), index=dat[2])

                    image = create_cache_img(self.game.CACHED_ENTITY_ZOOM_IMAGES, dat["key"], image, zoom).copy()
                    image.set_alpha(255 - i * 30)
                    
                    drawx = int((dat["pos"][0] - offset_x - self.morex) * zoom)
                    drawy = int((dat["pos"][1] - offset_y - self.morey) * zoom)
                    window.blit(image, (drawx, drawy))

                    if i > 10:
                        self.dashing = False
                        self.startx = self.rect.x
                        self.history = []
                        break
        else:
            self.startx = self.rect.x
            self.history = []

        window.blit(scaled_image, (draw_x, draw_y))

        if not self.dead:
            health_bar_rect = self.draw_health_bar(window, offset_x, offset_y, zoom)
            self.show_thoughts_and_feelings(health_bar_rect, window, offset_x, offset_y, zoom)
    