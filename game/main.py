import pygame
import json
import threading
import time
import sys
import math
from os import chdir
import itertools

from .settings import Settings
from .assets import Assets
from .data import text
from .windows import Windows
from . import player_helper as p_s
from .entities import Player, Enemy, Spawn_Point
from .entity_utils import PlatformNode
from .physics import get_degree, PHYSICS as physics
from .functions import (
    RPGMenu, Volume, Volumes, UIButton, Sounds,
    get_block, get_text_width, calculate_viewports,
    cache_img, map_chunks, remove_duplicates
)
from .objects import Arrow, Bomb, Bombs, Tree, Block, Deco, WaterZone, Platform, Treasure
from .calculate_class import get_total_size
from .data.palletes.blocks import block_pallete
from .data.palletes.entities import entity_pallete
from .spatial_grid import SpatialGrid

if getattr(sys, 'frozen', False):
    chdir(sys._MEIPASS)

'''
TARGET:
    LEVEL 10
    FUCTIONAL LOOK
    FUCTIONAL LOGIC & FLOW
    FUCTIONAL AI
    STORY
    GOOD UI & UX
'''
# 0, 2, 24, 19, 4, 6, 12, 14, 15, 17, 20, 21, 22, 23
# GAME CLASS

class Game(Settings, Windows):

    def __init__(self, level):
        self.initialise_constants()

        self.volumes = Volumes([Volume(y=200 * i, sound="Background" if i == 0 else 'In Game') for i in range(2)], self)
        self.cached_objects = {}
        self.players = []
        self.player_slots = []
        self.saved_players = {}
        self.nodes = []
        self.sprites = pygame.sprite.Group()

        self.controllers = []
        self.controller_selection = True
        
        self.player = Player(0, 0, 50, 50, 'Archer', 'Purple', game=self)
        self.player.control_type = 'keyboard'
        self.player.keyboard_num = 0
        self.saved_players[self.player.id] = self.player
        self.player_slots.append(self.player)

        if False:
            self.controller_selection = False
            self.controllers.append(["keyboard", 0])
            self.players.append(self.player)
            for i, player in enumerate(self.players):
                    viewport = calculate_viewports(self, len(self.players))[i]
                    player.viewport = pygame.Rect(*viewport)

        # ADD PLAYER AUTOMATICALLY... IF ITS RUNNING ON ANDROID
        if sys.platform == "linux":
            key = ["touch", 0]
            self.controller_selection = False
            self.controllers.append(key)
            self.player.control_type = key[0]
            self.players.append(self.player)
            
            for i, player in enumerate(self.players):
                viewport = calculate_viewports(self, len(self.players))[i]
                player.viewport = pygame.Rect(*viewport)
        
        player2 = Player(0, 0, 50, 50, 'Archer', 'Red', game=self)
        player2.control_type = 'keyboard'
        player2.keyboard_num = 1
        self.saved_players[player2.id] = player2
        self.player_slots.append(player2)

        player3 = Player(0, 0, 50, 50, 'Archer', 'Blue', game=self)
        player3.control_type = 'joystick'
        self.saved_players[player3.id] = player3
        self.player_slots.append(player3)

        player4 = Player(0, 0, 50, 50, 'Pawn', 'Blue', game=self)
        player4.control_type = 'joystick'
        self.saved_players[player4.id] = player4
        self.player_slots.append(player4)
    
        self.CACHED_ENTITY_ZOOM_IMAGES = {}
        self.entity_sprite_cache = {}
        self.object_sprite_cache = {}

        # Dictionary to store active touches
        self.touches = {}

        self.zoom_in_btn = UIButton(30, 10, 80, 40, "+", self.font, (150, 50, 50), (80, 80, 80))
        self.zoom_out_btn = UIButton(30, 60, 80, 40, "-", self.font, (50, 150, 50), (80, 80, 80))

        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 1.5
        self.zoom_speed = 0.05
        self.scroll_area_width = 200
        self.offset_x = 0
        self.offset_y = 0

        self.keys = []
        self.env_ready = False

        self.initialise_main_window()
        self.initialise_menu()
        self.initialise_grid()
        self.initialise_player_edit()

        self.fix_orientation()
        self.lock = threading.Lock()
        self.log = 0
        self.control_type = 'joystick'

        self.level = level

        self.color_zones = {
            "normal": (50, 50, 255),
            "current": (50, 50, 200),
            "toxic": (70, 220, 70),
            "healing": (0, 200, 100),
            "lava": (255, 80, 0)
        }
        
        self.bombs = Bombs(game=self)

        self.sounds = Sounds(self.player, 4)

        self.dead_entities = []
        self.start_points = (0, -200)

        self.dt = 0
        self.game_speed = 1
        self.max_game_speed = 1

        self.bg_color = (10, 10, 10)
        self.parallax_color = (22, 19, 40)

        self.selectedx, self.selectedy = (0, 0)
        self.chunk_w, self.chunk_h = (12, 12)

        self.draw_list        = []      # built once, reused until dirty
        self.draw_list_2 = []
        self._draw_list_dirty = True    # True on first frame → triggers build

    def initialise_constants(self):
        self.bg_image = pygame.transform.scale(pygame.image.load("assets/Background/space.jpg"),
                                               (self.WIDTH, self.HEIGHT)).convert()

        self.menu_bg = pygame.transform.scale(pygame.image.load("assets/Background/menu_bg.jpg"),
                                              (self.WIDTH, self.HEIGHT)).convert()

    def update_main_window_btns_pos(self):

        spacing = 10

        self.joystick_radius = 150
        self.joystick_x, self.joystick_y = 200, Settings.HEIGHT - self.joystick_radius - spacing * 2
        self.joystick_center = (self.joystick_x, self.joystick_y)

        self.bomb_joystick_x, self.bomb_joystick_y = Settings.WIDTH - self.bomb_joystick_radius, Settings.HEIGHT - self.bomb_joystick_radius

        self.player_joystick_x, self.player_joystick_y = self.player_joystick_radius + 50, Settings.HEIGHT - self.player_joystick_radius - 50

    def initialise_main_window(self):

        spacing = 10
        self.BUTTON_WIDTH = 20
        num_of_start_btns = 6
        self.GRID_BUTTON_HEIGHT = (Settings.HEIGHT / 2) // num_of_start_btns


        self.SENSOR_DISTANCE = 100

        # Set up the bomb joystick
        self.bomb_joystick_radius = 200
        self.bomb_joystick_x, self.bomb_joystick_y = Settings.WIDTH - self.bomb_joystick_radius, Settings.HEIGHT - self.bomb_joystick_radius
        self.bomb_joystick_angle = 0
        self.bomb_joystick_power = 0
        self.power_factor = 20
        self.bomb_joystick_tapping = False
        self.bomb_controlling_finger = None

        # Set up the player joystick
        self.player_joystick_radius = 150
        self.player_joystick_x, self.player_joystick_y = self.player_joystick_radius + 50, Settings.HEIGHT - self.player_joystick_radius - 50
        self.player_joystick_angle = 0
        self.player_joystick_power = 0
        self.player_x_vel_power = 20
        self.player_y_vel_power = 20
        self.player_joystick_tapping = False
        self.player_controlling_finger = None
        
        self.VIEW = False
        self.SPECTATING = False
        self.MENU = False

        # MODES 

        self.MENU_BUTTON_WIDTH = 200
        num_of_start_btns = 10
        self.MENU_BUTTON_HEIGHT = (Settings.HEIGHT - (num_of_start_btns * 30)) // num_of_start_btns
        self.SPACE = self.MENU_BUTTON_HEIGHT
        self.MENU_BUTTONS_POSITION = Settings.WIDTH / 2 - self.MENU_BUTTON_WIDTH / 2

        self.MULTIPLAYER = False
        self.SERVER = False

    def update_menu_btns_pos(self):
        pass

    def initialise_menu(self):
        self.menu_bg = pygame.transform.scale(self.menu_bg, (self.WIDTH, self.HEIGHT)).convert()

        self.sprite_index = 0
        self.animation_count = 1
        self.ANIMATION_DELAY = 2
        
        # Game Settings
        self.EDIT_WORLD = False

        # Player Settings
        self.AUTO_SHOOT = True

    # -------------------------------------------------- WORLD EDITOR ---------------------------------------------------- #

    def update_grid_btns_pos(self):
        pass

    def initialise_grid(self):
        # GRID BLOCK SETTINGS
        self.INSERT = True
        self.EDIT_GRID = 0

        self.confirm = None
        
        blocks = list(Assets.blocks.keys())
        all_blocks = []
        for type_ in block_pallete.keys():
            for variant in block_pallete[type_].keys():
                for index, name in enumerate(blocks):
                    if ("stone" in name or "grass" in name or "brick" in name):
                        if variant == "1":
                            var = name
                        else:
                            var = f"{name}_{variant}"
                    else:
                        var = name
                    
                    if var not in all_blocks:
                        all_blocks.append(var)


        self.block_types = [all_blocks]
        self.block_sizes = ['big', 'small']

        self.type_num = 0
        self.block_num = 0
        self.size_num = 0

        self.prev = None
        self.platform = []
        self.prev_num = 0
        self.thing = None

        self.history = {'flow-rise': f'1;0'}
        self.perspective = "fore"
        self.pressed = False

        self.edit_grid_settings = {
            0: {
                'button_text': 'CHANGE TO ENTITIES',
                'change_size_text': 'CHANGE SIZE',
                'block_types': [all_blocks],
                'block_sizes': ['big', 'small']
            },
            1: {
                'button_text': 'CHANGE TO TREASURE',
                'change_size_text': 'CHANGE COLOUR',
                'block_types': [['TNT'], ['Pawn'], ['Warrior'], ['Torch'], ['Archer']],
                'block_sizes': list(entity_pallete.keys())
            },
            2: {
                'button_text': 'CHANGE TO DECO',
                'change_size_text': '',
                'block_types': [['red', 'pink', 'green', 'yellow']],
                'block_sizes': []
            },
            3: {
                'button_text': 'CHANGE TO WATERZONES',
                'change_size_text': '',
                'block_types': [['tree'], ['grass1'], ['grass2'], ['shrub1'], ['shrub2'], ['shrub3'],
                                ['shroom1'], ['shroom2'], ['shroom3'], ['exit'], ['bone'], ['arrow'],
                                ['scare_crow'], ['pumpkin1'], ['pumpkin2']],
                'block_sizes': []
            },
            4: {
                'button_text': 'CHANGE TO PLATFORMS',
                'change_size_text': '',
                'block_types': [['normal'], ['current'], ['healing'], ['toxic'], ['lava']],
                'block_sizes': []
            },
            5: {
                'button_text': 'CHANGE TO BLOCKS',
                'change_size_text': '',
                'block_types': [['normal'], ['current']],
                'block_sizes': []
            }
        }

        self.world_rules = {
            "platforms" : {"block_fore", "entities", "deco", "platforms", "treasure"},
            "spawn_point" : {"block_fore", "entities", "platforms"},
            "water" : {"water"},
            "deco" : {"block_fore", "deco", "platforms", "treasure"},
            "treasure" : {"block_fore", "deco", "platforms", "block_back", "treasure"},
            "entities" : {"block_fore", "entities", "platforms"},
            "block_fore" : {"block_fore", "entities", "deco", "platforms", "block_back"},
            "block_back" : {"block_fore", "block_back"}
        }

    def personalise(self, entity):
        if not self.settings.get("entity", None):
            return
        for k, v in self.settings["entity"][entity.name].items():
            setattr(entity, k, v)

    
    def load_world(self):
        self.map = {}
        self.node_map = {}
        self.platforms = []
        self.grid = []
        self.enemy_list = []
        self.dead_entities = []
        self.objects = []
        self.bg_objects = []
        self.damageable_objects = []
        self.treasure_list = []
        self.fire_list = []
        self.projectile_list = []
        self.spawn_points = []
        self.zones = []
        self.bubbles = []
        self.splashes = []
        self.nodes = []
        self.air_nodes = []
        self.settings = {}
        self.world = [
            {
                "type": "entity settings",
                "Torch": {
                    "acquire_range": 1000,
                    "acquire_down": 300,
                    "acquire_up": 300,
                    "attack_up": 50,
                    "attack_down": 50,
                    "attack_range": 50,
                    "attack_power": 4
                },
                "Pawn": {
                    "acquire_range": 1000,
                    "acquire_down": 300,
                    "acquire_up": 300,
                    "attack_up": 50,
                    "attack_down": 50,
                    "attack_range": 40,
                    "attack_power": 5
                },
                "Warrior": {
                    "acquire_range": 1000,
                    "acquire_down": 300,
                    "acquire_up": 300,
                    "attack_up": 50,
                    "attack_down": 50,
                    "attack_range": 50,
                    "attack_power": 6
                },
                "TNT": {
                    "acquire_range": 1000,
                    "acquire_down": 300,
                    "acquire_up": 300,
                    "attack_up": 300,
                    "attack_down": 300,
                    "attack_range": 600,
                    "attack_power": 8
                },
                "Archer": {
                    "acquire_range": 1000,
                    "acquire_down": 300,
                    "acquire_up": 300,
                    "attack_up": 300,
                    "attack_down": 300,
                    "attack_range": 600,
                    "attack_power": 7
                }
            },
            {
                "x": 0,
                "y": -64,
                "points": [[0, 64], [0, -64]],
                "width": 64,
                "height": 64,
                "type": "start"
            },
            {
                "x": 0,
                "y": -64,
                "width": 64,
                "height": 64,
                "interval": 5,
                "limit": 5,
                "type": "spawn_point",
                "entities": [
                    [
                        "Pawn",
                        "Red"
                    ]
                ]
            },
            {
                "x": 0,
                "y": 0,
                "width": 64,
                "height": 64,
                "type": "block",
                "name": "stone",
                "size": "big"
            }
        ]
        self.all_entities = []
        self._entities_dirty = True


        try:
            with open(f"levels/{self.level}.json", "r") as f:
                self.world = json.load(f)

        except FileNotFoundError as e:
            print(f"{e} in load_world() creating one")
            with open(f"levels/{self.level}.json", "w") as w:
                json.dump(self.world, w, indent=2)

            with open(f"levels/{self.level}.json", "r") as r:
                self.world = json.load(r)
        
        
        self.env_ready = False
        threading.Thread(target=self.create_nodes, daemon=True).start()

    def prep(self):
        processed_data = []
        x, y, level = 10, 0, 0

        self.temp_grid_map = map_chunks({}, self.grid, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h, True, grid=True)
        # Checking to see if the grid rectangles are occupied
        for data in self.world:
            rect = pygame.Rect(data.get("x", 1), data.get("y", 1), data.get("width", 64), data.get("height", 64))
            added = False
            nearby_nodes = physics.get_objects(self.temp_grid_map, rect, 128, grid=True)
            nearby_nodes = remove_duplicates(nearby_nodes)
            for grid_info in nearby_nodes:
                # data['y'] = data.get("y", 0) - (64 * y if self.level == level else 0)
                # data['x'] = data.get("x", 0) - (64 * x if self.level == level else 0)
                
                skip = False
                delete = False
                collided = False
                
                if not added and data.get("type", None) == "entity settings":
                    self.settings["entity"] = data
                    processed_data.append(data)
                    break

                elif not added and data.get("type", None) == "start":
                    self.start_points = data.get("x", 0), data.get("y", 0)
                    self.points = data.get("points", [])
                    processed_data.append(data)
                    break

                if (
                    grid_info[0].x < data.get("x", 1) + data.get("width", 64) and
                    grid_info[0].x + grid_info[0].width > data.get("x", 1) and
                    grid_info[0].y < data.get("y", 1) + data.get("height", 64) and
                    grid_info[0].y + grid_info[0].height > data.get("y", 1)
                    ) and not skip:
                    grid_info[1] = (9, 8, 7)
                    collided = True
                
                if collided and data.get("type", None) == "block":
                    if data.get("perspective", "fore") == "back":
                        blacklist = {"block_fore", "block_back"}
                        if grid_info[2].isdisjoint(blacklist):
                            grid_info[2].add("block_back")
                            if not added:
                                self.bg_objects.append(
                                    Block(data.get("x", None), data.get("y", None), data.get("width", None), data.get("height", None),
                                        data.get("name", None), data.get("size", None), perspective="back"))
                        else:
                            delete = True

                    else:
                        blacklist = {"block_fore", "entities", "deco", "platforms", "block_back"}
                        if grid_info[2].isdisjoint(blacklist):
                            grid_info[2].add("block_fore")
                            if not added:
                                self.objects.append(
                                    Block(data.get("x", None), data.get("y", None), data.get("width", None), data.get("height", None),
                                        data.get("name", None), data.get("size", None), perspective="fore"))
                                skip = True  # Coz its no route for nodes
                                grid_info[1] = self.BLACK
                        else:
                            delete = True                           
                
                elif collided and data.get("type", None) == "enemy":
                    blacklist = {"block_fore", "entities", "platforms"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("entities")
                        if not added:
                            obj_ = Enemy(data.get("x", None), data.get("y", None), data.get("width", None), data.get("height", None),
                                data.get("name", None), data.get("color", None), game=self)
                            #self.personalise(obj)
                            #print(obj_.__dict__)
                            #print("SIZE : ", get_total_size(obj_))

                            self.enemy_list.append(
                                obj_)
                            self._entities_dirty = True
                    else:
                        delete = True
                
                elif collided and data.get("type", None) == "treasure":
                    blacklist = {"block_fore", "deco", "platforms", "block_back", "treasure"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("treasure")
                        if not added:
                            self.treasure_list.append(
                                Treasure(data.get("x", None), data.get("y", None), data.get("name", None), self))
                    else:
                        delete = True

                elif collided and data.get("type", None) == "deco":
                    blacklist = {"block_fore", "deco", "platforms", "treasure"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("deco")
                        if not added:
                            self.damageable_objects.append(
                                Deco(data.get("x", None), data.get("y", None), data.get("name", None), self))
                    else:
                        delete = True
                
                elif collided and data.get("type", None) == "tree":
                    blacklist = {"block_fore", "deco", "platforms", "treasure"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("deco")
                        if not added:
                            self.damageable_objects.append(Tree(data.get("x", None), data.get("y", None), self))
                    else:
                        delete = True
                
                elif collided and data.get("type", None) == "water":
                    grid_info[1] = (1, 1, 1)
                    blacklist = {"water"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("water")
                        if not added:
                            self.zones.append(WaterZone(data.get("x", None), data.get("y", None), data.get("width", None),
                                                        data.get("height", None), data.get("water_type", None), self,
                                                        tuple(data.get("color", None)), data.get("flow", None),
                                                        bool(data.get("rise", None))))
                        
                    else:
                        delete = True
                
                elif collided and data.get("type", None) == "spawn_point":
                    blacklist = {"block_fore", "entities", "platforms"}
                    if grid_info[2].isdisjoint(blacklist):
                        grid_info[2].add("entities")
                        if not added:
                            self.spawn_points.append(
                                Spawn_Point(
                                    data.get("x", None),
                                    data.get("y", None),
                                    data.get("width", None),
                                    data.get("height", None),
                                    data.get("interval", None),
                                    data.get("limit", None),
                                    data.get("entities", None),
                                    self
                                )
                            )
                    else:
                        delete = True
                    
                    self.log += 1
                
                elif collided and data.get("type", None) == "moving_platform":
                    grid_info[1] = (1, 1, 1)
                    if grid_info[2].isdisjoint(self.world_rules["platforms"]):
                        grid_info[2].add("platforms")
                        if not added:
                            self.platforms.append(
                                Platform(
                                    data.get("x", None),
                                    data.get("y", None),
                                    data.get("width", None),
                                    data.get("height", None),
                                    data.get("moving", None),
                                    data.get("direction", None),
                                    data.get("speed", None),
                                    data.get("dest_x", [data.get("min_x", 0), data.get("max_x", 0)]),
                                    data.get("dest_y", [data.get("y", 0), data.get("y", 0)]),
                                    self
                                )
                            )
                    else:
                        delete = True

                # Delete is for unwanted overlaps with other elements
                if not delete:
                    if collided and not added:
                        added = True
                        processed_data.append(data)
                else:
                    grid_info[1] = self.RED
        
        self.world = processed_data
        
        # DIVIDE THE WORLD INTO CHUNKS (IMMOVABLE-STRUCTURES)
        self.map = map_chunks(self.map, self.objects, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h, True) 
        
        """
        for pos in self.map.values():
            print(f"Blocks : {len(pos[1])}")
        """
        #self.objects.extend(self.platforms)
        self._draw_list_dirty = True

        self.all_entities = [*self.enemy_list, *self.players]
        self._entities_dirty = True

        self.spatial_grid = SpatialGrid(cell_size=512)
        
    def create_nodes(self):
        self.start = time.time()
        
        self.create_grid()
        self.prep()
        
        nodes = []        
        for grid in self.grid:
            blacklist = {"block_fore"}
            if grid[2].isdisjoint(blacklist):
                nodes.append(grid)

        print("Len of nodes", len(nodes))
        self.temp_grid_map = map_chunks({}, self.grid, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h, True, grid=True)
        for node in nodes:
            var = 0
            nearby_nodes = physics.get_objects(self.temp_grid_map, node[0], 128, grid=True)
            nearby_nodes = remove_duplicates(nearby_nodes)
            for grid_info in nearby_nodes:
                if node == grid_info:
                    continue

                dx = abs(node[0].centerx - grid_info[0].centerx)
                dy = abs(node[0].centery - grid_info[0].centery)

                if dy < 66 and dx < 66 and grid_info[1] != self.BLACK:
                    var += 1

                if var >= 8:
                    break

            if var <= 7 or node[1] == (1, 1, 1):
                self.nodes.append(
                    PlatformNode(
                        node[0]
                    )
                )

            if var == 8 and node[1] == self.RED:
                self.air_nodes.append(
                    PlatformNode(
                        node[0]
                    )
                )
            
        
        print("Number of block (filled) nodes:", len(self.nodes))
        print("Number of air (blanks):", len(self.air_nodes))
        
        temp_node_map = map_chunks({}, self.nodes, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h, True)

        
        print(time.time() - self.start)
        self.start = time.time()
        
        self.connect_nodes(self.nodes, temp_node_map)

    def connect_nodes(self, nodes, map={}):
        for node in nodes:
            for other in remove_duplicates(physics.get_objects(map, node.rect, 300)):
                if node == other:
                    continue

                # Remove/Skip diagonal nodes
                diagonal = False
                x, y = node.rect.center
                size = 64
                for e, i in enumerate(
                        [(x + size, y + size), (x - size, y + size), (x + size, y - size), (x - size, y - size)]):
                    if other.rect.collidepoint(i):
                        diagonal = True
                        break

                if diagonal:
                    continue

                dx = abs(node.rect.centerx - other.rect.centerx)
                dy = abs(node.rect.centery - other.rect.centery)

                if dy < 66 and dx < 66:
                    node.neighbors.append(other)

        print('connected')
        self.env_ready = True

        self.node_map = map_chunks(self.node_map, self.nodes, self.minx, self.miny, self.maxx, self.maxy, 5, 5, True)
        
        self.g_score = {node: float('inf') for node in self.nodes}
        
        print(time.time() - self.start)

    def grid_settings_manager(self, event, events):
        if self.control_type == "touch":
            self.clicked = True

        # Inserting or Deleting Items from the Grid
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.pressed = False
            if event.button == 1:
                self.clicked = False

        if event.type == pygame.MOUSEMOTION:
            if self.EDIT_WORLD and self.clicked:
                new_offset_x = self.offset_x - event.rel[0]
                new_offset_y = self.offset_y - event.rel[1]

                self.offset_x = max(self.minx, min(new_offset_x, self.maxx - (Settings.WIDTH / self.zoom)))
                self.offset_y = max(self.miny, min(new_offset_y, self.maxy - (Settings.HEIGHT / self.zoom)))
            
            if self.pressed:
                self.handle_grid_click(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.pressed = True
                return

            if event.button == 1:
                self.clicked = True
                if self.EDIT_WORLD:
                    blocks = list(Assets.blocks.keys())
                    all_blocks = []
                    for type_ in block_pallete.keys():
                        for variant in block_pallete[type_].keys():
                            for index, name in enumerate(blocks):
                                if ("stone" in name or "grass" in name or "brick" in name):
                                    if variant == "1":
                                        var = name
                                    else:
                                        var = f"{name}_{variant}"
                                else:
                                    var = name
                                
                                if var not in all_blocks:
                                    all_blocks.append(var)


                    self.edit_grid_settings = {
                        0: {
                            'button_text': 'CHANGE TO ENTITIES',
                            'change_size_text': 'CHANGE SIZE',
                            'block_types': [all_blocks],
                            'block_sizes': ['big', 'small']
                        },
                        1: {
                            'button_text': 'CHANGE TO TREASURE',
                            'change_size_text': 'CHANGE COLOUR',
                            'block_types': [['TNT'], ['Pawn'], ['Warrior'], ['Torch'], ['Archer']],
                            'block_sizes': list(entity_pallete.keys())
                        },
                        2: {
                            'button_text': 'CHANGE TO DECO',
                            'change_size_text': '',
                            'block_types': [['red', 'pink', 'green', 'yellow']],
                            'block_sizes': []
                        },
                        3: {
                            'button_text': 'CHANGE TO WATERZONES',
                            'change_size_text': '',
                            'block_types': [['tree'], ['grass1'], ['grass2'], ['shrub1'], ['shrub2'], ['shrub3'],
                                            ['shroom1'], ['shroom2'], ['shroom3'], ['exit'], ['bone'], ['arrow'],
                                            ['scare_crow'], ['pumpkin1'], ['pumpkin2']],
                            'block_sizes': []
                        },
                        4: {
                            'button_text': 'CHANGE TO PLATFORMS',
                            'change_size_text': '',
                            'block_types': [['normal'], ['current'], ['healing'], ['toxic'], ['lava']],
                            'block_sizes': []
                        },
                        5: {
                            'button_text': 'CHANGE TO BLOCKS',
                            'change_size_text': '',
                            'block_types': [['normal'], ['current']],
                            'block_sizes': []
                        }
                    }

                self.handle_grid_click(event)

    def handle_grid_click(self, event):
        if self.EDIT_GRID == 0:
            self.mode = "block_" + self.perspective
        elif self.EDIT_GRID == 1:
            self.mode = "entities"
        elif self.EDIT_GRID == 2:
            self.mode = "treasure"
        elif self.EDIT_GRID == 3:
            self.mode = "deco"
        elif self.EDIT_GRID == 4:
            self.mode = "water"
        else:
            self.mode = "platforms"
        
        for index, grid_info in enumerate(self.grid):
            grid_rect = pygame.Rect(int(grid_info[0].x - self.offset_x) * self.zoom,
                                    int(grid_info[0].y - self.offset_y) * self.zoom,
                                    int(grid_info[0].width) * self.zoom,
                                    int(grid_info[0].height) * self.zoom)
            
            if grid_rect.collidepoint(event.pos):
                addable = grid_info[2].isdisjoint(self.world_rules[self.mode])
                if self.INSERT and (self.confirm == grid_info[0]  or self.pressed) and addable:
                        self.insert_object(index, grid_info)

                elif not self.INSERT and (self.confirm == grid_info[0] or self.pressed):
                    self.delete_object(index, grid_info)
                    
                else:
                    self.confirm = grid_info[0]
                    if (
                            addable or not self.INSERT
                    ):
                        if self.prev:
                            self.grid[self.prev[0]][1] = self.prev[1]
                        self.prev = (index, grid_info[1], addable)
                        grid_info[1] = self.BLUE

                        self.selectedx, self.selectedy = grid_info[0].topleft

                        if self.EDIT_GRID == 5:
                            if addable:
                                self.platform.append(grid_info[0])
                                self.platform = self.platform[-2:]

                                if len(self.platform) == 2:
                                    self.confirm = grid_info[0]
                                self._draw_list_dirty = True
                    
                break

    def insert_object(self, index, grid_info):
        grid_info[1] = self.BLACK
        grid_info[2].add(self.mode)
                        
        if self.EDIT_GRID == 0:
            self.add_block(grid_info)
            self.map = map_chunks(self.map, self.objects, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h)
        elif self.EDIT_GRID == 1:
            self.add_enemy(grid_info)
        elif self.EDIT_GRID == 2:
            self.add_treasure(grid_info)
        elif self.EDIT_GRID == 3:
            self.add_deco(grid_info)
        elif self.EDIT_GRID == 4:
            self.add_water(grid_info)
        else:
            self.add_platform(grid_info)

        self.prev = (index, grid_info[1])
        self._draw_list_dirty = True                                   
        self.confirm = None
        self.platform = []

    def delete_object(self, index, grid_info):
        self.prev = (index, grid_info[1])
        self._draw_list_dirty = True
        self.remove(grid_info)
        self.confirm = None
        if not grid_info[2]:
            grid_info[1] = self.RED

    def add_platform(self, grid_info):
        self.item_size = f'100;20'
        size = self.enter_text(self.item_size)
        width = int(size.split(';')[0])
        height = int(size.split(';')[1])

        item_size = f'{-1 if self.platform[0].x > self.platform[1].x else 1},{-1 if self.platform[0].y > self.platform[1].y else 1};1;100'
        size = self.enter_text(item_size)
        direction = [int(size.split(';')[0].split(',')[0]), int(size.split(';')[0].split(',')[1])]
        moving = bool(size.split(';')[1])
        speed = int(size.split(';')[2])
        color = self.color_zones.get(self.type, (50, 200, 50))
        minx = min(self.platform[0].left, self.platform[1].left)
        maxx = max(self.platform[1].right, self.platform[0].right)

        miny = min(self.platform[0].top, self.platform[1].top)
        maxy = max(self.platform[1].bottom, self.platform[0].bottom)

        plat = Platform(grid_info[0].x, grid_info[0].y, width, height, moving, direction, speed, (minx,
                        maxx),(miny,
                        maxy), self)
        self.platforms.append(
            plat
        )
        """self.objects.append(
            plat
        )"""
        data = {
            "x": grid_info[0].x,
            "y": grid_info[0].y,
            "width": width,
            "height": height,
            "moving": moving,
            "direction": direction,
            "type": "moving_platform",
            "speed": speed,
            "dest_x": [minx, maxx],
            "dest_y": [miny, maxy],
            "min_x": minx,
            "max_x": maxx,
            "path": [[0, 0]],
            "color": list(color)
        }
        self.world.append(data)

    def add_water(self, grid_info):
        self.item_size = f'64;64'
        flow_rise = self.history['flow-rise']

        if not self.pressed:
            flow_rise = self.enter_text(self.history['flow-rise'])

            self.item_size = self.enter_text(self.item_size)

        width = int(self.item_size.split(';')[0])
        height = int(self.item_size.split(';')[1])

        self.history['flow-rise'] = flow_rise
        flow = int(flow_rise.split(';')[0])
        rise = bool(flow_rise.split(';')[1])
        color = self.color_zones.get(self.type, (50, 200, 50))

        self.zones.append(WaterZone(grid_info[0].x, grid_info[0].y, width, height, self.type, self,
                                    color, flow,
                                    rise))

        data = {
            "x": grid_info[0].x,
            "y": grid_info[0].y,
            "width": width,
            "height": height,
            "type": "water",
            "water_type": self.type,
            "color": list(color),
            "flow": flow,
            "rise": rise
        }
        self.world.append(data)

    def add_block(self, grid_info):
        image = get_block(self.type, self.size)
        self.item_size = f'{image.get_width()};{image.get_height()}'

        if not self.pressed:
            self.item_size = self.enter_text(self.item_size)

        width = int(self.item_size.split(';')[0])
        height = int(self.item_size.split(';')[1])
        
        if self.perspective == "back":
            self.bg_objects.append(Block(grid_info[0].x, grid_info[0].y, width, height, self.type, self.size, game=self, perspective=self.perspective))
        else:
            self.objects.append(Block(grid_info[0].x, grid_info[0].y, width, height, self.type, self.size, game=self, perspective=self.perspective))
        
        data = {
            "x": grid_info[0].x,
            "y": grid_info[0].y,
            "width": width,
            "height": height,
            "type": "block",
            "name": self.type,
            "size": self.size,
            "perspective": self.perspective
        }

        self.world.append(data)

    def add_enemy(self, grid_info):

        enemy = Enemy(grid_info[0].x, grid_info[0].y, grid_info[0].width, grid_info[0].width, self.type, self.size,
                      self)
        enemy.update_sprite()

        data = {
            "x": grid_info[0].x,
            "y": grid_info[0].y,
            "width": enemy.rect.width,
            "height": enemy.rect.height,
            "type": "enemy",
            "name": self.type,
            "color": self.size
        }

        self.world.append(data)

        self.enemy_list.append(enemy)
        self._entities_dirty = True

    def add_treasure(self, grid_info):

        data = {
            "x": grid_info[0].x,
            "y": grid_info[0].y,
            "width": grid_info[0].width,
            "height": grid_info[0].height,
            "type": "treasure",
            "name": self.type
        }

        self.world.append(data)

        treasure = Treasure(grid_info[0].x, grid_info[0].y, self.type, self)
        self.treasure_list.append(treasure)

    def add_deco(self, grid_info):

        if self.block_types[self.type_num][self.block_num] == 'tree':

            data = {
                "x": grid_info[0].x,
                "y": grid_info[0].y,
                "width": grid_info[0].width,
                "height": grid_info[0].height,
                "type": "tree",
                "name": self.type
            }

            self.world.append(data)

            self.damageable_objects.append(Tree(grid_info[0].x, grid_info[0].y, self))

        else:
            data = {
                "x": grid_info[0].x,
                "y": grid_info[0].y,
                "width": grid_info[0].width,
                "height": grid_info[0].height,
                "type": "deco",
                "name": self.type
            }

            self.world.append(data)

            self.damageable_objects.append(
                Deco(grid_info[0].x, grid_info[0].y, self.block_types[self.type_num][self.block_num], self))

    def remove(self, grid_info):
        for data in self.world[:]:
            if grid_info[0].collidepoint(data.get("x", 1), data.get("y", 1)):
                done = False
                self._draw_list_dirty = True
                if not grid_info[2]:
                    continue

                order = str(list(grid_info[2])[0])
                # print(order, data)
                if data.get("type", None) == "block" and ("block_fore" == order or "block_back" == order):
                    if data.get("perspective", "fore") == "back":
                        for block in self.bg_objects[:]:
                            if block.rect.colliderect(grid_info[0]):
                                self.bg_objects.remove(block)
                                done = True
                                break
                    else:
                        for block in self.objects[:]:
                            if block.rect.colliderect(grid_info[0]):
                                self.objects.remove(block)
                                self.map = map_chunks(self.map, self.objects, self.minx, self.miny, self.maxx, self.maxy, self.chunk_w, self.chunk_h, True) 
                                done = True
                                break
    
                elif data.get("type", None) == "enemy" and order == "entities":
                    for block in self.enemy_list[:]:
                        if (block.origin_rect.x, block.origin_rect.y, block.origin_rect.width) == (
                                grid_info[0].x, grid_info[0].y, grid_info[0].width):
                            self.enemy_list.remove(block)
                            self._entities_dirty = True
                            done = True
                            break

                elif data.get("type", None) == "treasure" and order == "treasure":
                    for block in self.treasure_list[:]:
                        if (block.origin_rect.x, block.origin_rect.y) == (grid_info[0].x, grid_info[0].y):
                            self.treasure_list.remove(block)
                            done = True
                            break

                elif data.get("type", None) == "deco" and order == "deco":
                    for blck in self.damageable_objects[:]:
                        if (blck.origin_rect.x, blck.origin_rect.y) == (grid_info[0].x, grid_info[0].y):
                            self.damageable_objects.remove(blck)
                            done = True
                            break

                elif data.get("type", None) == "tree" and order == "deco":
                    for blck in self.damageable_objects[:]:
                        if (blck.origin_rect.x, blck.origin_rect.y) == (grid_info[0].x, grid_info[0].y):
                            self.damageable_objects.remove(blck)
                            done = True
                            break

                elif data.get("type", None) == "water" and order == "water":
                    for blck in self.zones[:]:
                        if (blck.origin_rect.x, blck.origin_rect.y) == (grid_info[0].x, grid_info[0].y):
                            self.zones.remove(blck)
                            done = True
                            break

                elif data.get("type", None) == "moving_platform" and order == "platforms":
                    for blck in self.objects[:]:
                        if (blck.origin_rect.x, blck.origin_rect.y) == (grid_info[0].x, grid_info[0].y):
                            self.objects.remove(blck)
                            done = True
                            break
                if done:
                    self.world.remove(data)
                    grid_info[2].discard(order)
                    break

    # -------------------------------------------------- PLAYER EDITOR --------------------------------------------------- #

    def update_player_edit_btns_pos(self):
        pass
    
    def update_player_edit(self):
        for player in self.players:
                if player.id not in self.players_config:
                        self.players_config[player.id] = {
                            'player': player,
                            'confirm_player': None,
                            'player_type_num': player.player_types.index(player.name),
             
                            'player_num': 0,
                            'player_color_num': player.player_colors.index(player.color),

                        }

                if player.id in self.players_config:
                        data = self.players_config[player.id]

                        view_rect = player.viewport.clip(self.window_rect)
                        viewport = self.window.subsurface(view_rect)

                        sw, sh = viewport.get_size()
                        font = pygame.font.SysFont("impact", int(sw * 0.02))
                        
                        button_data = [
                            ("Back", p_s.back_, [self])
                        ]
                        menu = RPGMenu(viewport, font, button_data, p_s.layout)

                        width = 0.12
                        height = 0.06
                        menu.add([('TYPE', p_s.change_type, [self, player.id])],
                                 [(0.5 - (width / 2) - 0.15, 0.2, width, height)])
                        menu.add([('COLOR', p_s.change_color, [self, player.id])],
                                 [(0.5 - (width / 2) + 0.15, 0.2, width, height)])

                        menu.add([('SAVE', p_s.save, [self, player.id])],
                                 [(0.5 - (width / 2) - 0.12, 0.3, width, height)])
                        menu.add([('REMOVE', p_s.remove, [self, player.id])],
                                 [(0.5 - (width / 2) + 0.12, 0.3, width, height)])

                        data['window'] = viewport
                        data['menu'] = menu

                        display_rect = pygame.Rect(
                            int(p_s.rel_rect[0] * sw),
                            int(p_s.rel_rect[1] * sh),
                            int(p_s.rel_rect[2] * sw),
                            int(p_s.rel_rect[3] * sh)
                        )
                        data['display_rect'] = display_rect

        for player in self.player_slots:
            if player not in self.players and player.id in self.players_config:
                del self.players_config[player.id]

    def initialise_player_edit(self):
        self.player_types = ['TNT', 'Pawn', 'Warrior', 'Torch', 'Archer']
        self.player_colors = list(entity_pallete.keys())
        self.players_config = {}

    def player_settings_manager(self, event):
        pass

    def menu_icons(self, other=None):
        if other is None:
            other = []
        for btn in [*self.MENU_BUTTONS, *other]:
            btn.draw(self.window)

    def draw_buttons(self, other=None):
        if other is None:
            other = []
        for btn in other:
            btn.draw(self.window)

    @staticmethod
    def update_buttons(other=None):
        if other is None:
            other = []
        for btn in other:
            btn.update()

    def get_fps(self):
        # Get and draw FPS
        fps = self.clock.get_fps()
        fps_surface = self.font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        self.window.blit(fps_surface, (10, 10))

    def enter_text(self, base_text, input_restrictions=None):
        if input_restrictions is None:
            input_restrictions = [None, None, None, None]
        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u',
                    'v', 'w', 'x', 'y', 'z']
        special_chars = [';']
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        number_specials = ['-', '.']
        entering = True

        original_text = base_text

        backspace_hold = False
        backspace_hold_timer = 0

        while entering:
            self.window.fill((0, 0, 0))
            box = cache_img((get_text_width(base_text, 1) * 2 + 8, 22))
            box.fill((0, 17, 32))

            pos = (int(Settings.WIDTH / 2 - box.get_width() / 2), int(Settings.HEIGHT / 2 - box.get_height() / 2))

            self.window.blit(box, pos)
            text.show_text(base_text, pos[0] + 4, pos[1] + 4, 1, 99999, self.font_, self.window, 2)

            if backspace_hold:
                backspace_hold_timer += 1
            else:
                backspace_hold_timer = 0
            if backspace_hold_timer > 30:
                if base_text != '':
                    base_text = base_text[:-1]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    entering = False

                if event.type == pygame.KEYDOWN:
                    if input_restrictions[0] is None:
                        for char in alphabet:
                            if event.key == ord(char):
                                base_text += char
                    if input_restrictions[1] is None:
                        for char in special_chars:
                            if event.key == ord(char):
                                base_text += char
                    if input_restrictions[2] is None:
                        for char in numbers:
                            if event.key == ord(char):
                                base_text += char
                    if input_restrictions[3] is None:
                        for char in number_specials:
                            if event.key == ord(char):
                                base_text += char
                    if event.key == pygame.K_SPACE:
                        base_text += ' '
                    if event.key == pygame.K_BACKSPACE:
                        backspace_hold = True
                        if base_text != '':
                            base_text = base_text[:-1]
                    if event.key == pygame.K_RETURN:
                        entering = False
                    if event.key == pygame.K_ESCAPE:
                        entering = False
                        base_text = original_text
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_BACKSPACE:
                        backspace_hold = False

            pygame.display.update()
            self.clock.tick(60)

        return base_text


    def _rebuild_all_entities(self) -> None:
        """
        Rebuild self.all_entities from enemy_list + players + dead_entities.
        Call only when _entities_dirty is True.
        spatial_grid.rebuild() already iterates this list — zero extra cost.
        """
        self.all_entities    = list(itertools.chain(
            self.enemy_list, self.players, self.dead_entities
        ))
        self._entities_dirty = False
    
    def _rebuild_draw_list(self, code = 1) -> None:
        """
        Rebuild self.draw_list from all source lists.

        Uses itertools.chain so no intermediate list is allocated — objects are
        yielded from each source list in order without copying.

        Call this only when self._draw_list_dirty is True.  draw_sub() calls it
        automatically; you should not need to call it manually.
        """
        if code:
            self.draw_list = list(itertools.chain(
                self.bg_objects,
                self.bubbles,
                self.bombs.list,
                self.objects,
                self.platforms,
                self.players,
                self.enemy_list,
                self.dead_entities,
                self.damageable_objects,
                self.fire_list,
                self.treasure_list,
                self.zones,
                self.splashes
            ))
        else:
            self.draw_list_2 = [
                self.bg_objects,
                self.bubbles,
                self.bombs.list,
                self.objects,
                self.platforms,
                self.players,
                self.enemy_list,
                self.dead_entities,
                self.damageable_objects,
                self.fire_list,
                self.treasure_list,
                self.zones,
                self.splashes
            ]
        
        self._draw_list_dirty = False

    def draw_sub(self):
        # only rebuild the draw list when something changed
        if self._draw_list_dirty:
            self._rebuild_draw_list()

        try:
            for obj in self.draw_list:
                try:
                    if not self.hide(obj):
                        see_through = False
                        if obj.nature == "damageable_object":
                            if abs(self.player.rect.centerx - obj.rect.centerx) < 96 and \
                               abs(self.player.rect.centery - obj.rect.centery) < 96:
                                see_through = True
                        obj.draw(see_through=see_through,
                                 window=self.window,
                                 cam=(self.offset_x, self.offset_y),
                                 zoom=self.zoom)
                except Exception as e:
                    print(e, "In draw list")
        except Exception as e:
            print(e,"In draw_list")

    def hide(self, item, type_=None, width=None, height=None,
             offset_x=None, offset_y=None, zoom=None, window=None):
        #try:
            width = self.WIDTH if not width else width
            height = self.HEIGHT if not height else height
            offset_x = self.offset_x if not offset_x else offset_x

            offset_y = self.offset_y if not offset_y else offset_y
            zoom = self.zoom if not zoom else zoom
            
            if type_ == "rect":
                margin_x = item.width
                margin_y = item.height
                return (
                        (item.left - offset_x) * zoom < margin_x * zoom or
                        (item.right - offset_x) * zoom > width + margin_x * zoom or
                        (item.top - offset_y) * zoom < margin_y * zoom or
                        (item.bottom - offset_y) * zoom > height + margin_y * zoom
                )
            
            elif type_ == 'special':
                return (
                        (item.rect.left - offset_x) < window.x
                )
            
            else:
                return (
                        (item.rect.right - offset_x) * zoom < 0 or
                        (item.rect.left - offset_x) * zoom > width or
                        (item.rect.bottom - offset_y) * zoom < 0 or
                        (item.rect.top - offset_y) * zoom > height
                )
        #except Exception as e:
        #    print("In hide", e)

    def draw_main(self):

        """# Bg
        self.window.blit(pygame.transform.scale(self.bg_image, (self.WIDTH, self.HEIGHT)), (0, 0))

        color_top = (0, 0, 0)
        color_bottom = (52, 25, 40)
        draw_vertical_gradient(color_top, color_bottom)"""

        self.draw_sub()

        if self.SPECTATING:
            return

        if self.control_type == 'joystick':
            pass

        elif self.control_type == 'touch':
            self.draw_shooting_stick()
            self.draw_player_stick()
           
        else:
            pass

    @staticmethod
    def update(obj_list):
        alive = []
        for i, objects in enumerate(obj_list):
            if i == 3:
                alive += objects
                continue

            for o, obj in sorted(enumerate(objects), reverse=True):
                try:
                    if not obj.dead or (i == 7 and obj.nature == 'entity'):
                        obj.update_sprite()

                    elif obj.dead and i not in [4, 7, 11]:
                        objects.pop(o)

                except Exception as e:
                    print("In static update ", obj.name, obj.type, e)

            alive += objects

        return alive

    def clean(self, objects_list):
        alive = []
        for i, objects in enumerate(objects_list):
            if i in [3, 4, 7, 11]:
                alive += objects
                continue

            for obj in objects:
                if obj.dead:
                    objects.remove(obj)
                    self._draw_list_dirty = True


            alive += objects

        return alive

    def exec(self, func):
        if self._draw_list_dirty:
            self._rebuild_draw_list(0)

        return func(self.draw_list_2)


    def fix_orientation(self, apps=None):
        if apps is None:
            apps = []

        # Get the current screen dimensions

        Settings.WIDTH = pygame.display.Info().current_w
        Settings.HEIGHT = pygame.display.Info().current_h

        self.window_rect = self.window.get_rect()
        new_orientation = 'landscape' if Settings.WIDTH > Settings.HEIGHT else 'portrait'

        if self.orientation != new_orientation:
            self.orientation = new_orientation
            self.window_rect = self.window.get_rect()
            # Update button and UI positions
            self.update_main_window_btns_pos()
            self.update_menu_btns_pos()
            self.update_grid_btns_pos()
            self.update_player_edit_btns_pos()

            # Reinitialize volumes
            self.volumes.initialize()
            for volume in self.volumes.volumes:
                volume.initialize()

            # Reinitialize any extra apps
            for app in apps:
                app.initialize()

    def draw_player_stick(self):

        # Draw the player joystick
        pygame.draw.circle(self.window, Settings.BLACK, (self.player_joystick_x, self.player_joystick_y),
                           self.player_joystick_radius, 2)

        if self.player_joystick_tapping:
            player_joystick_end_x = self.player_joystick_x + math.cos(
                self.player_joystick_angle) * self.player_joystick_radius * self.player_joystick_power

            player_joystick_end_y = self.player_joystick_y + math.sin(
                self.player_joystick_angle) * self.player_joystick_radius * self.player_joystick_power

            pygame.draw.line(self.window, Settings.BLACK, (self.player_joystick_x, self.player_joystick_y),
                             (int(player_joystick_end_x), int(player_joystick_end_y)), 2)

            pygame.draw.circle(self.window, Settings.BLACK, (int(player_joystick_end_x), int(player_joystick_end_y)),
                               10)

    def draw_shooting_stick(self):

        if self.player.name in ["TNT", "Archer"] and not self.AUTO_SHOOT:
            # Draw the bomb joystick
            pygame.draw.circle(self.window, Settings.BLACK, (self.bomb_joystick_x, self.bomb_joystick_y),
                               self.bomb_joystick_radius, 2)

            if self.bomb_joystick_tapping:
                bomb_joystick_end_x = self.bomb_joystick_x + math.cos(
                    self.bomb_joystick_angle) * self.bomb_joystick_radius * self.bomb_joystick_power

                bomb_joystick_end_y = self.bomb_joystick_y + math.sin(
                    self.bomb_joystick_angle) * self.bomb_joystick_radius * self.bomb_joystick_power

                pygame.draw.line(self.window, Settings.BLACK, (self.bomb_joystick_x, self.bomb_joystick_y),
                                 (int(bomb_joystick_end_x), int(bomb_joystick_end_y)), 2)

                pygame.draw.circle(self.window, Settings.BLACK, (int(bomb_joystick_end_x), int(bomb_joystick_end_y)),
                                   10)

            # Draw the trajectory
            if self.bomb_joystick_tapping:
                trajectory = []
                bomb_x = self.player.rect.centerx
                bomb_y = self.player.rect.centery
                bomb_vel_x = math.cos(self.bomb_joystick_angle) * self.bomb_joystick_power * self.power_factor
                bomb_vel_y = math.sin(self.bomb_joystick_angle) * self.bomb_joystick_power * self.power_factor
                if self.player.name == 'Archer':
                    bomb_obj = Arrow(bomb_x, bomb_y, self.player, self.sounds)
                else:
                    bomb_obj = Bomb(bomb_x, bomb_y, self.player, self.sounds)
                bomb_obj.rect.center = self.player.rect.center
                try:
                    bomb_obj.x_vel = bomb_vel_x
                    bomb_obj.y_vel = bomb_vel_y
                    bomb_obj.degree, _ = get_degree(bomb_obj.x_vel, bomb_obj.y_vel, bomb_obj.degree)
                except Exception as e:
                    print(e)

                for _ in range(50):
                    bomb_obj.update_sprite()
                    if bomb_obj.dead:
                        break
                    trajectory.append((bomb_obj.rect.x, bomb_obj.rect.y))

                for dot_x, dot_y in trajectory:
                    pygame.draw.circle(self.window, Settings.RED,
                                       (int(dot_x) - self.offset_x, int(dot_y) - self.offset_y), 5)

    def create_grid(self):
        block_size = 64
        width = 2000
        height = 2000
        for h in range(-height // block_size, height // block_size):
            for w in range(-width // block_size, width // block_size):
                self.grid.append([pygame.Rect(w * block_size, h * block_size, block_size, block_size), self.RED, set()])

        self.minx = min(obj[0].left for obj in self.grid)
        self.miny = min(obj[0].top for obj in self.grid)
        self.maxx = max(obj[0].right for obj in self.grid)
        self.maxy = max(obj[0].bottom for obj in self.grid)
        self.world_rect = pygame.Rect(self.minx, self.miny, self.maxx, self.maxy)

    def update_game_logic(self, u=False):
        if u:
            self.player.update_sprite()
            self.exec(self.update)
            return
        
        self.spatial_grid.rebuild(self.all_entities)
        if not self.player.dead:
            self.player.manage()
        else:
            if not self.done:
                self.done = True

        for enemy in self.enemy_list:
            enemy.manage()

        self.bombs.handle_proccesses()

        self.player.update_sprite()

        self.exec(self.update)

    def joybuttondown(self, player):
        player.attacking = False
        data = []
        x_vel = 0
        y_vel = 0

        x_axis = player.joystick.get_axis(0)  # Left-right movement
        y_axis = player.joystick.get_axis(1)  # Up-down movement

        # Update rectangle position
        x_vel = int(x_axis * 10)
        y_vel = int(y_axis * 10)

        for i in range(player.joystick.get_numbuttons()):
            if player.joystick.get_button(i):  # Check if the button is pressed
                data.append(i)

        if True:
            if 5 in data:
                if not player.dashing:
                    player.dashing = True
                    player.startx = player.rect.x
                    if self.game_speed == self.max_game_speed:
                        self.game_speed = 0

            if x_vel < 0 and 5 not in data and not player.dashing:
                player.move_left(abs((x_vel / 10) * player.current_speed))
                self.request_x = -200

            elif x_vel > 0 and 5 not in data and not player.dashing:
                self.request_x = 200
                player.move_right(abs((x_vel / 10) * player.current_speed))

            if y_vel < 0:
                self.request_y = -200
                if player.zone:
                    player.swim_up()
                elif player.jump_count < 1 or player.jump_count == 1 and player.fall_count > 0.1:
                    player.jump()

            if y_vel > 0:
                self.request_y = 200
                if player.zone:
                    player.swim_down()

        if player.dashing:
            if x_vel > 0:
                player.move_right(abs(player.current_speed * 2))
            elif x_vel < 0:
                player.move_left(abs(player.current_speed * 2))
            
            elif player.direction == "right":
                player.move_right(abs(player.current_speed * 2))
            else:
                player.move_left(abs(player.current_speed * 2))

        # Zoom control
        if 8 in data:  # Zoom in
            player.target_zoom = min(player.target_zoom + 0.05, player.zoom_max)
        elif 9 in data:  # Zoom out
            player.target_zoom = max(player.target_zoom - 0.05, player.zoom_min)
        
        if 7 in data:
            pass

        if 6 in data:
            if not (player.name in ["TNT", "Archer"]) or self.AUTO_SHOOT:
                player.attacking = True

                self.request_attack = True
                player.animation_count += 1
                if "attack" not in player.sprite_sheet:
                    player.animation_count = 0

        player.zoom += (player.target_zoom - player.zoom) * 0.1  # Smooth transition

    def handle_finger_movement(self):
        player = self.player

        x_vel = math.cos(self.player_joystick_angle) * self.player_joystick_power

        y_vel = math.sin(self.player_joystick_angle) * self.player_joystick_power * self.player_y_vel_power

        if x_vel < 0:
            player.move_left(abs(player.current_speed))
        elif x_vel > 0:
            player.move_right(abs(player.current_speed))

        if y_vel < -10:
            if player.zone:
                player.swim_up()
            elif player.jump_count < 1 or player.jump_count == 1 and player.fall_count > 0.1:
                player.jump()

    def handle_keypress(self, player):
        player.attacking = False
        keys = self.keys  # Universal pressed keys

        if not keys:
            return
        
        if (keys[pygame.K_RCTRL] and player.keyboard_num == 0) or (keys[pygame.K_LCTRL] and player.keyboard_num == 1):
            if not player.dashing:
                player.dashing = True
                player.startx = player.rect.x
                if self.game_speed == self.max_game_speed:
                    self.game_speed = 0

        if ((keys[pygame.K_LEFT] and player.keyboard_num == 0) or (
                keys[pygame.K_a] and player.keyboard_num == 1)) and not player.dashing:
            player.move_left(abs(player.current_speed))
            self.request_x = -200

        if ((keys[pygame.K_RIGHT] and player.keyboard_num == 0) or (
                keys[pygame.K_d] and player.keyboard_num == 1)) and not player.dashing:
            self.request_x = 200
            player.move_right(abs(player.current_speed))

        if (keys[pygame.K_UP] and player.keyboard_num == 0) or (keys[pygame.K_w] and player.keyboard_num == 1):
            self.request_y = -200
            if player.zone:
                player.swim_up()
            elif player.jump_count < 1 or player.jump_count == 1 and player.fall_count > 0.1:
                player.jump()

        if (keys[pygame.K_DOWN] and player.keyboard_num == 0) or (keys[pygame.K_s] and player.keyboard_num == 1):
            self.request_y = 200
            if player.zone:
                player.swim_down()

        if (keys[pygame.K_RSHIFT] and player.keyboard_num == 0) or (keys[pygame.K_LSHIFT] and player.keyboard_num == 1):
            if not (player.name in ["TNT", "Archer"]) or self.AUTO_SHOOT:
                player.attacking = True

                self.request_attack = True
                player.animation_count += 1
                if "attack" not in player.sprite_sheet:
                    player.animation_count = 0

        if player.dashing:
            if (keys[pygame.K_RIGHT] and player.keyboard_num == 0) or (keys[pygame.K_d] and player.keyboard_num == 1):
                player.move_right(abs(player.current_speed * 2))
            elif (keys[pygame.K_LEFT] and player.keyboard_num == 0) or (keys[pygame.K_a] and player.keyboard_num == 1):
                player.move_left(abs(player.current_speed * 2))
            elif player.direction == "right":
                player.move_right(abs(player.current_speed * 2))
            else:
                player.move_left(abs(player.current_speed * 2))

        # Zoom control
        if (keys[pygame.K_z] and player.keyboard_num == 1) or (
                keys[pygame.K_n] and player.keyboard_num == 0):  # Zoom in
            player.target_zoom = min(player.target_zoom + 0.05, player.zoom_max)
        if (keys[pygame.K_x] and player.keyboard_num == 1) or (
                keys[pygame.K_m] and player.keyboard_num == 0):  # Zoom out
            player.target_zoom = max(player.target_zoom - 0.05, player.zoom_min)

        player.zoom += (player.target_zoom - player.zoom) * 0.1  # Smooth transition
        player.zoom = round(player.zoom, 2)

