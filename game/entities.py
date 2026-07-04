import random
import pygame
from .entity_utils import Entity, TargetSystem
from .physics import PHYSICS
from .data.palletes.entities import entity_pallete

# ENEMY CLASS
class Enemy(Entity, PHYSICS):
    COLOR = (255, 0, 0)
    total = -1

    def __init__(self, x, y, width, height, name="Archer", color="Red", game=None, auto=True, id=None, client=None):
        # Attributes
        self.type = 'enemy'
        self.auto = auto
        super().__init__(x, y, width, height, name, color, game)

        self.client = client

        Enemy.total += 1
        self.id = Enemy.total if not id else id
        Entity.total += 1
        self.entity_id = Entity.total if not id else id

        self.personalise()
        # self.game.personalise(self)


# PLAYER CLASS
class Player(Entity, PHYSICS):
    COLOR = (0, 0, 255)
    total = -1

    def __init__(self, x, y, width, height, name="TNT", color="Blue", game=None, auto=False, viewport=None, j=None,
                 id=None, client=None, groups=None):
        # Attributes
        self.type = 'player'
        self.auto = auto
        super().__init__(x, y, width, height, name, color, game, groups)
        
        self.joystick_id = None
        self.key = ["None", 0]
        self.keyboard_num = 1
        self.control_type = None

        self.ready = False
        self.client = client

        Player.total += 1
        self.id = Player.total if not id else id
        Entity.total += 1
        self.entity_id = Entity.total if not id else id

        self.personalise()
        self.health = 500
        self.max_health = self.health
        self.mad = True

        self.shake_frames = 0  # Number of frames to apply shake
        self.shake_intensity = 6

        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_min = 0.5
        self.zoom_max = 2.0

        self.target_system = TargetSystem(self)

        self.player_types = ['TNT', 'Pawn', 'Warrior', 'Torch', 'Archer']
        self.player_colors = list(entity_pallete.keys())
        

    def reassign_joystick(self, new_joystick):
        self.joystick = new_joystick


class Spawn_Point():
    total = -1

    def __init__(self, x, y, width, height, interval=10, limit=10, entities=None, game=None, id=None):

        # Attributes
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.interval = interval
        self.limit = limit
        self.game = game
        self.type = "spawn_point"
        self.entities = [("Pawn", "Red")] if not entities else entities
        Spawn_Point.total += 1
        self.id = Spawn_Point.total if not id else id

        self.health = 1000
        self.history = -10
        self.created = 0
        self.finished = False

    def update(self):
        type_ = random.choice(self.entities)
        name = type_[0]
        color = type_[1]

        if self.game.seconds % self.interval == 0 and self.created < self.limit:
            if self.history != self.game.seconds:
                self.game.enemy_list.append(Enemy(self.x, self.y, 50, 50, name, color, game=self.game))
                self.game._draw_list_dirty = True
                self.game._entities_dirty = True
                
                self.history = self.game.seconds
                self.created += 1

        if self.created >= self.limit:
            self.finished = True
