import sys
import pygame
import math
import random

# from .networking import *
from .physics import get_degree
from .assets import Assets
from .settings import Settings
from .objects import Bomb, Arrow
from .object_utils import CACHED_OBJECT_IMAGES, CACHED_OBJECT_ZOOMED_IMAGES
from .functions import (
    RPGMenu, 
    refresh_joysticks, calculate_viewports, 
    parallax_bg, player_settings, playit,
    draw_minimap, cache_font,
    GLOW_CACHE, CACHED_IMAGES, CACHED_RECTS,
    FONTS, CACHED_ENTITY_IMAGES
)


WORLD_WIDTH, WORLD_HEIGHT = 1600, 1200

def handle_fingers(self, event):
    if event.type == pygame.FINGERDOWN:
        event_pos = (event.x * Settings.WIDTH, event.y * Settings.HEIGHT)
        
        # Register new touch
        self.touches[event.finger_id] = event_pos
       
        
        if not self.player_controlling_finger:
            if math.hypot(event_pos[0] - self.player_joystick_x,
                          event_pos[1] - self.player_joystick_y) < self.player_joystick_radius:
                self.player_joystick_tapping = True
                self.player_controlling_finger = event.finger_id

        if self.player.name in ["TNT", "Archer"] and not self.AUTO_SHOOT:
            if not self.bomb_controlling_finger:
                if math.hypot(event_pos[0] - self.bomb_joystick_x,
                              event_pos[1] - self.bomb_joystick_y) < self.bomb_joystick_radius:
                    self.bomb_joystick_tapping = True
                    self.bomb_controlling_finger = event.finger_id

    elif event.type == pygame.FINGERUP:
        # Remove touch when lifted
        if event.finger_id in self.touches:
            del self.touches[event.finger_id]

        if self.player_controlling_finger == event.finger_id:
            self.player_joystick_tapping = False
            self.player_joystick_angle = 0
            self.player_joystick_power = 0
            self.player_controlling_finger = None
            self.player.x_vel = 0

        if self.player.name in ["TNT", "Archer"] and not self.AUTO_SHOOT:
            if self.bomb_controlling_finger == event.finger_id:
                if self.bomb_joystick_tapping:
                    bomb_x = self.player.rect.x
                    bomb_y = self.player.rect.y
                    bomb_vel_x = math.cos(self.bomb_joystick_angle) * self.bomb_joystick_power * 100
                    bomb_vel_y = math.sin(self.bomb_joystick_angle) * self.bomb_joystick_power * 100
                    if self.player.name == "TNT":
                        obj = Bomb(bomb_x, bomb_y, self.player, self.sounds)
                    else:
                        obj = Arrow(bomb_x, bomb_y, self.player, self.sounds)
                        obj.rect.center = self.player.rect.center
                
                    obj.x_vel = bomb_vel_x
                    obj.y_vel = bomb_vel_y

                    if self.player.name == 'Archer':
                        obj.degree, _ = get_degree(obj.x_vel, obj.y_vel, obj.degree)

                        playit("arrow_fly", self.player)

                    self.bombs.list.append(obj)
                    self._draw_list_dirty = True

                    self.player.wait = 0

                self.bomb_joystick_tapping = False
                self.bomb_joystick_angle = 0
                self.bomb_joystick_power = 0
                self.bomb_controlling_finger = None

    elif event.type == pygame.FINGERMOTION:
        event_pos = (event.x * Settings.WIDTH, event.y * Settings.HEIGHT)

        # Update touch position
        self.touches[event.finger_id] = event_pos

        if self.player_controlling_finger == event.finger_id:

            if math.hypot(event_pos[0] - self.player_joystick_x, event_pos[
                                                                     1] - self.player_joystick_y) < self.player_joystick_radius or self.player_joystick_tapping:

                self.player_joystick_angle = math.atan2(event_pos[1] - self.player_joystick_y,
                                                        event_pos[0] - self.player_joystick_x)

                if math.hypot(event_pos[0] - self.player_joystick_x,
                              event_pos[1] - self.player_joystick_y) < self.player_joystick_radius:
                    self.player_joystick_power = math.hypot(event_pos[0] - self.player_joystick_x, event_pos[
                        1] - self.player_joystick_y) / self.player_joystick_radius

                self.player_joystick_tapping = True

        if self.player.name in ["TNT", "Archer"] and not self.AUTO_SHOOT:
            if self.bomb_controlling_finger == event.finger_id:

                if math.hypot(event_pos[0] - self.bomb_joystick_x, event_pos[
                                                                       1] - self.bomb_joystick_y) < self.bomb_joystick_radius or self.bomb_joystick_tapping:

                    self.bomb_joystick_angle = math.atan2(event_pos[1] - self.bomb_joystick_y,
                                                          event_pos[0] - self.bomb_joystick_x)

                    if math.hypot(event_pos[0] - self.bomb_joystick_x,
                                  event_pos[1] - self.bomb_joystick_y) < self.bomb_joystick_radius:
                        self.bomb_joystick_power = math.hypot(event_pos[0] - self.bomb_joystick_x, event_pos[
                            1] - self.bomb_joystick_y) / self.bomb_joystick_radius

                    self.bomb_joystick_tapping = True


def update_game_logic(self):
    self.spatial_grid.rebuild(self.all_entities)
    for entity in self.all_entities:
        entity.manage()

    self.bombs.handle_proccesses()

    return self.exec(self.update)

# Camera shake effect
def apply_shake(cam_rect, intensity=5):
    cam_rect.x += random.randint(-intensity, intensity)
    cam_rect.y += random.randint(-intensity, intensity)

def reset_cache(self):
    global CACHED_OBJECT_IMAGES, CACHED_OBJECT_ZOOMED_IMAGES
    global GLOW_CACHE, CACHED_IMAGES, CACHED_RECTS, FONTS
    global CACHED_ENTITY_IMAGES
    
    CACHED_IMAGES.clear()
    CACHED_RECTS.clear()
    CACHED_RECTS['other'] = {}
    CACHED_RECTS['player_wins'] = {}
    GLOW_CACHE.clear()
    FONTS.clear()
    CACHED_OBJECT_IMAGES['other'].clear()
    CACHED_OBJECT_ZOOMED_IMAGES.clear()
    self.CACHED_ENTITY_ZOOM_IMAGES.clear()
    CACHED_ENTITY_IMAGES.clear()
    self.entity_sprite_cache.clear()
    self.object_sprite_cache.clear()

def main(self, code=0):
    self.initialise_main_window()
    self.initialise_menu()
    self.initialise_grid()
    self.initialise_player_edit()

    self.sounds.play_bg('theme', -1)

    lastx = 0
    lasty = 0

    self.running = True
    self.done = False

    '''
    initialize_server(self)
    e2 = threading.Thread(target=get_clients, args=(self,))
    e2.start()
    '''

    exit_code = True
    pos = (9999999, 9999999)
    abs_pos = (9999999, 9999999)

    clicked = False

    self.speed = 10  # Adjust speed sensitivity
    self.x_vel = 0
    self.x_axis = 0
    self.y_vel = 0
    self.y_axis = 0

    self.SECONDS = 0
    self.delta = 0
    self.new = True

    # Timer variables
    self.start_ticks = pygame.time.get_ticks()
    self.current_ticks = pygame.time.get_ticks()
    self.pause_start = 0
    self.pause_total = 0
    self.elapsed_seconds = (self.current_ticks - self.start_ticks - self.pause_total) // 1000
    self.seconds = 0
    self.minutes = 0

    self.window_rect = self.window.get_rect()
    
    self.debug = {}
    self.keys = {}

    self.bg_particles = []
    self.master_clock = 0
    height = 2

    # SCREEN BUTTONS
    sw, sh = self.window.get_rect().size
    font = cache_font(("impact", int(sw * 0.02)))
    
    def menu(_object):
        print("Start Menu!")
        _object.MENU = True
        _object.pause_start = pygame.time.get_ticks()
        _object.menu()
        _object.pause_total += pygame.time.get_ticks() - _object.pause_start
        print("Menu Ended!")

    def spectate(_object):
        print("Started Spectate Window!")
        _object.SPECATING = True
        _object.spectate()
        print("Ended Spectate Window!")

    def view(_object):
        _object.VIEW = not _object.VIEW
        print(f"Object Info is {'ON' if _object.VIEW else 'OFF'}")
        
    def attack(_object):
        if not (_object.player.name in ["TNT", "Archer"]) or _object.AUTO_SHOOT:
                if _object.player.duration == 0:
                    _object.player.animation_count = 0
                    _object.player.attacking = True
          

    button_data = [
        ("MENU", menu, [self]), 
        ("SPECTATE", spectate, [self]), 
        ("VIEW", view, [self]),
        ("ATTACK", attack, [self])
    ]

    layout = [
        (1 - 0.08 - 0.01, 0.2, 0.08, 0.06), 
        (0.5 - 0.2 - 0.03, 0.03, 0.2, 0.06),
        (0.5 + 0.03, 0.03, 0.2, 0.06),
        (0.65, 0.89, 0.25, 0.06)
    ]

    menu = RPGMenu(self.window, font, button_data, layout)
    
    coin_data = {'yellow': 'gold', 'red': 'ruby', 'green': 'emerald', 'pink': 'pearl'}
    e = "NO ERROR"

    refresh_joysticks(self)
    
    while self.running:
        # THE SHOOT BUTTON ON ANDROID
        menu.exclude((3, not sys.platform == "linux"))
        
        # SETTING BUTTONS ACCORDING TO MODE
        if self.controller_selection:
            menu.exclude(
                [
                    (0, self.controller_selection), 
                    (1, self.controller_selection), 
                    (2, self.controller_selection)
                ]
            )
        else:
            menu.exclude(
                [
                    (0, False), 
                    (1, len(self.players) != 1), 
                    (2, len(self.players) != 1)
                ]
            )
                
        # CAPTURE EVENTS
        self.mouse_pos = pygame.mouse.get_pos()
        self.events = pygame.event.get()

        # CHECK IF NEW LEVEL
        if self.new:
            self.load_world()

            self.start_ticks = pygame.time.get_ticks()
            self.pause_total = 0

            for player in self.players:
                player.rect.x, player.rect.y = self.start_points

            for entity in self.all_entities + self.fire_list + self.bombs.list:
                entity.zone = None

            self.new = False
            reset_cache(self)
        
        if not self.env_ready:
            # --------------------------------------------------------------------------------------------------------------
            # LOADING SCREEN
            # --------------------------------------------------------------------------------------------------------------
            self.loading()
              
        if self._entities_dirty:
           self._rebuild_all_entities()

        if not self.controller_selection:
            # Calculate elapsed time (in seconds)
            self.current_ticks = pygame.time.get_ticks()
            self.elapsed_seconds = (self.current_ticks - self.start_ticks - self.pause_total) // 1000
            self.minutes = self.elapsed_seconds // 60
            self.seconds = self.elapsed_seconds % 60
            self.game_time = f"{self.minutes:02}:{self.seconds:02}"

        '''if self.player.dead:
            self.GAME_OVER = True
            self.game_over()'''

        self.clicked = False
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False
                break
                
            if event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                print(event)
                self.fix_orientation()
                continue
                
            if event.type == pygame.KEYUP:
                self.keys = pygame.key.get_pressed()

            if event.type == pygame.KEYDOWN:
                self.keys = pygame.key.get_pressed()

                # HANDLE MENU BUTTONS EVENTS
                menu.handle_key(event.key)
                
                if self.controller_selection:
                    if self.keys[pygame.K_LSHIFT] or self.keys[pygame.K_RSHIFT]:
                        if self.keys[pygame.K_RSHIFT]:
                            key = ["keyboard", 0]
                        else:
                            key = ["keyboard", 1]

                        if key in self.controllers:
                            for player in self.players:
                                if player.key == key:
                                    break
        
                            player.keyboard_num = None
                            player.control_type = None
                            self.players.remove(player)
                            self._draw_list_dirty = True
                            self._entities_dirty = True

                            self.controllers.remove(key)

                            for i, player in enumerate(self.players):
                                viewport = calculate_viewports(self, len(self.players))[i]
                                player.viewport = pygame.Rect(*viewport)
                            
                        
                        elif len(self.controllers) < 5:
                            slots = self.player_slots.copy()
                            [slots.remove(player) for player in self.players]
                            player = slots[0]
                            
                            self.controllers.append(key)
                            player.key = key
                            player.keyboard_num = key[1]
                            player.control_type = "keyboard"
                            self.players.append(player)
                            self._draw_list_dirty = True
                            self._entities_dirty = True


                            for i, player in enumerate(self.players):
                                viewport = calculate_viewports(self, len(self.players))[i]
                                player.viewport = pygame.Rect(*viewport)
                            
                        self.update_player_edit()

                        
                    if self.keys[pygame.K_RCTRL] or self.keys[pygame.K_LCTRL]:
                        if self.keys[pygame.K_RCTRL]:
                            key = ["keyboard", 0]
                        else:
                            key = ["keyboard", 1]

                        for player in self.players:
                            if key == player.key:
                                player.ready = not player.ready
                                break
                        
                        length_of_ready = len([player.key for player in self.player_slots if player.ready])
                        if  length_of_ready != 0 and length_of_ready == len(self.players):
                            self.controller_selection = False
                            
                            

                # DEBUG KEYS
                if self.keys[pygame.K_0]:
                    self.debug['0'] = not self.debug.get('0', False)

                elif self.keys[pygame.K_1]:
                    self.debug['1'] = not self.debug.get('1', False)

                elif self.keys[pygame.K_2]:
                    self.debug['win'] = not self.debug.get('win', False)

                elif self.keys[pygame.K_3]:
                    self.debug['path'] = not self.debug.get('path', False)

                elif self.keys[pygame.K_4]:
                    self.debug['map'] = not self.debug.get('map', False)

                # EXIT KEYS
                elif self.keys[pygame.K_ESCAPE]:
                    self.running = False
                    del self
                    return
            
            if event.type == pygame.JOYAXISMOTION:
                # HANDLE MENU JOY_BUTTONS EVENTS
                menu.handle_joy(event, "axis")
                
            if event.type == pygame.JOYBUTTONDOWN:
                
                # HANDLE MENU JOY_BUTTONS EVENTS
                menu.handle_joy(event)
                
                if self.controller_selection:
                    if event.button == 0:
                        key = ["joystick", event.joy]

                        if key in self.controllers:
                            for player in self.players:
                                if player.key == key:
                                    break
                         
                            player.keyboard_num = None
                            player.control_type = None
                            self.players.remove(player)
                            self._draw_list_dirty = True
                            self._entities_dirty = True

                            self.controllers.remove(key)

                            for i, player in enumerate(self.players):
                                viewport = calculate_viewports(self, len(self.players))[i]
                                player.viewport = pygame.Rect(*viewport)
                            

                        elif len(self.controllers) < 5:
                            slots = self.player_slots.copy()
                            [slots.remove(player) for player in self.players]
                            player = slots[0]

                            self.controllers.append(key)
                            player.key = key
                            player.joystick = self.active_joys[key[1]]
                            player.joystick_id = key[1]
                            player.control_type = key[0]
                            
                            self.players.append(player)
                            self._draw_list_dirty = True
                            self._entities_dirty = True

                            for i, player in enumerate(self.players):
                                viewport = calculate_viewports(self, len(self.players))[i]
                                player.viewport = pygame.Rect(*viewport)
                            
                        self.update_player_edit()
                                
                    if event.button == 5:
                        for player in self.players:
                            if event.joy == player.joystick_id:
                                player.ready = not player.ready
                                break
                        
                        length_of_ready = len([player.key for player in self.player_slots if player.ready])
                        if  length_of_ready != 0 and length_of_ready == len(self.players):
                            self.controller_selection = False

            if event.type == (pygame.JOYDEVICEADDED or pygame.JOYDEVICEREMOVED):
                refresh_joysticks(self)
                for player in self.players:
                    key = player.key
                    if player.control_type == "joystick":
                        player.joystick = self.active_joys[key[1]]
                        player.joystick_id = key[1]
                
            if event.type == pygame.MOUSEBUTTONUP:
                # MOUSE SCROLLING
                if event.button == 1:
                    clicked = False

            if event.type == pygame.MOUSEMOTION:
                # ABS_POS IS MOUSE POSITION BASED ON PLAYER'S (DISTANCE AND ZOOM) OFFSET.
                abs_pos = ((self.mouse_pos[0] / self.zoom) + self.offset_x, ((self.mouse_pos[1] / self.zoom) + self.offset_y))
        
                # MOUSE SCROLLING
                if clicked:
                    self.offset_x -= event.rel[0]
                    self.offset_y -= event.rel[1]

            if event.type == pygame.MOUSEBUTTONDOWN:
                # ABS_POS IS MOUSE POSITION BASED ON PLAYER'S (DISTANCE AND ZOOM) OFFSET.
                abs_pos = ((self.mouse_pos[0] / self.zoom) + self.offset_x, ((self.mouse_pos[1] / self.zoom) + self.offset_y))
        
                # HANDLE BUTTON EVENTS
                menu.handle_mouse(event)

                # MOUSE SCROLLING
                if event.button == 1:
                    clicked = True

            if sys.platform == "linux":
                if self.player.control_type == 'touch':
                    handle_fingers(self, event)

        if exit_code == 'quit':
            self.running = False
            del self
            return

        if not self.running:
            break
        
        # ENTITY INFO
        if self.VIEW:
            for entity_ in self.all_entities:
                if entity_.rect.collidepoint(abs_pos):
                    self.pause_start = pygame.time.get_ticks()
                    self.entity_info(entity_)
                    self.pause_total += pygame.time.get_ticks() - self.pause_start

                    abs_pos = (99999999, 9999999)
            
        if not self.controller_selection:
            # UPDATE EVERYTHING
            # REMOVING DEAD OBJECTS
            objects_to_draw = update_game_logic(self)

        # MANAGE SPAWN POINTS
        points_done = 0
        for point in self.spawn_points:
            point.update()
            if point.finished:
                points_done += 1

        # CHECK OBJECT IN ZONES
        if self.zones:
            # Precompute zone rects once — no per-entity overhead
            zone_affected = self.all_entities   # already built, no new alloc

            # Include fire and bombs only if lists are non-empty
            if self.fire_list:
                zone_affected = zone_affected + self.fire_list
            if self.bombs.list:
                zone_affected = zone_affected + self.bombs.list
            for entity in zone_affected:
                in_zone = None
                ex, ey = entity.rect.centerx, entity.rect.centery

                for zone in self.zones: # Turn this into a dict map later
                    # Cheaper than filter+lambda: plain attribute access + early out
                    if zone.rect.colliderect(entity.rect):
                        in_zone = zone
                        break

                entity.zone = in_zone
        
        # CHECK LEVEL CRITERIA
        if len(self.enemy_list) == 0 and points_done == len(self.spawn_points):
            self.level += 1
            self.new = True
            continue

        
        # --------------------------------------------------------------------------------------------------------------
        # DRAWING THE SCREEN
        # --------------------------------------------------------------------------------------------------------------
        self.window.fill(self.bg_color)

        # PARALLAX BACKGROUND
        self.bg_particles = parallax_bg(
            self.window, 
            Settings.WIDTH, Settings.HEIGHT, 
            self.bg_particles, self.master_clock,
            threshold=20, height=0,
            parallax_color=Settings.PARALLAX, bg_color=Settings.BG_COLOR
        )

        # NETWORKING SYNCING
        '''
        for player in self.client_list:
            send_sync(self, player)
        '''

        # DRAW EVERY PLAYER'S SCREEN
        for i, player in enumerate(self.players):
            
            key = (str(player.viewport), str(self.window_rect))
            if key not in CACHED_RECTS["player_wins"]:
                CACHED_RECTS["player_wins"][key] = player.viewport.clip(self.window_rect)
            view_rect = CACHED_RECTS["player_wins"][key]
            if view_rect.width <= 0 or view_rect.height <= 0:
                continue
            viewport = self.window.subsurface(view_rect)

            if self.controller_selection:
                # BORDERS FOR PLAYER WINDOWS
                pygame.draw.rect(self.window, (0, 200, 200), view_rect, 1, 20)
                sw, sh = view_rect.size

                font = cache_font(("impact", int(sw * 0.03)))

                # HUD
                label = font.render(f"{player.control_type.capitalize()} | {('WASD' if player.keyboard_num else '< ^ >') if player.control_type == 'keyboard' else player.joystick_id}", True, (255, 255, 255))
                self.window.blit(label, (view_rect.x + sw * 0.03, view_rect.y + sh * 0.05))

                label = font.render(f"PLAYER {player.id} : {'READY' if player.ready else 'NOT READY'}", True, (255, 255, 255))
                self.window.blit(label, (view_rect.x + sw * 0.5 - label.get_width() / 2, view_rect.y + sh * 0.8 + font.get_height()))
                
                player_settings(self, player)
                continue

            # CAMERA FOLLOW PLAYER
            cam_width = int(player.viewport.width / player.zoom)
            cam_height = int(player.viewport.height / player.zoom)
            key = (cam_width, cam_height)
            if key not in CACHED_RECTS["player_wins"]:
                CACHED_RECTS["player_wins"][key] = pygame.Rect(0, 0, cam_width, cam_height)
            cam_rect = CACHED_RECTS["player_wins"][key]
            cam_rect.center = player.rect.center
            
            # BOUNDING BOX FOR WORLD SIZE
            if cam_rect.bottom > self.maxy:
                cam_rect.bottom = self.maxy
            if cam_rect.top < self.miny:
                cam_rect.top = self.miny
            if cam_rect.right > self.maxx:
                cam_rect.right = self.maxx
            if cam_rect.left < self.minx:
                cam_rect.left = self.minx

            # SET GAME SETTINGS TO THE FIRST PLAYER
            if player.entity_id == 0:
                self.offset_x = cam_rect.x
                self.offset_y = cam_rect.y
                self.zoom = player.zoom

            # SHAKE FADE
            if player.shake_frames > 0:
                apply_shake(cam_rect, intensity=player.shake_intensity)
                player.shake_frames -= 1

            # POINTER GPS FOR THE PLAYERS
            #player.target_system.draw_pointers(window=viewport, cam=cam_rect, zoom=player.zoom)
            
            # DRAW EVERYTHING ON THE PLAYER'S PERSPECTIVE
            for obj in objects_to_draw:
                if i == 0:
                    obj.in_screen = False
                if not self.hide(obj, width=view_rect.width, height=view_rect.height, offset_x=cam_rect.x,
                                 offset_y=cam_rect.y, zoom=player.zoom):
                    
                    see_through = False
                    if obj.nature == "damageable_object":
                        if abs(player.rect.centerx - obj.rect.centerx) < 96 and abs(
                                player.rect.centery - obj.rect.centery) < 96:
                            see_through = True
                    
                    obj.in_screen = True
                    obj.draw(see_through=see_through, window=viewport, cam=cam_rect.topleft, zoom=player.zoom)
                
                        
            # Draw minimap in top-right corner of this viewport
            draw_minimap(viewport, player, self.all_entities, map=self.map)

            # DRAW CONTROLLERS
            if player.control_type == 'joystick':
                pass

            elif player.control_type == 'touch':
                self.draw_shooting_stick()
                self.draw_player_stick()

            else:
                pass
            
            # DEBUG WINDOW
            if self.debug.get('map', None):
                # DRAW MAP CHUNKS
                for pos in self.map.values():
                    pygame.draw.rect(self.window, (0, 200, 200), (int((pos[0].x - cam_rect.x) * player.zoom), int((pos[0].y - cam_rect.y) * player.zoom), int(pos[0].width * player.zoom), int(pos[0].height * player.zoom)), 5, 20)
                    
            # BORDERS FOR PLAYER WINDOWS
            pygame.draw.rect(self.window, (0, 200, 200), view_rect, 1, 20)
            sw, sh = view_rect.size

            font = cache_font(("impact", int(sw * 0.02)))

            # HUD
            label = font.render(f"LEVEL: {self.level}", True, (255, 255, 255))
            self.window.blit(label, (view_rect.x + sw * 0.03, view_rect.y + sh * 0.05))

            label = font.render(f"GAME_TIME: {self.minutes}:{self.seconds}", True, (255, 255, 255))
            self.window.blit(label, (view_rect.x + sw * 0.03, view_rect.y + sh * 0.06 + font.get_height()))

            # PLAYER INFO
            for j, data in enumerate(coin_data.items()):
                k, v = data
                size = (view_rect.width * 0.04, view_rect.width * 0.04)
                key = (k, v, size)
                if key not in CACHED_IMAGES:
                    CACHED_IMAGES[key] = pygame.transform.scale(Assets.GEM_SPRITES[k][0], size)

                self.window.blit(CACHED_IMAGES[key], (
                    view_rect.x + sw * 0.03, view_rect.y + (sh * 0.07 + font.get_height() * 2) + (j * size[1])))
                label = font.render(f"{getattr(player, f'{v}_coins')}", True, (255, 255, 255))
                self.window.blit(label, (view_rect.x + sw * 0.03 + size[0] + sw * 0.01,
                                         view_rect.y + (sh * 0.07 + font.get_height() * 2) + (
                                                 j * size[1] + (size[1] / 4))))

            # DEBUG WINDOW
            if self.debug.get('win', None):
                debug = {
                    'ERROR': len(self.object_sprite_cache),
                    'FONTS': len(FONTS),
                    'GLOW_CACHE': len(CACHED_ENTITY_IMAGES),
                    'CACHED_IMAGES': len(CACHED_IMAGES),
                    'CACHED_RECTS[\'other\']': len(CACHED_RECTS['other']),
                    'CACHED_RECTS[\'player_wins\']': len(CACHED_RECTS['player_wins']),
                    'CACHED_ENTITY_IMAGES': len(CACHED_ENTITY_IMAGES),
                    'CACHED_ENTITY_ZOOM_IMAGES': len(self.CACHED_ENTITY_ZOOM_IMAGES[1]),                   
                    'CACHED_OBJECT_IMAGES': len(CACHED_OBJECT_IMAGES['other']),
                    'CACHED_OBJECT_ZOOMED_IMAGES': len(CACHED_OBJECT_ZOOMED_IMAGES),
                    'HIT-WALL-FOR': player.hit_wall_for,
                    'BEEN_FALLING-FOR': player.fall_count,
                    'ON-GROUND-FOR': player.on_ground_for,
                    'IN-AIR-FOR': player.in_air_for,
                    'ENV_READY': self.env_ready
                }

                for i, (k, v) in enumerate(debug.items()):
                    label = font.render(f"{k} {v}", True, (255, 255, 255))
                    self.window.blit(label, (
                        view_rect.x + sw * 0.25, view_rect.y + sh * 0.1 + (font.get_height() + sw * 0.01) * i))

        # MENU BUTTONS
        menu.update(self.mouse_pos)
        menu.draw()
        
        # GAME FPS
        self.get_fps()

        # --------------------------------------------------------------------------------------------------------------
        # HANDLING CACHE
        # --------------------------------------------------------------------------------------------------------------
        
        # HANDLE RECT CACHE
        if len(CACHED_RECTS["player_wins"]) > 2 * len(self.players):
            CACHED_RECTS["player_wins"].clear()
        
        
        # HANDLE ENTITY CACHE
        if len(self.CACHED_ENTITY_ZOOM_IMAGES) > len(self.players):  
            self.CACHED_ENTITY_ZOOM_IMAGES.clear()

        for key in self.CACHED_ENTITY_ZOOM_IMAGES.keys():
            MAX_ZOOM_LEVELS = 300   # a little headroom
            while len(self.CACHED_ENTITY_ZOOM_IMAGES[key]) > MAX_ZOOM_LEVELS:
                oldest_zoom = next(iter(self.CACHED_ENTITY_ZOOM_IMAGES[key]))
                del self.CACHED_ENTITY_ZOOM_IMAGES[key][oldest_zoom]

        if len(CACHED_ENTITY_IMAGES) > 10:
            CACHED_ENTITY_IMAGES.clear()

        # HANDLE OBJECT CACHE
        if len(CACHED_OBJECT_ZOOMED_IMAGES) > len(self.players):
            CACHED_OBJECT_ZOOMED_IMAGES.clear()
        
        for key in CACHED_OBJECT_ZOOMED_IMAGES.keys():
            if len(CACHED_OBJECT_ZOOMED_IMAGES[key]) > 300:  
                CACHED_OBJECT_ZOOMED_IMAGES[key].clear()

        if len(CACHED_OBJECT_IMAGES['other']) > 750:
            CACHED_OBJECT_IMAGES['other'].clear()
        
        if len(CACHED_OBJECT_IMAGES['arrows']) > 350:
            CACHED_OBJECT_IMAGES['arrows'].clear()
            
        # HANDLE OTHER CACHE
        if len(FONTS) > 5:
            FONTS.clear()
        
        if len(CACHED_IMAGES) > 150: # 200
            CACHED_IMAGES.clear()

        if len(CACHED_RECTS['other']) > 100:
            CACHED_RECTS['other'].clear()

        pygame.display.update()
        
        # HANDLE DELTA TIME
        raw_dt = self.clock.tick(self.FPS) / 1000.0
        self.game_speed = min(self.max_game_speed, self.game_speed + 0.1)
        self.dt = round(min(0.1, raw_dt * self.game_speed), 3)

        self.master_clock += int(raw_dt * 80)

    pygame.quit()
    sys.exit(0)
