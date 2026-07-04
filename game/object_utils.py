import pygame
from pygame import Rect
from typing import Tuple, Any
import random

from .assets import Assets
from .settings import Settings
from .physics import PHYSICS
from .functions import get_block, pallete_swap

CACHED_OBJECT_IMAGES = {'other': {}, 'arrows': {}}
CACHED_OBJECT_ZOOMED_IMAGES = {}

class Object(PHYSICS):
    GRAVITY = 1
    total = 0

    def __init__(self, x, y, width, height, name=None, game=None):
        super().__init__()
        self.origin_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = None
        self.mask = None
        self.color = (156, 77, 8)

        # Attributes
        self.name = name
        self.type = name

        # Decisions
        if not self.name == "block":
            self.game = game
            self.direction = "left"
            self.decision = 'left'
            self.choice = 'wl'
            self.jump_choice = 'single'
            self.activities = ['wl', 'wr', 'rl', 'rr', 'il', 'ir', 'c', 'j']

        # Status Values
        if not self.name == "block":
            self.kills = 0
            self.hit_count = 0
            self.fall_count = 0
            self.jump_count = 0
            self.hit_wall_for = 0        
            self.on_ground_for = 0
            self.in_air_for = 0
            
        self.health = 50
        
        if not self.name == "block":
            # Strength
            self.knockback_power = 10
            self.attack_power = 10

            # Times and Timers
            self.timer = 0
            self.time = 0

        # Sprites
        self.sprite_index = 0

        # Speeds
        if not self.name == "block":    
            self.animation_count = 0
            self.x_vel = 0
            self.y_vel = 0
            self.speed = 200
            self.jump_vel = -400
            self.walk_speed = 10
            self.acceleration = 50
            self.current_speed = self.speed
            self.current_gravity = Settings.GRAVITY
            self.current_jump = self.jump_vel
            self.duration = 0

        # Status
        self.dead = False
        self.death = False
        
        if not self.name == "block":
            self.hit_wall = False
            self.on_ground = False
            self.attacking = False
            self.hurt = False
        
            # Somethings
            self.activities = ['on', 'off']
            self.degree = 0
            self.title = 'Whookid'    
            self.sprite_sheet = 'idle'
            self.sheet_name = 'idle_left'
            self.oxygen = 100
            self.max_oxygen = 100
            self.sprites = list()
        
        self.morex = 0
        self.morey = 0

        self.nature = 'object'
        self.knocking_back = 0
        self.type_name = 'rock_1'
        self.type_size = 'big'
        self.size = 50
        self.zoom = 1

        self.max_health = 100
        
        if not self.name == "block":
            self.zone = None
            self.time_accumulator = 0
            self.frame_duration = 0.1
            self.stuck = False
            self.elapsed = 0
            self.swim_strength = 300

            self._last_sheet_key = None
        
        self.in_screen = False
    
    def personalise(self):
        if "platform" in self.name.lower():
            self.activities = ['onwl', 'onwr', 'onrl', 'onrr', 'offil']

    def hit(self, enemy):
        self.health -= enemy.attack_power
        self.animation_count = 0
        self.hurt = True
    
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

        cache_key = (self.name, self.sprite_sheet, self.sheet_name, self.direction, self.type, self.dead, self.death)

        if cache_key not in self.game.object_sprite_cache:
            # Cache miss — walk the Assets dict once and store the result.
            # This branch runs at most once per unique (name, color, sheet_name)
            # combination for the lifetime of the entity.
            try:
                if self.name == "bomb":
                    if self.death or self.dead:
                        sprites = Assets.EXPLOSION_SPRITES[self.sheet_name]
                    else:
                        sprites = Assets.BOMB_SPRITES[self.sheet_name]

                elif self.name == 'arrow' and self.type == 'weapon':
                    sprites = Assets.ARROW_SPRITES[self.sheet_name]            
                
                elif self.type == "fire":
                    sprites = Assets.FIRE_SPRITES[self.sheet_name]
                
                elif self.type == "tree":
                    sprites = Assets.TREE_SPRITES[self.sheet_name]
                
                elif self.type == "treasure":
                    sprites = Assets.GEM_SPRITES[self.sheet_name]

                self.game.object_sprite_cache[cache_key] = sprites
            except KeyError:
                # Sheet doesn't exist — return empty list so caller can handle it
                # gracefully (same behaviour as before, but now explicit).
                 self.game.object_sprite_cache[cache_key] = []

        return self.game.object_sprite_cache[cache_key]

    def update(self):
        if not self.name == "block":
            image = self.image
        else:
            image = get_block(self.type_name, self.type_size, self.width, self.height)

        if self.name == 'water':
            image_key = (self.name, self.water_type, self.color, (self.rect.width, self.rect.height),
                            self.sprite_sheet, self.sheet_name, self.sprite_index, self.direction)  
                        
        elif self.name == 'platform':
            image_key = (self.name, self.sprite_sheet, self.sheet_name, self.sprite_index)
        
        elif self.type == "block":
            image_key = (self.name, self.type_name, self.type_size, self.sprite_index)

        elif self.name == 'arrow' and self.type == 'weapon':
            image_key = (self.sprite_sheet, self.sheet_name, self.sprite_index,
                        int(self.degree))
            
        else:
            image_key = (self.name, self.sprite_sheet, self.sheet_name, self.sprite_index, self.direction)

        # Use cached image if available
        if self.name == 'arrow' and self.type == 'weapon':
            if 'arrows' not in CACHED_OBJECT_IMAGES:
                CACHED_OBJECT_IMAGES['arrows'] = {}

            if image_key in CACHED_OBJECT_IMAGES['arrows']:
                image, self.mask, rect = CACHED_OBJECT_IMAGES['arrows'][image_key]
        else:
            if 'other' not in CACHED_OBJECT_IMAGES:
                CACHED_OBJECT_IMAGES['other'] = {}
                
            if image_key in CACHED_OBJECT_IMAGES['other']:
                image, self.mask, rect = CACHED_OBJECT_IMAGES['other'][image_key]
        
        from_x = 0
        from_y = 0
        photo_width = 64
        photo_height = 64

        n = 0
        n2 = 0
        y = 0

        if self.type == 'deco':
            if self.name == 'scare_crow':
                from_x = 50
                photo_width = 192
                from_y = 50
                photo_height = 192
                n = -20

            elif self.name == 'grass1':
                from_x = 20
                photo_width = 64
                from_y = 20
                photo_height = 64

            elif self.name == 'grass2':
                from_x = 20
                photo_width = 70
                from_y = 16
                photo_height = 64

            elif self.name == 'shrub1':
                from_x = 12
                photo_width = 64
                from_y = 25
                photo_height = 64

            elif self.name == 'shrub2':
                from_x = 17
                photo_width = 64
                from_y = 18
                photo_height = 64

            elif self.name == 'shrub3':
                from_x = 5
                photo_width = 64
                from_y = 15
                photo_height = 64

            elif self.name == 'shroom1':
                from_x = 20
                photo_width = 64
                from_y = 24
                photo_height = 64

            elif self.name == 'shroom2':
                from_x = 17
                photo_width = 64
                from_y = 22
                photo_height = 64

            elif self.name == 'shroom3':
                from_x = 12
                photo_width = 64
                from_y = 18
                photo_height = 64

            elif self.name == 'pumpkin1':
                from_x = 10
                photo_width = 64
                from_y = 18
                photo_height = 64

            elif self.name == 'pumpkin2':
                from_x = 12
                photo_width = 64
                from_y = 20
                photo_height = 64

            elif self.name == 'bone':
                from_x = 21
                photo_width = 64
                from_y = 22
                photo_height = 64

            elif self.name == 'exit':
                from_x = 25
                photo_width = 64
                from_y = 30
                photo_height = 128

            elif self.name == 'arrow':
                from_x = 5
                photo_width = 64
                from_y = 30
                photo_height = 128

        elif self.name == 'fire':

            from_x = 25
            from_y = 20
            photo_width = 128
            photo_height = 128

        elif self.name == 'tree':

            from_x = 80
            from_y = 80
            photo_width = 192
            photo_height = 192

            n = -55

        elif self.name == 'bomb':
            from_x = 20 if not self.death else 0
            from_y = 12 if not self.death else 0
            photo_width = 64 if not self.death else 1
            photo_height = 64 if not self.death else 1
            if self.death:
                n = -90
                n2 = -90

        elif self.name == 'arrow' and self.type == 'weapon':
            from_x = 0
            from_y = 28
            photo_width = 64
            photo_height = 64

            n = 28
            y = 5
        
        margin_distance_x = from_x * 2
        width_distance = photo_width - margin_distance_x

        margin_distance_y = from_y * 2 - y
        height_distance = photo_height - margin_distance_y

        trimarea = (from_x, from_y, width_distance, height_distance)

        self.morex = from_x - n2
        self.morey = from_y - n

        if (self.type not in ['block', 'treasure', 'moving_platform']) and (self.name not in ['water', 'platform']):
            if self.name == 'arrow' and self.type == 'weapon':
                if image_key not in CACHED_OBJECT_IMAGES['arrows']:
                    image = image.subsurface(trimarea)
            
            else:
                if image_key not in CACHED_OBJECT_IMAGES['other']:
                    image = image.subsurface(trimarea)
            
        if self.name == 'arrow' and self.type == 'weapon':
            if image_key not in CACHED_OBJECT_IMAGES['arrows']:
                original_rect = self.rect.copy()
                image = pygame.transform.rotate(image, self.degree)
                
                image_ = pallete_swap(image, (22, 28, 46), (0, 0, 0))
                image_ = pallete_swap(image_, (151, 123, 107), (0, 0, 0))
                image_ = pallete_swap(image_, (239, 225, 171), (0, 0, 0))
                image_ = pallete_swap(image_, (213, 181, 131), (0, 0, 0))
                image_.set_colorkey((0, 0, 0, 0))

                self.mask = pygame.mask.from_surface(image_)
                self.rect = self.mask.get_rect()
                self.rect.center = original_rect.center

            else:
                self.rect = pygame.Rect(self.rect.x, self.rect.y, rect.width, rect.height)
            
            self.image = image        

        else:
            if image_key not in CACHED_OBJECT_IMAGES['other']:
                self.rect = image.get_rect(topleft=self.rect.topleft)
            else:
                self.rect = pygame.Rect(self.rect.x, self.rect.y, rect.width, rect.height)

        if self.name == 'arrow' and self.type == 'weapon':
            if image_key not in CACHED_OBJECT_IMAGES['arrows']:
                CACHED_OBJECT_IMAGES['arrows'][image_key] = image, self.mask, self.rect

        else:
            if image_key not in CACHED_OBJECT_IMAGES['other']:
                self.mask = pygame.mask.from_surface(image)
                CACHED_OBJECT_IMAGES['other'][image_key] = image, self.mask, self.rect

        
    def update_health_bar(self) -> tuple[int, Any]:
        bar = int(self.health)

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
            bar = 100

        return bar, color

    def draw_health_bar(self, win, offset_x, offset_y, zoom=None) -> Rect:

        bar, color = self.update_health_bar()
        bar = 20
        health_bar_rect = pygame.Rect(self.rect.centerx - (bar / 2), self.rect.y - 20, bar, 10)

        pygame.draw.rect(win, color, (
            (health_bar_rect.x - offset_x) * zoom, (health_bar_rect.y - offset_y) * zoom,
            health_bar_rect.width * zoom,
            health_bar_rect.height * zoom), border_radius=20)

        text = Settings.health_font.render(f"Health {self.degree}", True, color)
        
        width = text.get_width()
        height = text.get_height()
        win.blit(pygame.transform.scale(text, (width * zoom, height * zoom)),
                 ((self.rect.centerx - (bar / 2) - offset_x + bar + 5) * zoom, (self.rect.y - 20 - offset_y) * zoom))
        
        return health_bar_rect

    def draw(self, see_through=False, window=None, cam=(0, 0), zoom=1, game=None) -> None:
        if self.type == "block":
            game = game
        else:
            game = self.game

        zoom = round(zoom, 2)
        self.zoom = zoom

        # Use game offset if None is provided
        if cam:
            offset_x = cam[0]
            offset_y = cam[1]

        # Bubbles
        if self.name == 'bubble':
            pygame.draw.circle(window, self.color, (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
                               self.radius * zoom)
            return

        # Platforms
        elif self.name == 'platform':
            scaled_rect = pygame.Rect(
                int((self.rect.x - offset_x) * zoom),
                int((self.rect.y - offset_y) * zoom),
                int(self.rect.width * zoom),
                int(self.rect.height * zoom)
            )
            pygame.draw.rect(window, self.color, scaled_rect)
            # Add support lines to platforms
            for i in range(3):
                pygame.draw.line(window, (100, 80, 60),
                                 (int((self.rect.x + i * (self.rect.width // 2) - offset_x) * zoom),
                                  int((self.rect.y + self.rect.height - offset_y) * zoom)),
                                 (int((self.rect.x + i * (self.rect.width // 2) - offset_x) * zoom),
                                  int((self.rect.y + self.rect.height + 10 - offset_y) * zoom)),
                                 int(2 * zoom))
            return

        # Key for checking cache
        if self.name == 'water':
            key = (self.name, self.water_type, self.color, (self.rect.width, self.rect.height),
                   self.sprite_sheet, self.sheet_name, self.sprite_index, self.direction,
                   see_through)  # Round to avoid excessive keys
        
        elif self.type == 'bomb':
            key = (self.name, self.sprite_sheet,
                   self.sheet_name, self.sprite_index, self.direction, 
                   self.dead, self.death)

        elif self.type == 'block':
            key = (self.name, (self.rect.width, self.rect.height),
                   self.type_size, self.type_name, self.sprite_index, self.perspective)  # Round to avoid excessive keys

        elif self.name == 'arrow' and self.type == 'weapon':
            key = (
                self.sprite_sheet, self.sheet_name, self.sprite_index, self.direction,
                int(self.degree)
            ) #, self.dead, self.death)  # Round to avoid excessive keys

        else:
            key = (self.name, self.type_name, self.type_size,
                   self.sprite_sheet, self.sheet_name, self.sprite_index, self.direction,
                   see_through, self.dead, self.death)  # Round to avoid excessive keys

        if self.type == "block":
            image = get_block(self.type_name, self.type_size, self.width, self.height, self.perspective)
        else:
            image = self.image
            if not image:
                print(self.name)
        
        if zoom not in CACHED_OBJECT_ZOOMED_IMAGES:
            CACHED_OBJECT_ZOOMED_IMAGES[zoom] = {}
        
        # Use cached image if available
        if key in CACHED_OBJECT_ZOOMED_IMAGES[zoom]:
            scaled_image = CACHED_OBJECT_ZOOMED_IMAGES[zoom][key]
        else:
            scaled_size = (
                int(image.get_width() * zoom),
                int(image.get_height() * zoom)
            )
            scaled_image = pygame.transform.scale(image, scaled_size)

            if self.name != "water":
                if see_through:
                    scaled_image.set_alpha(100)

            CACHED_OBJECT_ZOOMED_IMAGES[zoom][key] = scaled_image

        # Position centered on player
        draw_x = int((self.rect.x - offset_x - self.morex) * zoom)
        draw_y = int((self.rect.y - offset_y - self.morey) * zoom)

        window.blit(scaled_image, (draw_x, draw_y))
        
        if game:
            if game.debug.get('0', False):
                health_bar_rect = self.draw_health_bar(window, offset_x, offset_y, zoom)
                draw_x_ = int((self.rect.x - offset_x) * zoom)
                draw_y_ = int((self.rect.y - offset_y) * zoom)

                scaled_rect = pygame.Rect(
                    draw_x_,
                    draw_y_,
                    int(self.rect.width * zoom),
                    int(self.rect.height * zoom)
                )
                pygame.draw.rect(window, self.color, scaled_rect)
                
                if self.mask:
                    image = self.mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255))
                else:
                    image = self.image

                scaled_size = (
                    int(image.get_width() * zoom),
                    int(image.get_height() * zoom)
                )
                scaled_image = pygame.transform.scale(image, scaled_size)

                window.blit(scaled_image, (draw_x_, draw_y_))
