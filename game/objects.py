import pygame
import random
import math
import time

from .object_utils import Object
from .functions import get_block, playit, cache_img
from .assets import Assets
from .settings import Settings
from .physics import get_degree, PHYSICS as physics

class Platform(Object):
    total = -1

    def __init__(self, x, y, width, height, moving, direction, speed, dest_x, dest_y, game):
        super().__init__(x, y, width, height, "platform", game=game)
        Platform.total += 1
        self.id = Platform.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "moving_platform"
        self.moving = moving
        self.direction = direction
        self.min_x = dest_x[0]
        self.max_x = dest_x[1]
        self.min_y = dest_y[0]
        self.max_y = dest_y[1]
        self.color = (150, 120, 80)
        self.speed = speed

        surf = cache_img(self.rect.size)
        surf.fill(self.color)
        self.image = surf

    def attack(self):
        pass

    def destroy(self):
        pass

    def update_sprite(self):
        if self.moving:
            self.x_vel = int((self.speed * self.direction[0]) * self.game.dt)
            self.y_vel = int((self.speed * self.direction[1]) * self.game.dt)

            if self.rect.x + self.x_vel > self.max_x:
                self.direction[0] = -1
                self.x_vel = 0

            elif self.rect.x + self.x_vel < self.min_x:
                self.direction[0] = 1
                self.x_vel = 0

            elif not abs(self.min_x-self.max_x) > 64:
                self.x_vel = 0

            else:
                self.rect.x += self.x_vel

            if self.rect.y + self.y_vel > self.max_y:
                self.direction[1] = -1
                self.y_vel = 0

            elif self.rect.y + self.y_vel < self.min_y:
                self.y_vel = 0
                self.direction[1] = 1

            elif not abs(self.min_y - self.max_y) > 64:
                self.y_vel = 0

            else:
                self.rect.y += self.y_vel

        else:
            print(99999999)
    
        self.update()


# === Flow effect function ===
def apply_current(x_velocity, current_strength, current_direction, time,
                  max_velocity=3.0, turbulence=0.1, oscillation_freq=0.5, oscillation_amp=0.3):
    flow = current_strength * current_direction
    wave = math.sin(time * oscillation_freq * 2 * math.pi) * oscillation_amp
    jitter = random.uniform(-turbulence, turbulence)
    total_flow = flow + wave + jitter
    resistance = 1 - abs(x_velocity * current_direction)
    adjusted_velocity = x_velocity + total_flow * resistance
    return max(-max_velocity, min(max_velocity, adjusted_velocity))


class Bubble(Object):
    def __init__(self, x, y, color=(200, 200, 255), game=None):
        super().__init__(x, y, 10, 10, "bubble", game=game)
        self.x = x
        self.y = y
        self.y_vel = -random.uniform(30, 90)
        self.radius = random.randint(2, 4)
        self.spawn_time = time.time()
        self.color = color

    def update_sprite(self):
        self.y += self.y_vel * self.game.dt
        if not time.time() - self.spawn_time < 3.0:
            self.dead = True
            self.death = True


class Splash(Object):
    def __init__(self, x, y, color=(180, 220, 255, 180), game=None):
        super().__init__(x, y, 10, 10, "splash", game=game)
        self.x = x
        self.y = y
        self.spawn_time = time.time()
        self.size = random.randint(2, 5)
        self.image = cache_img((self.size * 2, self.size * 2))
        self.color = color
        alpha = int(255 * ((time.time() - self.spawn_time) / 0.5))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)

    def update_sprite(self):
        if not time.time() - self.spawn_time < 0.5:
            self.dead = True
            self.death = True
        else:
            self.rect.x += self.vx
            self.rect.y += self.vy
            self.vy += 0.1  # Gravity
            alpha = int(255 * ((time.time() - self.spawn_time) / 0.5))
            color = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(self.image, color, (self.size, self.size), self.size)


# === Water Zones ===
class WaterZone(Object):
    def __init__(self, x, y, w, h, type="normal", game=None, color=(0, 100, 255), flow=0, rise=False):
        super().__init__(x, y, w, h, "water", game=game)
        self.rect = pygame.Rect(x, y, w, h)
        self.water_type = type
        self.color = color
        self.flow = flow
        self.rise = rise
        self.base_y = y
        self.wave_offset = 0
        self.mass = 0.5
        surf = cache_img(self.rect.size, self.color)
        surf.fill(self.color)
        surf.set_alpha(120)
        self.image = surf

    def update_sprite(self):
        if self.rise:
            self.wave_offset += self.game.dt * 5
            self.y_vel += int(20 * math.sin(self.wave_offset))

        if self.in_screen:
            if self.water_type == "toxic":
                if random.random() < 0.05:
                    self.game.bubbles.append(
                        Bubble(random.randint(self.rect.x, self.rect.right), self.rect.top, color=(50, 150, 50),
                            game=self.game))
                    self.game._draw_list_dirty = True

            elif self.water_type == "lava":
                if random.random() < 0.05:
                    self.game.bubbles.append(
                        Bubble(random.randint(self.rect.x, self.rect.right), self.rect.top, color=(255, 100, 0),
                            game=self.game))
                    self.game._draw_list_dirty = True

        self.update()

    def affect(self, player):
        ztype = self.water_type
        player.current_speed *= 0.5 if player.name not in ["arrow", "bomb"] else 1
        if ztype == "normal":
            player.current_gravity *= 0.05
            player.current_jump *= 0.1
            player.oxygen -= 30 * self.game.dt

        elif ztype == "current":
            if not player.name == "arrow":
                player.x_vel += apply_current(player.x_vel - (self.flow * 100), 0.6, self.flow, self.game.dt,
                                              max_velocity=player.current_speed, turbulence=0.2, oscillation_freq=0.5,
                                              oscillation_amp=0.7)
            player.current_gravity *= 0.05
            player.current_jump *= 0.1

            player.oxygen -= 30 * self.game.dt

        elif ztype == "toxic":
            player.current_gravity *= 0.05
            player.current_jump *= 0.1
            player.health -= 2.5 * self.game.dt
            player.oxygen -= 30 * self.game.dt

        elif ztype == "healing":
            player.current_gravity *= 0.05
            player.current_jump *= 0.1
            player.health += 30 * self.game.dt
            player.health = min(player.max_health, player.health)

        elif ztype == "lava":
            player.current_gravity *= 0.05
            player.current_jump *= 0.1
            player.health -= 5 * self.game.dt


# BOMBS CLASS

class Bombs:
    COLOR = (255, 0, 0)
    GRAVITY = 1
    ANIMATION_DELAY = 3
    total = -1

    def __init__(self, bomb=None, game=None):
        self.list = list()
        self.game = game

    def handle_proccesses(self):
        self.total = len(self.list)
        for bomb in self.list:
            objects = list(
                filter(lambda target: abs(target.rect.x - bomb.rect.x) < 400 and abs(target.rect.y - bomb.rect.y) < 400,
                       [*self.game.all_entities, *self.game.damageable_objects]))

            bomb.attack(objects)

    def update_sprites(self):
        """"""

    def draw(self):
        for bomb in self.list:
            if (bomb.rect.left - self.game.offset_x > self.game.WIDTH or bomb.rect.x + 64 - self.game.offset_x < 0) or (
                    bomb.rect.y - self.game.offset_y > self.game.HEIGHT + 64 * 2 or bomb.rect.bottom - self.game.offset_y < 0):
                continue

            bomb.draw(game=self.game)

# BOMB CLASS
class Bomb(Object, Bombs):
    total = -1

    def __init__(self, x, y, owner, sounds, bomb_lifespan=6):
        super().__init__(x, y, 10, 10, "bomb", game=owner.game)
        self.owner = owner
        self.targets = None
        self.attack_power = 5
        self.knockback_power = 300
        self.timer = 10
        Bombs.total += 1
        self.id = Bombs.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "weapon"
        self.sounds = sounds
        self.game = owner.game
        if self.owner.type == 'player':
            self.attack_power = 21
        else:
            self.attack_power = 9

        self.lifespan = bomb_lifespan
        self.mass = 0.5

    def attack(self, targets):
        if self.death or self.dead:
            return

        self.targets = targets
        for target in targets:
            # For team purposes - The bomb won't hit a team member
            if target.color == self.owner.color:
                continue
            
            if not target.dead:
                if target.nature == 'entity':
                    if target.entity_id == self.owner.entity_id:
                        continue
                elif target.nature != 'damageable_object':
                    continue

                if self.mask_collided(target):
                    self.target = target

                    self.attacking = False
                    self.destroy()

                    if target.nature == 'damageable_object':
                        target.hit(self.owner)
                    else:
                        if self.target.type == "player":
                            self.target.shake_frames = 8  # Apply shake for next few frames
                            self.target.shake_intensity = 6

                        target.hit(self.owner, 'bomb')

                        physics.knockback(self, target=target)
                        
                        # To reset to a distance where he can get a shot
                        self.owner.clear_shot_range = 0
                        self.owner.clear_shot_up = 0
                        self.owner.clear_shot_down = 0
                        self.owner.missed = 0

                    playit("hit_3", self)
                    break

                else:
                    self.attacking = True

    def destroy(self):
        playit('explosion_3', self)
        self.sprite_index = 0
        self.animation_count = 0
        self.death = True

    def update_sprite(self):
        if not self.death:
            self.current_speed = self.x_vel
            self.current_gravity = Settings.GRAVITY

            if self.zone:
                self.zone.affect(self)

            self.y_vel += (self.current_gravity * self.mass) * self.game.dt

            self.x_vel = self.current_speed

            self.collide()
                    
            self.elapsed += self.game.dt

            if self.rect.y > 2000:
                self.destroy()


        self.sheet_name = "on_" + self.direction

        # Check bomb lifespan
        if self.elapsed >= self.lifespan:
            if not self.death:
                self.destroy()
                self.owner.missed += 1
        
        if f"{self.sheet_name}_{self.dead}_{self.death}" != self._last_sheet_key:
            self.sprites         = self._resolve_sprites(self.sheet_name)
            self._last_sheet_key = f"{self.sheet_name}_{self.dead}_{self.death}"
        
        if self.sprite_index == len(self.sprites) - 1 and self.death:
            self.dead = True

        self.time_accumulator += self.game.dt
        if (self.in_screen or self.death) and self.time_accumulator >= self.frame_duration:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)

            self.time_accumulator = 0
            self.animation_count += 1

        if self.animation_count == 0 and self.sprite_index != 0:
            self.sprite_index = 0
            self.time_accumulator = 0

        self.image = self.sprites[self.sprite_index]

        self.update()


# ARROW CLASS

class Arrow(Object, Bombs):
    total = -1

    def __init__(self, x, y, owner, sounds):
        super().__init__(x, y, 10, 10, "arrow", game=owner.game)
        self.owner = owner
        self.targets = None
        self.attack_power = 5
        self.knockback_power = 300
        self.timer = 10
        Arrow.total += 1
        self.id = Arrow.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "weapon"
        self.sounds = sounds
        self.game = owner.game
        self.degree = random.randint(-360, 360)
        self.sprites = Assets.ARROW_SPRITES
        self.stuck = False
        self.sheet_name = 'full'

        if self.owner.type == 'player':
            self.attack_power = 18
        else:
            self.attack_power = 6

        self.mass = 0.25

        self.lifespan = 2
        self.image = Assets.ARROW_SPRITES[self.sheet_name][self.sprite_index]

    def attack(self, targets):
        if self.death or self.dead:
            return

        self.targets = targets
        for target in targets:
            if target.color == self.owner.color:
                    continue

            if not target.dead:
                if target.nature == 'entity':
                    if target.entity_id == self.owner.entity_id:
                        continue
                elif target.nature != 'damageable_object':
                    continue

                if self.mask_collided(target):
                    self.target = target

                    self.attacking = False
                    self.destroy()

                    if target.nature == 'damageable_object':
                        target.hit(self.owner)
                    else:
                        if self.target.type == "player":
                            self.target.shake_frames = 8  # Apply shake for next few frames
                            self.target.shake_intensity = 6

                        target.hit(self.owner, 'arrow')
                        
                        physics.knockback(self, target=target)

                        # To reset to a distance where he can get a shot
                        self.owner.clear_shot_range = 0
                        self.owner.clear_shot_up = 0
                        self.owner.clear_shot_down = 0
                        self.owner.missed = 0

                    playit("hit_3", self)

                else:
                    self.attacking = False
                    
    def destroy(self):
        self.stick()
        self.dead = True

    def stick(self, obj=None):
        if not self.death or self.dead:
            if self.owner.type == 'enemy':
                self.owner.missed += 1
        self.death = True
        self.stuck = True
        self.y_vel = 0
        self.x_vel = 0

    def update_sprite(self):
        self.current_speed = self.x_vel
        self.current_gravity = Settings.GRAVITY

        if self.zone:
            self.zone.affect(self)

        self.y_vel += (self.current_gravity * self.mass) * self.game.dt

        self.x_vel = self.current_speed
        
        self.collide(True)
        
        if self.stuck:
            self.elapsed += self.game.dt

            # Check arrow lifespan
            if self.elapsed >= self.lifespan:
                self.destroy()

        if self.rect.y > 2000:
            self.destroy()
        
        if self.sheet_name != self._last_sheet_key:
            self.sprites         = self._resolve_sprites(self.sheet_name)
            self._last_sheet_key = self.sheet_name
        
        self.time_accumulator += self.game.dt
        if self.time_accumulator >= self.frame_duration:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.time_accumulator = 0
            self.animation_count += 1

        if self.animation_count == 0 and self.sprite_index != 0:
            self.sprite_index = 0
            self.time_accumulator = 0

        self.image = self.sprites[self.sprite_index]

        self.update()


# FIRE CLASS
class Fire(Object):
    total = -1
    ANIMATION_DELAY = 2

    def __init__(self, x, y, owner, fire_lifespan=6):
        super().__init__(x, y, 50, 50, "fire", owner.game)
        self.rect.bottomleft = (x, y)
        self.rect.centerx = x
        Fire.total += 1
        self.id = Fire.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "fire"
        self.game = owner.game
        self.nature = 'weapon'
        self.owner = owner
        self.game = owner.game
        self.lifespan = fire_lifespan
        self.burning = False
        self.mass = 0.5

    def attack(self):
        self.targets = list(
            filter(lambda goal: abs(goal.rect.x - self.rect.x) < 400 and abs(goal.rect.y - self.rect.y) < 400,
                   [*self.game.all_entities, *self.game.damageable_objects]))

        for target in self.targets:
            if target.color == self.owner.color:
                    continue
            
            self.target = target
            
            if target.nature == 'entity':
                if target.entity_id == self.owner.entity_id:
                    continue
            elif target.nature != 'damageable_object':
                    continue

            if not target.dead:
                if self.rect.colliderect(target):

                    self.attacking = False
                    # Check fire lifespan
                    if self.elapsed < self.lifespan:
                        # Apply damage at each burn interval
                        self.attack_power = self.game.dt * 3
                        if target.nature == 'damageable_object':
                            target.hit(self.owner)
                        else:
                            if self.target.type == "player":
                                self.target.shake_frames = max(self.target.shake_frames,
                                                               8)  # Apply shake for next few frames
                                self.target.shake_intensity = max(self.target.shake_intensity, 6)

                            target.hit(self.owner, obj=self, type_='fire')
                        self.burning = True
                        target.burning = True

                else:
                    self.attacking = False

    def destroy(self):
        self.sprite_index = 0
        self.animation_count = 0
        self.death = True

    def update_sprite(self):
        self.elapsed += self.game.dt

        if self.zone:
            self.dead = True
            self.death = True

        # Check fire lifespan
        if self.elapsed >= self.lifespan:
            self.dead = True
            self.death = True

        self.sheet_name = "on"
        if self.sheet_name != self._last_sheet_key:
            self.sprites         = self._resolve_sprites(self.sheet_name)
            self._last_sheet_key = self.sheet_name

        self.time_accumulator += self.game.dt
        if self.in_screen and self.time_accumulator >= self.frame_duration:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.time_accumulator = 0
            self.animation_count += 1

        if self.animation_count == 0 and self.sprite_index != 0:
            self.sprite_index = 0
            self.time_accumulator = 0

        self.image = self.sprites[self.sprite_index]

        self.update()
        self.attack()


# TREE CLASS
class Tree(Object):
    total = -1
    ANIMATION_DELAY = 2

    def __init__(self, x, y, game):
        super().__init__(x, y, 50, 50, "tree", game=game)
        Tree.total += 1
        self.id = Tree.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "tree"
        self.game = game
        self.nature = 'damageable_object'
        self.mass = 1

    def destroy(self):
        self.sprite_index = 0
        self.animation_count = 0
        self.death = True

    def update_sprite(self):
        self.y_vel += min(1, (self.fall_count / Settings.FPS) * self.GRAVITY)

        if self.y_vel < 0:
            self.y_vel = 0

        self.y_vel += (Settings.GRAVITY * self.mass) * self.game.dt
        self.x_vel = 0

        self.collide()

        if self.rect.y > self.game.maxy:
            # self.health = 0
            # self.death = True
            if self.type == "enemy":
                self.rect.x = 0
            self.rect.y = -200

        if self.health <= 0:
            self.health = 0
            if not self.death:
                self.death = True
                self.destroy()

        self.sheet_name = "idle_" + self.direction

        if self.hurt:
            self.sheet_name = "hit_" + self.direction
        
        if self.death:
            self.sheet_name = "chopped_" + self.direction

        if self.sheet_name != self._last_sheet_key:
            self.sprites         = self._resolve_sprites(self.sheet_name)
            self._last_sheet_key = self.sheet_name
        
        if self.hurt:
            if self.sprite_index == len(self.sprites) - 1:
                self.hurt = False

        self.time_accumulator += self.game.dt
        if self.time_accumulator >= self.frame_duration:
            if self.in_screen and not self.hurt and not self.death:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            elif self.hurt:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.time_accumulator = 0
            self.animation_count += 1

        if self.animation_count == 0 and self.sprite_index != 0:
            self.sprite_index = 0
            self.time_accumulator = 0

        self.image = self.sprites[self.sprite_index]
        self.animation_count += 1

        self.update()


# BLOCK CLASS
class Block(Object):
    COLOR = (0, 255, 0)
    GRAVITY = 1
    ANIMATION_DELAY = 3
    total = -1

    def __init__(self, x, y, width, height, type="rock_1", type_size="big", game=None, perspective="fore"):
        super().__init__(x, y, width, height, game=game, name='block')
        self.image = get_block(type, type_size, width, height)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.image = None
        self.perspective = perspective
        self.type = 'block'
        self.type_name = type
        self.type_size = type_size
        self.size = self.rect.width
        Block.total += 1
        self.id = Block.total
        Object.total += 1
        self.object_id = Object.total
        self.mass = 1

    def update_sprite(self):
        if self.dead:
            self.y_vel += min(1, (self.fall_count / Settings.FPS) * self.GRAVITY)
            self.move(self.x_vel, self.y_vel, self.game.objects)

        self.update()


# TRAP CLASS
class Trap(Object):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    ANIMATION_DELAY = 3
    total = -1

    def __init__(self, x, y, width, height, name):
        super().__init__(x, y, width, height, name)
        self.type = 'trap'
        # Trap.total += 1
        self.trap = Assets.TRAPS[name]
        self.image = self.trap["on"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
        self.personalise()
        Trap.total += 1
        self.id = Trap.total
        Object.total += 1
        self.object_id = Object.total
        self.jump_vel = 0

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def update_sprite(self, objects):
        # self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel, objects)

        # self.fall_count += 1
        sprites = self.trap[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        self.update()

    def attack(self, objects):
        if not self.rect2.under(self.target.rect2) and not self.rect2.ontop(self.target.rect2):
            if abs(self.rect2.cxdistance(self.target.rect2)) <= self.attack_range:
                if self.rect2.centerx < self.target.rect2.centerx:
                    self.direction = "left"
                    self.target.health -= self.attack_power

                elif self.rect2.centerx > self.target.rect2.centerx:
                    self.direction = "right"
                    self.target.health -= self.attack_power

                else:
                    self.attacking = False
            else:
                self.attacking = False

    def manage(self, targets, objects):
        for target in targets:
            self.target = target
            self.attack(objects)

        if "platform" in self.name.lower():
            self.patrol()

        if not self.patrolling:
            self.wander()

        self.handle_physical_processes(objects)


# DECO CLASS
class Deco(Object):
    total = -1
    ANIMATION_DELAY = 3

    def __init__(self, x, y, name, game):
        super().__init__(x, y, 50, 50, name, game=game)
        Deco.total += 1
        self.id = Deco.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "deco"
        self.game = game
        self.nature = 'damageable_object'
        self.mass = 0.5
        self.sprites = Assets.DECO_SPRITES
        self.image = self.sprites[self.name]

    def destroy(self):
        self.sprite_index = 0
        self.animation_count = 0
        self.death = True

    def update_sprite(self):
        self.y_vel += (Settings.GRAVITY * self.mass) * self.game.dt
        if self.y_vel < 0:
            self.y_vel = 0

        self.x_vel = 0

        self.collide()

        if self.rect.y > 2000:
            self.destroy()
            self.dead = True

        if self.health <= 0:
            self.health = 0
            self.death = True
            self.dead = True

        if self.hurt:
            self.hurt = False

        self.update()


# TREASURE CLASS

class Treasure(Object):
    total = -1
    ANIMATION_DELAY = 3

    def __init__(self, x, y, name, game, coin_type='static'):
        super().__init__(x, y, 50, 50, name, game=game)
        Treasure.total += 1
        self.id = Treasure.total
        Object.total += 1
        self.object_id = Object.total
        self.type = "treasure"
        self.game = game
        self.nature = 'object'
        self.mass = 0.25
        self.coin_type = coin_type
        if coin_type == 'dropped':
            self.y_vel = -200
            self.x_vel = random.randint(-320, 320)

    def update_sprite(self):
        if self.coin_type == 'dropped':
            self.y_vel += (Settings.GRAVITY * self.mass) * self.game.dt
            self.x_vel = min(-16, self.x_vel + 5) if self.x_vel < 0 else max(16, self.x_vel - 5)

            self.collide()

            if self.rect.y > self.game.maxy:
                # self.health = 0
                # self.death = True
                if self.type == "enemy":
                    self.rect.x = 0
                self.rect.y = self.game.miny

        self.sheet_name = self.name
        if self.sheet_name != self._last_sheet_key:
            self.sprites         = self._resolve_sprites(self.sheet_name)
            self._last_sheet_key = self.sheet_name

        self.time_accumulator += self.game.dt
        if self.in_screen and self.time_accumulator >= self.frame_duration:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.time_accumulator = 0
            self.animation_count += 1

        if self.animation_count == 0 and self.sprite_index != 0:
            self.sprite_index = 0
            self.time_accumulator = 0

        self.image = self.sprites[self.sprite_index]
        self.animation_count += 1

        for player in self.game.players:
            if self.rect.colliderect(player.rect):
                if self.name == 'green':
                    player.emerald_coins += 1
                elif self.name == 'pink':
                    player.pearl_coins += 1
                elif self.name == 'red':
                    player.ruby_coins += 1
                elif self.name == 'yellow':
                    player.gold_coins += 1
                self.dead = True
                self.death = True

        self.update()
