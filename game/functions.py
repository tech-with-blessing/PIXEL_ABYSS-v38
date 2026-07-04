import time
import random
import pygame
import math

from .assets import Assets
from .settings import Settings
from .physics import distance, PHYSICS
from .data.palletes.blocks import block_pallete
from .data.palletes.entities import entity_pallete
import threading
import random, time

CACHED_ENTITY_IMAGES = {}
CACHED_IMAGES = {}
CACHED_RECTS = {}
CACHED_RECTS['other'] = {}
GLOW_CACHE = {}
FONTS = {}

def remove_duplicates(garbage_list) -> list:
    clean_list = []
    for garbage in garbage_list:
        if garbage not in clean_list:
            clean_list.append(garbage)

    return clean_list

# SOUND PLAYER
def playit(song, origin):
    volume = origin.game.sounds.get_volume(origin)
    main_vol = volume * Settings.IN_GAME_SOUNDS_VOLUME

    channel = pygame.mixer.find_channel()
    if channel and main_vol > 0:
        channel.set_volume(main_vol)
        channel.play(Assets.SOUNDS[song])


def apply_pallete(unchanged_image, pallete, type_="single"):
    if type_ == "list":
        processed_images = list()
        for image in unchanged_image:
            image_ = image.copy()
            for swap in pallete:
                image_ = pallete_swap(image_, (0, 0, 0), (0, 0, 1))
                image_ = pallete_swap(image_, swap[0], swap[1])
                image_.set_colorkey((0, 0, 1, 255))    
            processed_images.append(image_)
        return processed_images
    
    else:
        image_ = unchanged_image.copy()
        for swap in pallete:
            image_ = pallete_swap(image_, swap[0], swap[1])

        image_.set_colorkey((0, 0, 0, 0))    
        return image_


def pallete_swap(surf, old_c, new_c):
    # credit : DaFluffyPotato
    image_copy = pygame.Surface(surf.get_size())
    image_copy.fill(new_c)
    surf.set_colorkey(old_c)
    image_copy.blit(surf, (0, 0))
    return image_copy


def create_cache_img(cache_dict, zoom_key, sprite, zoom=1) -> pygame.Surface:
    # Use cached image if available
    if zoom not in cache_dict:
        cache_dict[zoom] = {}

    if zoom_key in cache_dict[zoom]:
        scaled_image = cache_dict[zoom][zoom_key]
    else:
        scaled_size = (
            int(sprite.get_width() * zoom),
            int(sprite.get_height() * zoom)
        )
        scaled_image = pygame.transform.scale(sprite, scaled_size)
        cache_dict[zoom][zoom_key] = scaled_image
    
    return scaled_image

# CACHE FONTS
def cache_font(key):
    if key not in FONTS:
        FONTS[key] = pygame.font.SysFont(key[0], key[1])
    
    return FONTS[key]

# CACHED GLOW IMAGES
def glow_img(size, color):
    if (size, color) not in GLOW_CACHE:
        surf = pygame.Surface((size * 2 + 2, size * 2 + 2))
        pygame.draw.circle(surf, color, (surf.get_width() // 2, surf.get_height() // 2), size)
        surf.set_colorkey((0, 0, 0))
        GLOW_CACHE[(size, color)] = surf
    return GLOW_CACHE[(size, color)]


def find_last(word, char):
    last_index = -1
    while word.find(char) != -1:
        last_index = word.find(char)
        word = word[:last_index] + "&" + word[last_index + 1:]
    return last_index



# CACHE ASSET IMAGES
def cache_assets(key, color=(0, 0, 0, 0), index="none"):
    #if type_ == 1:
    if (key, color) not in CACHED_ENTITY_IMAGES:
        name, color, sheet_name = key
        if name != "Blue":
            if index == "none":
                images = apply_pallete(Assets.ENEMY_SPRITES[name]["Blue"][sheet_name], entity_pallete[color], "list")
            else:
                images = apply_pallete(Assets.ENEMY_SPRITES[name]["Blue"][sheet_name][index], entity_pallete[color])
        else:
            if index == "none":
                images = Assets.ENEMY_SPRITES[name]["Blue"][sheet_name]
            else:
                images = Assets.ENEMY_SPRITES[name]["Blue"][sheet_name][index]
        
        CACHED_ENTITY_IMAGES[(key, color)] = images

    return CACHED_ENTITY_IMAGES[(key, color)]


# CACHE IMAGES
def cache_img(size, color=(0, 0, 0, 0), clear=False, alpha=True, fill=True, assets=False):
    if (size, color) not in CACHED_IMAGES:
        if assets:
            type_, size_, width, height, perspective = size
            if ("stone" in type_ or "grass" in type_ or "brick" in type_) and find_last(type_, "_") != -1:
                    last = find_last(type_, "_")
                    i = type_[last+1:]
                    try:
                        image = apply_pallete(Assets.blocks[type_.replace("_" + i, "")][size_], block_pallete[type_[:5]][i])
                    except KeyError:
                        image = Assets.blocks[type_][size_]
                    surf = pygame.transform.scale(image, (width, height))
            
            else:
                surf = pygame.transform.scale(Assets.blocks[type_][size_], (width, height))
            
            if perspective == "back":
                surf.set_alpha(150)
        
        else:
            surf = pygame.Surface(size, pygame.SRCALPHA)
        
        if fill:
            surf.fill(color)

        CACHED_IMAGES[(size, color)] = surf

    elif clear:
        CACHED_IMAGES[(size, color)].fill(color)

    return CACHED_IMAGES[(size, color)]


# CACHE RECTS
def cached_rect(size, from_surf=None):
    key = size if not from_surf else (size, from_surf.get_rect().size)
    if key not in CACHED_RECTS['other']:
        CACHED_RECTS['other'][key] = from_surf.get_rect()

    return CACHED_RECTS['other'][key]

def parallax_bg(window, WIDTH, HEIGHT, bg_particles, master_clock, threshold=200, height=0, parallax_color=(0,20, 9), bg_color=(60, 0, 0)):
    # PARALLAX BACKGROUND
    parallax = random.random()
    if parallax > 0.9:
        bg_particles.append(
            [[random.random() * WIDTH, random.random() * HEIGHT - height * parallax], parallax,
             random.randint(1, 10),
             random.random() * 1 + 1, [0, random.uniform(-1, 1), random.uniform(-1, 1)],
             random.choice([parallax_color, bg_color])])

    for i, p in sorted(enumerate(bg_particles), reverse=True):
        # Reduce size
        size = p[2]
        p[2] -= 0.01

        # Move around
        p[0][1] += p[4][2]
        p[0][0] += p[4][1]

        # Timer
        p[4][0] += 1

        if size < 1:
            window.set_at((int(p[0][0]), int(p[0][1] + height * p[1])), bg_color)
        else:
            if p[4][0] > 60:
                p[4][1] = random.uniform(-1, 1)
                p[4][2] = random.uniform(-0.1, 1)
                p[4][0] = 0

        r1 = int(9 + math.sin((master_clock * random.uniform(1.2, 2)) / 40) * 3) 
        r2 = int(5 + math.sin((master_clock * random.uniform(1, 2)) / 30) * 2)

        window.blit(glow_img(r1, (12, 8, 2)), (p[0][0] - r1 - 1, p[0][1] + height - r1 - 2),
                    special_flags=pygame.BLEND_RGBA_ADD)
        window.blit(glow_img(r2, (24, 16, 3)), (p[0][0] - r2 - 1, p[0][1] + height - r2 - 2),
                    special_flags=pygame.BLEND_RGBA_ADD)

        window.set_at((int(p[0][0]), int(p[0][1] + height)), (255, 255, 255))

        if size < 0:
            bg_particles.pop(i)

    if len(bg_particles) > threshold:
        bg_particles = bg_particles[-threshold:]
    
    return bg_particles
    

# Minimap overlay
def draw_minimap(surface, player, all_players, radius=500, size=(120, 120), map={}):
    minimap = cache_img(size, (20, 20, 20), clear=True)
    
    center = pygame.Vector2(size[0] // 2, size[1] // 2)
    scale = size[0] / (2 * radius)

    for block in PHYSICS.get_objects(map, player.rect, radius):
        offset = pygame.Vector2(block.rect.center) - pygame.Vector2(player.rect.center)
        distance = offset.length()

        if distance <= radius:
            # Inside radar range — draw dot
            scaled = offset * scale
            dot_pos = center + scaled
            pygame.draw.rect(minimap, (50, 50, 50), (int(dot_pos.x), int(dot_pos.y), 8, 8))
        
    
    for p in all_players:
        if p == player or p.dead or p.death:
            continue
        offset = pygame.Vector2(p.rect.center) - pygame.Vector2(player.rect.center)
        distance = offset.length()

        if distance <= radius:
            # Inside radar range — draw dot
            scaled = offset * scale
            dot_pos = center + scaled
            pygame.draw.circle(minimap, p.color, (int(dot_pos.x), int(dot_pos.y)), 4)
        else:
            # Outside radar — draw directional arrow
            direction = offset.normalize()
            edge_pos = center + direction * (size[0] // 2 - 8)

            # Arrow shape
            angle = math.atan2(direction.y, direction.x)
            arrow = [
                (edge_pos.x + math.cos(angle) * 6, edge_pos.y + math.sin(angle) * 6),
                (edge_pos.x + math.cos(angle + 2.5) * 6, edge_pos.y + math.sin(angle + 2.5) * 6),
                (edge_pos.x + math.cos(angle - 2.5) * 6, edge_pos.y + math.sin(angle - 2.5) * 6),
            ]
            pygame.draw.polygon(minimap, p.color, arrow)

    # Draw self at center
    pygame.draw.circle(minimap, player.color, center, 5)

    pygame.draw.rect(minimap, (200, 200, 200), minimap.get_rect(), 1)
    surface.blit(minimap, (surface.get_width() - size[0] - 10, 10))

# Grouping world into chunks

def create_chunks(map, minx, miny, maxx, maxy, chunk_w=6, chunk_h=6, clear_chunks=False, overlap=True):
    if clear_chunks:
        map = {}
    
    """if map:
        return map
    """
    height = miny
    for h in range(chunk_h):
        width = minx
        for w in range(chunk_w):
            size = abs(maxx - minx) // chunk_w, abs(maxy - miny) // chunk_h
            rect = (width, height, size[0], size[1])
            # print(rect)
            width += size[0]
            rect_ = pygame.Rect(rect)
            if overlap:
                rect_ = rect_.inflate(128, 128)
                rect_.x -= 64
                rect_.y -= 64
            map[rect] = [rect_, []]

        height += size[1]

    return map

def map_chunks(map, objects, minx, miny, maxx, maxy, chunk_w=6, chunk_h=6, clear_chunks=False, grid=False, overlap=True):
    map = create_chunks(map, minx, miny, maxx, maxy, chunk_w, chunk_h, clear_chunks, overlap)

    for object_ in objects:
        if getattr(object_, "type", None) == "moving_platform":
            continue
        for pos, obs in map.items():
            if grid:
                if obs[0].colliderect(object_[0]):
                    map[pos][1].append(object_)
            else:
                if obs[0].colliderect(object_.rect):
                    map[pos][1].append(object_)
    
    return map

def calculate_viewports(self, n):
    sw, sh = Settings.WIDTH, Settings.HEIGHT
    if n == 1:
        return [(0, 0, sw, sh)]
    elif n == 2:
        return [(0, 0, sw // 2, sh), (sw // 2, 0, sw // 2, sh)]
    else:
        return [
                   (0, 0, sw // 2, sh // 2), (sw // 2, 0, sw // 2, sh // 2),
                   (0, sh // 2, sw // 2, sh // 2), (sw // 2, sh // 2, sw // 2, sh // 2)
               ][:n]


def refresh_joysticks(self):
    self.active_joys = []
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        j.rumble(0.5, 0.9, 5)
        jid = j.get_id()
        self.active_joys.append(j)

def player_settings(self, player):
    mouse_pos = self.mouse_pos
    
    players = self.players_config
    id_ = player.id
    menu = players[id_]['menu']
    
    for event in self.events:
        if player.control_type == "joystick":
            if event.type == pygame.JOYAXISMOTION:
                if event.joy == player.joystick_id:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                
            if event.type == pygame.JOYBUTTONDOWN:
                if event.joy == player.joystick_id:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
            
        else:
            if event.type == pygame.KEYDOWN:
                menu.handle_key(event.key, player.keyboard_num)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            menu.handle_mouse(event, player.viewport.topleft,
                                                    player.keyboard_num)

        self.player_settings_manager(event)

    # DRAW
    if True:
        player = players[id_]['player']
        if players[id_]['player_color_num'] > len(player.player_colors) - 1:
            players[id_]['player_color_num'] = 0

        if players[id_]['player_type_num'] > len(player.player_types) - 1:
            players[id_]['player_type_num'] = 0

        players[id_]['player_type'] = player.player_types[players[id_]['player_type_num']]

        try:
            players[id_]['player_color'] = player.player_colors[players[id_]['player_color_num']]
        except Exception as e:
            print(e)
        
        sprites = cache_assets((players[id_]['player_type'], players[id_]['player_color'], 'idle_right'))
        self.sprite_index = (self.animation_count //
                                3) % len(sprites)
        self.sprite = pygame.transform.scale(sprites[self.sprite_index], players[id_]['display_rect'].size)
        self.animation_count += 1

        players[id_]['window'].blit(self.sprite, players[id_]['display_rect'].topleft)

        players[id_]['menu'].update(mouse_pos, player.viewport.topleft)
        players[id_]['menu'].draw()
        
                
# Function to draw text on the screen
def draw_text(surface, text, position, font, color):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)


# Rotating images from the center    
def blit_rotate_center(win, image, top_left, angle, offset_x=0, offset_y=0):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    pygame.draw.rect(win, (2, 2, 2), (new_rect.topleft[0], new_rect.topleft[1], 10, 10))
    win.blit(rotated_image, (new_rect.topleft[0] - offset_x, new_rect.topleft[1] - offset_y))


# Text ------------------------------------------------------- #
def get_text_width(text, spacing):
    width = 0
    for char in text:
        if char in Settings.font_dat:
            width += Settings.font_dat[char][0] + spacing
        elif char == ' ':
            width += Settings.font_dat['A'][0] + spacing
    return width


# BLOCK PICKER

def get_block(type_="stone_2", size='big', width=None, height=None, perspective="fore"):
    # type_ = random.choice(['rock_1', 'grass_1', 'rock_2', 'grass_2', 'rock_3', 'grass_3', 'sand', 'mud', 'ice'])
    # size = random.choice(['big', 'small'])

    if not width and not height and size == 'big':
        width, height = (64, 64)

    if not width and not height and size == 'small':
        width, height = (32, 32)

    key = (type_, size, width, height, perspective)
    return cache_img(key, fill=False, assets=True)
    # return Assets.blocks[type_][size]


def draw_vertical_gradient(start_color, end_color, window, HEIGHT, WIDTH):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        pygame.draw.line(window, (r, g, b), (0, y), (WIDTH, y))


def get_dynamic_color(time_offset=0):
    # Create smooth RGB cycling using sine wave functions
    r = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.001 + time_offset))
    g = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.001 + 2 + time_offset))
    b = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.001 + 4 + time_offset))
    return r, g, b


# --- Particle Effect ---
class Particle:
    def __init__(self, pos):
        self.pos = list(pos)
        self.vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.life = 30

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, (255, 255, 100), (int(self.pos[0]), int(self.pos[1])), 3)


# --- RPG Button ---
class RPGButton:
    def __init__(self, text, font, screen, rel_rect, callback=None, args=None):
        self.text = text
        self.args = args
        self.font = font
        self.screen = screen
        self.callback = callback

        sw, sh = screen.get_size()
        self.target_rect = pygame.Rect(
            int(rel_rect[0] * sw),
            int(rel_rect[1] * sh),
            int(rel_rect[2] * sw),
            int(rel_rect[3] * sh)
        )

        self.rect = self.target_rect.copy()
        self.rect.x -= sw
        
        self.glow_color = (255, 255, 100, 100)
        self.color = (90, 50, 40)

        self.alpha = 0
        self.fade_speed = 5
        self.slide_speed = 20
        self.selected = False
        self.hovered = False
        self.pulse_time = 0
        self.visible = False

    def update(self, mouse_pos, pos=(0, 0)):
        rect = self.rect.copy()
        rect.x += pos[0]
        rect.y += pos[1]
        self.hovered = rect.collidepoint(mouse_pos)
        self.pulse_time += 0.05

        if self.rect.x < self.target_rect.x:
            self.rect.x += self.slide_speed
        else:
            self.rect.x = self.target_rect.x

        if not self.visible:
            if self.alpha < 255:
                self.alpha += self.fade_speed
            else:
                self.alpha = 255
                self.visible = True

    def draw(self):
        scale = 1 + 0.05 * math.sin(self.pulse_time * 2) if self.selected else 1
        scaled_rect = self.rect.inflate(self.rect.width * (scale - 1), self.rect.height * (scale - 1))

        if self.selected or self.hovered:
            glow = cache_img((scaled_rect.width + 10, scaled_rect.height + 10), alpha=True, fill=False)
            pygame.draw.rect(glow, self.glow_color, cached_rect(scaled_rect.size, from_surf=glow),
                             border_radius=12)
            self.screen.blit(glow, (scaled_rect.x - 5, scaled_rect.y - 5))

        button_surf = cache_img(scaled_rect.size, alpha=True, fill=False)
        pygame.draw.rect(button_surf, self.color + (self.alpha,), cached_rect(scaled_rect.size, from_surf=button_surf),
                         border_radius=8)
        self.screen.blit(button_surf, scaled_rect.topleft)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        self.screen.blit(text_surf, text_rect)

    def press(self):
        if self.callback:
            if self.args:
                self.callback(*self.args)
            else:
                self.callback()


# --- RPG Menu ---
class RPGMenu:
    def __init__(self, screen, font, button_data, layout):
        self.screen = screen
        self.font = font
        self.buttons = []
        self.selected_index = 0
        self.particles = []
        self.excluded = {}
        self.add(button_data, layout)
        
        if not self.buttons:
            return
        
        self.buttons[self.selected_index].selected = True

    def add(self, button_data, layout):
        for i, ((text, callback, args), rel_rect) in enumerate(zip(button_data, layout)):
            btn = RPGButton(text, self.font, self.screen, rel_rect, callback, args=args)
            self.buttons.append(btn)

    def exclude(self, btns):
        if isinstance(btns, list):
            for btn_dat in btns:
                id_, pass_ = btn_dat
                if id_ not in self.excluded:
                    if pass_:
                        btn = self.buttons[id_]
                        self.excluded[id_] = (self.buttons.index(btn), btn)
                else:
                    if not pass_:
                        del self.excluded[id_]
                    
        else:
            id_, pass_ = btns
            if id_ not in self.excluded:
                if pass_:
                    btn = self.buttons[id_]
                    self.excluded[id_] = (self.buttons.index(btn), btn)
            else:
                if not pass_:
                    del self.excluded[id_]
                
                        
    def update(self, mouse_pos, pos=(0, 0)):
        for i, btn in enumerate(self.buttons):
            if (i, btn) in self.excluded.values():
                continue
            btn.update(mouse_pos, pos)
            if btn.hovered:
                self.buttons[self.selected_index].selected = False
                self.selected_index = i
                btn.selected = True

        for p in self.particles:
            p.update()

        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self):
        for p in self.particles:
            p.draw(self.screen)
        
        for index, btn in enumerate(self.buttons):
            if (index, btn) in self.excluded.values():
                continue
            btn.draw()

    def handle_dir(self, right=False, left=False, top=False, bottom=False):
        selected = self.buttons[self.selected_index]
        near = self.selected_index
        min_ = float('inf')
        min_2 = float('inf')
        for i, btn in enumerate(self.buttons):
            if i in self.excluded.keys():
                btn.selected = False
                continue
            if btn == selected:
                continue
            
            # If pressed right
            if right:
                if btn.rect.x > selected.rect.x:
                    current_min = abs(distance(selected.rect.right, selected.rect.y, btn.rect.x, btn.rect.y))
                    if current_min < min_:
                        min_ = current_min
                        near = i

            # If pressed left
            elif left:
                if btn.rect.x < selected.rect.x:
                    current_min = abs(distance(selected.rect.x, selected.rect.y, btn.rect.right, btn.rect.y))
                    if current_min < min_:
                        min_ = current_min
                        near = i

            # If pressed bottom
            elif bottom:
                if btn.rect.y > selected.rect.y:
                    current_min = abs(distance(selected.rect.bottom, selected.rect.y, btn.rect.x, btn.rect.x))
                    if current_min < min_:
                        min_ = current_min
                        near = i
            
            # If pressed top
            elif top:
                if btn.rect.y < selected.rect.y:
                    current_min = abs(distance(selected.rect.x, selected.rect.y, btn.rect.x, btn.rect.bottom))
                    if current_min < min_:
                        min_ = current_min
                        near = i

        self.selected_index = near
        
    def handle_joy(self, event, type_="button"):
        if not self.buttons or len(self.excluded.keys()) == len(self.buttons):
            return  
        self.buttons[self.selected_index].selected = False
        
        if type_ == "axis":
            top = int(event.value) < -0.75 and event.axis == 1
            bottom = round(event.value) > 0.75 and event.axis == 1
            left = int(event.value) < -0.75 and event.axis == 0
            right = round(event.value) > 0.75 and event.axis == 0
            
            self.handle_dir(right, left, top, bottom)
                    
        if type_ == "button":
            if event.button == 2:
                self.buttons[self.selected_index].press()
                self.spawn_particles(self.buttons[self.selected_index].rect.center)

        self.buttons[self.selected_index].selected = True
            
    def handle_key(self, key, id_='None'):
        if not self.buttons or len(self.excluded.keys()) == len(self.buttons):
            return  
        
        self.buttons[self.selected_index].selected = False
        
        bottom = (key == pygame.K_DOWN and id_ == 0) or (key == pygame.K_s and id_ == 1) or (
                (key == pygame.K_DOWN or key == pygame.K_s) and id_ == 'None')
        
        top = (key == pygame.K_UP and id_ == 0) or (key == pygame.K_w and id_ == 1) or (
                (key == pygame.K_UP or key == pygame.K_w) and id_ == 'None')
        
        right = (key == pygame.K_RIGHT and id_ == 0) or (key == pygame.K_d and id_ == 1) or (
                (key == pygame.K_RIGHT or key == pygame.K_d) and id_ == 'None')
        
        left = (key == pygame.K_LEFT and id_ == 0) or (key == pygame.K_a and id_ == 1) or (
                (key == pygame.K_LEFT or key == pygame.K_a) and id_ == 'None')
        
        self.handle_dir(right, left, top, bottom)

        if (key == pygame.K_RETURN and id_ == 0) or (key == pygame.K_f and id_ == 1) or (
                (key == pygame.K_RETURN or key == pygame.K_f) and id_ == 'None'):
            self.buttons[self.selected_index].press()
            self.spawn_particles(self.buttons[self.selected_index].rect.center)
        
        self.buttons[self.selected_index].selected = True

    def handle_mouse(self, event, pos=(0, 0), id_=0):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for index, btn in enumerate(self.buttons):
                if (index, btn) in self.excluded.values():
                    continue
                # THIS IS FOR SPLIT SCREENS (CHANGING TOPLEFT VALUE)
                rect = btn.rect.copy()
                rect.x += pos[0]
                rect.y += pos[1]
                if rect.collidepoint(event.pos):
                    btn.press()
                    self.spawn_particles(btn.rect.center)

    def spawn_particles(self, center):
        for _ in range(20):
            self.particles.append(Particle(center))


class My_Text:
    def __init__(self, text=None, x=None, y=None):
        self.text = 'WHOOKID' if not text else text
        self.initialize(x, y)
        self.offset_x = 0
        self.offset_y = 10

        self.update()
        # Title animation
        self.glow_alpha = 0
        self.animation_speed = 2  # animation speed
        self.glow_max = 100
        self.glow_min = 0
        self.alpha_direction = 1

    def initialize(self, x=None, y=None):
        self.x = Settings.WIDTH // 2 if not x else x
        self.y = 10 if not y else y

    def update(self):
        self.title_surface = Settings.FONT.render(self.text, True, Settings.WHITE)
        self.rect = self.title_surface.get_rect(topleft=(self.x, self.y))

    def draw(self):
        bg_color = get_dynamic_color(-50)

        self.glow_alpha += self.alpha_direction * self.animation_speed
        if self.glow_alpha >= self.glow_max or self.glow_alpha <= self.glow_min:
            self.alpha_direction *= -1

        # Render glowing title
        title_surface = Settings.FONT.render(self.text, True, Settings.WHITE)
        glow_surface = Settings.FONT.render(self.text, True, bg_color)
        glow_surface.set_alpha(self.glow_alpha)
        Settings.window.blit(glow_surface, (self.x - glow_surface.get_width() // 2, self.y + self.offset_y))
        Settings.window.blit(title_surface, (self.x - title_surface.get_width() // 2, self.y))


class TypeText:
    def __init__(self, text, pos, font, color=(255, 255, 255), speed=50):
        self.full_text = text
        self.current_text = ""
        self.font = font
        self.color = color
        self.pos = pos
        self.speed = speed  # characters per second

        self.index = 0
        self.start_time = time.time()
        self.done = False

    def update(self):
        if self.done:
            return

        elapsed = time.time() - self.start_time
        chars_to_show = int(elapsed * self.speed)

        if chars_to_show >= len(self.full_text):
            self.current_text = self.full_text
            self.done = True
        else:
            self.current_text = self.full_text[:chars_to_show]

    def draw(self, surface, infinite=False):
        if self.done and not infinite:
            return
        lines = self.current_text.split('\n')
        y_offset = 0
        for line in lines:
            rendered_line = self.font.render(line, True, self.color)
            surface.blit(rendered_line, (self.pos[0], self.pos[1] + y_offset))
            y_offset += self.font.get_height()

    def skip(self):
        self.current_text = self.full_text
        self.done = True


# VOLUME SYS CLASS
class Volumes(Settings):
    def __init__(self, volumes, game):
        self.game = game
        self.volumes = volumes
        self.selected = None
        self.name = "volume"
        self.initialize()

    def initialize(self):
        pass

    def main(self):

        # Main loop
        running = True

        try:
            self.selected = self.volumes[0]
        except Exception as e:
            print(e)
        clicked = False

        font = pygame.font.SysFont("serif", 36)

        def back_(object_):
            print("Quit Game Settings!")
            object_.volume_settings_window = False
            object_.selected = None

        button_data = [
            ("Back", back_, [self])
        ]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)
        ]

        menu = RPGMenu(self.game.window, font, button_data, layout)
        self.volume_settings_window = True

        self.pulse_time = 0

        while self.volume_settings_window:
            self.game.fix_orientation()

            try:
                if self.selected.mode == 'In Game':
                    Settings.IN_GAME_SOUNDS_VOLUME = self.selected.volume
                elif self.selected.mode == 'Background':
                    Settings.BG_SOUNDS_VOLUME = self.selected.volume
                    self.selected.sounds[0].set_volume(self.selected.volume)

            except Exception as e:
                print(e)

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break

                elif event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)
                    if event.button == 1:
                        clicked = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        clicked = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the mute/unmute button is clicked
                    for volume in self.volumes:
                        if volume.button_rect.collidepoint(event.pos):
                            volume.is_muted = not volume.is_muted
                            self.selected = volume
                            volume.dragging = False
                        else:
                            volume.dragging = True

                elif event.type == pygame.MOUSEMOTION and clicked:
                    x_vel = event.rel[0] / 10
                    for volume in self.volumes:

                        if volume.slider_rect.collidepoint(event.pos):
                            if volume.dragging:  # Update the handle position based on mouse movement
                                self.selected = volume

                                if volume.handle_x + x_vel < volume.slider_rect.right and x_vel > 0:
                                    volume.handle_x += x_vel
                                elif volume.handle_x + x_vel > volume.slider_rect.left and x_vel < 0:
                                    volume.handle_x += x_vel

                                volume.volume = abs(
                                    round((volume.slider_rect.x - volume.handle_x) / volume.slider_rect.width, 2))
                        else:
                            try:

                                if self.selected.handle_x + x_vel < self.selected.slider_rect.right and x_vel > 0:
                                    self.selected.handle_x += x_vel
                                elif self.selected.handle_x + x_vel > self.selected.slider_rect.left and x_vel < 0:
                                    self.selected.handle_x += x_vel

                                self.selected.volume = abs(round((
                                                                         self.selected.slider_rect.x - self.selected.handle_x) / self.selected.slider_rect.width,
                                                                 2))
                            except Exception as e:
                                print(e)

            dt = self.game.clock.tick(self.game.FPS)
            self.pulse_time += 0.005 * dt

            self.window.fill(Settings.DARK_BG)

            menu.update(mouse_pos)
            menu.draw()

            if self.selected:
                scale = 1 + 0.05 * math.sin(self.pulse_time * 2) if self.selected else 1
                scaled_rect = self.selected.slider_rect.inflate(self.selected.slider_rect.width * (scale - 1),
                                                                self.selected.slider_rect.height * (scale - 1)).inflate(
                    32, 0)

                glow = cache_img((scaled_rect.width + 10, scaled_rect.height + 10))
                pygame.draw.rect(glow, (255, 255, 100, 120), glow.get_rect(), border_radius=20)
                self.window.blit(glow, (scaled_rect.x - 5, scaled_rect.y - 5))

            for volume in self.volumes:
                if volume.is_muted:
                    volume.handle_x = volume.slider_rect.left
                    volume.volume = 0

                # Draw the slider
                pygame.draw.rect(self.window, (50, 50, 50
                                               ), volume.slider_rect.inflate(32, 0), border_radius=20)
                pygame.draw.circle(self.window, self.BLUE if not volume.is_muted else self.RED,
                                   (volume.handle_x, volume.slider_y + volume.slider_height // 2), volume.handle_radius)

                # Draw the mute/unmute button
                volume.button_color = self.RED if volume.is_muted else self.BLUE
                pygame.draw.rect(self.window, volume.button_color, volume.button_rect, border_radius=20)

                volume.button_text = Settings.menu_font.render("Mute" if not volume.is_muted else "Unmute", True,
                                                               self.WHITE)
                text_rect = volume.button_text.get_rect(center=volume.button_rect.center)
                self.window.blit(volume.button_text, text_rect)

                # Display the volume percentage
                volume_text = Settings.menu_font.render(f"{volume.mode} — {round(volume.volume * 100, 2)}%", True,
                                                        (70, 70, 70))
                self.window.blit(volume_text, (volume.slider_x, volume.slider_y - 40))

            # Update the display
            pygame.display.flip()


# VOLUME CLASS

class Volume:
    def __init__(self, x=0, y=0, sound=None, sounds=None):
        if sounds is None:
            sounds = [Assets.SOUNDS['theme']]
        self.settings = Settings()
        self.sounds = sounds
        self.mode = sound
        self.initialise_volume(x, y)

    def initialise_volume(self, x, y):
        self.x = x
        self.y = y

        # Volume settings
        self.volume = 0.5  # Default volume (50%)
        self.is_muted = False
        self.dragging = False

        # Slider properties
        self.slider_width = 300
        self.slider_height = 30

        self.handle_radius = 15

        # Button properties
        self.button_width = 100
        self.button_height = 50

        self.initialize()

    def initialize(self):
        # Slider properties
        self.slider_x = (self.settings.WIDTH - self.slider_width) // 2 + self.x
        self.slider_y = self.settings.HEIGHT // 2 + self.y
        self.slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)

        self.handle_x = self.slider_x + int(self.volume * self.slider_width)

        # Button properties
        self.button_x = (self.settings.WIDTH - self.button_width) // 2 + self.x
        self.button_y = self.settings.HEIGHT // 2 + 60 + self.y
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)


# SOUNDS 

class Sounds:
    def __init__(self, player, degree=1):
        self.protagonist = player
        self.degree = degree
        self.bg_volume = 0.5
        self.bg_degree = 1

    def play_bg(self, sound, loop=None):
        if loop == -1:
            Assets.SOUNDS[sound].set_volume(Settings.BG_SOUNDS_VOLUME)
            Assets.SOUNDS[sound].play(loop)
            return

        Assets.SOUNDS[sound].set_volume(Settings.BG_SOUNDS_VOLUME)
        Assets.SOUNDS[sound].play()

    def stop(self, sound):
        Assets.SOUNDS[sound].stop()

    def get_volume(self, enemy):
        the_distance = abs(distance(self.protagonist.rect.x, self.protagonist.rect.y, enemy.rect.x, enemy.rect.y))
        max_distance = Settings.WIDTH
        volume = max(0, 1 - the_distance / (max_distance / 2))
        return volume


class UIButton:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color

    def draw(self, surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(
            text_surf,
            (self.rect.centerx - text_surf.get_width() // 2,
             self.rect.centery - text_surf.get_height() // 2)
        )

    def is_clicked(self, mouse_pos, events):
        if self.rect.collidepoint(mouse_pos):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                    return True
        return False