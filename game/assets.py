import os

from .file_loaders import *
from .calculate_class import get_total_size

# TRAPS
'''
TRAPS = dict()

names = listdir("assets/Traps/")
width = 32
height = 32
for trap in names:
    if trap == "Fan":
        width = 24
        height = 8
    elif trap == "Fire":
        width = 16
        height = 32
    elif trap == "Spikes":
         width = 16
        height = 16
    elif trap == "Trampoline":
        width = 28
        height = 28
    elif trap == "Falling_Platforms":
        width = 32
        height = 10
    elif trap == "Grey_Platform":
        width = 32
        height = 8
    elif trap == "Brown_Platform":
        width = 32
        height = 8

    TRAPS[trap] = load_sprite_sheets2("Traps", trap, width, height, False, True)
'''

# ENEMY SPRITES
def create_enemy_sprites():
    states = ['idle', 'run', 'attack_1', 'attack_2']
    names = listdir('assets/Enemies/')
    ENEMY_SPRITES = dict()
    ENEMY_RECT_SPRITES = dict()

    for name in names:
        ENEMY_SPRITES[name] = dict()

        colors = ["Blue"]
        states = ['idle', 'run', 'attack_1', 'attack_2']
        if name == 'Archer':
            states = [('idle_right', 'idle_left'), ('run_right', 'run_left'), ('attack_0', 'attack_0_2'),
                        ('attack_45', 'attack_315'), ('attack_90', 'attack_270'), ('attack_135', 'attack_225'),
                        ('attack_180', 'attack_180_2')]
        
        if name == "Warrior":
            w_ = 6
            h_ = 8
            s = 4
        elif name == "Pawn":
            w_ = 6
            h_ = 6
            s = 4
        elif name == "Torch":
            w_ = 7
            h_ = 5
            s = 3
        elif name == 'TNT':
            w_ = 7
            h_ = 3
            s = 3
        else:
            w_ = 8
            h_ = 7
            s = 7

        for color in colors:
            real_image = pygame.image.load(join('assets', 'Enemies', name, f"{name}.png"))
            ENEMY_SPRITES[name][color] = dict()

            width = real_image.get_width() / w_
            height = real_image.get_height() / h_
            w = 0
            for h, state in enumerate(states[:s]):
                if name == 'Archer':
                    ENEMY_SPRITES[name][color][state[0]] = list()
                    ENEMY_SPRITES[name][color][state[1]] = list()
                    
                else:
                    ENEMY_SPRITES[name][color][state + '_right'] = list()
                    ENEMY_SPRITES[name][color][state + '_left'] = list()

                sprites = list()
                rect_sprites = []

                for w in range(w_):
                    if (name == 'TNT' and w == 6 and h < 2) or (name == 'Torch' and w == 6 and h > 0) or (
                            name == 'Archer' and w > 5 and h < 2):
                        continue
                    try:
                        trimarea = (w * width, h * height, width, height)
                        sprite = real_image.subsurface(trimarea)

                        from_x = 0
                        from_y = 0

                        if name == 'Warrior':
                            from_x = 76
                            from_y = 67

                        elif name == 'Torch':
                            from_x = 76
                            from_y = 67

                        elif name == 'TNT':
                            from_x = 76
                            from_y = 67

                        elif name == 'Pawn':
                            from_x = 80
                            from_y = 70

                        elif name == 'Archer':
                            from_x = 75
                            from_y = 67

                        photo_width = 192
                        photo_height = 192

                        margin_distance_x = from_x * 2
                        margin_distance_y = from_y * 2

                        width_distance = photo_width - margin_distance_x
                        height_distance = photo_height - margin_distance_y

                        trimarea = (from_x, from_y, width_distance, height_distance)

                        try:
                            sprite_ = sprite.subsurface(trimarea)
                        except:
                            continue
                        rect_sprites.append(sprite_.convert_alpha())
                        sprites.append(sprite.convert_alpha())
                    except Exception as e:
                        print(e)

                if name == 'Archer':
                    ENEMY_SPRITES[name][color][state[0]] = sprites
                    ENEMY_SPRITES[name][color][state[1]] = flip(sprites)
                    
                    sprite = rect_sprites[0]
                    
                    if 'attack_' in state[0]:
                        image_key = (name, 'attack')
                    
                    else:
                        image_key = (name, state[0].replace('_right', '').replace('_left', ''))
                    
                    if image_key in ENEMY_RECT_SPRITES:
                        continue
                    
                    rect = sprite.get_rect(topleft=(0, 0))
                    mask = pygame.mask.from_surface(sprite)
                
                    ENEMY_RECT_SPRITES[image_key] = mask, rect.size

                else:
                    ENEMY_SPRITES[name][color][state + '_right'] = sprites
                    ENEMY_SPRITES[name][color][state + '_left'] = flip(sprites)
                    
                    sprite = rect_sprites[0]
                    image_key = (name, state)
                    
                    rect = sprite.get_rect(topleft=(0, 0))
                    mask = pygame.mask.from_surface(sprite)
                
                    ENEMY_RECT_SPRITES[image_key] = mask, rect.size

    return ENEMY_RECT_SPRITES, ENEMY_SPRITES

def trees():
    # TREE SPRITES
    states = ['idle', 'hit', 'chopped']
    TREE_SPRITES = dict()

    real_image = pygame.image.load(join('assets', 'Trees', "Tree.png")).convert_alpha()
    width = real_image.get_width() / 4
    height = real_image.get_height() / 3
    w = 0
    for h, state in enumerate(states):

        TREE_SPRITES[state + '_right'] = list()
        TREE_SPRITES[state + '_left'] = list()

        sprites = list()

        for w in range(3):
            if (state == 'hit' and w >= 2 and h == 1) or (state == 'chopped' and w >= 1 and h == 2):
                continue
            try:
                trimarea = (w * width, h * height, width, height)
                sprite = real_image.subsurface(trimarea)
                sprites.append(sprite)
            except Exception as e:
                print(e)

        TREE_SPRITES[state + '_left'] = flip(sprites)
        TREE_SPRITES[state + '_right'] = sprites

    return TREE_SPRITES

def arrows():
    # ARROW SPRITES
    ARROW_SPRITES = dict()
    states = ["full", "stuck"]
    real_image = pygame.image.load("assets/Weapons/Arrow/Arrow.png").convert_alpha()

    for h, state in enumerate(states):
        ARROW_SPRITES[f'{state}'] = list()
        ARROW_SPRITES[f'{state}'] = list()

        sprites = list()
        trimarea = (0, h * 64, 64, 64)
        sprite = real_image.subsurface(trimarea)
        sprites.append(sprite)

        ARROW_SPRITES[f'{state}'] = sprites

    return ARROW_SPRITES

def death():
    # DEATH SPRITES
    DEAD_SPRITES = dict()
    states = ["death", "sink"]
    real_image = pygame.image.load("assets/Dead/dead.png").convert_alpha()

    for h, state in enumerate(states):
        DEAD_SPRITES[f'{state}_right'] = list()
        DEAD_SPRITES[f'{state}_left'] = list()

        sprites = list()
        for w in range(7):
            trimarea = (w * 128, h * 128, 128, 128)
            sprite = real_image.subsurface(trimarea)
            from_x = 40
            from_y = 40
            photo_width = 128
            photo_height = 128

            margin_distance_x = from_x * 2
            margin_distance_y = from_y * 2

            width_distance = photo_width - margin_distance_x
            height_distance = photo_height - margin_distance_y

            trimarea = (from_x, from_y, width_distance, height_distance)

            try:
                sprite = sprite.subsurface(trimarea)
            except Exception as e:
                print(e)
                pass
            sprites.append(sprite)

        DEAD_SPRITES[f'{state}_left'] = flip(sprites)
        DEAD_SPRITES[f'{state}_right'] = sprites

    return DEAD_SPRITES

def blocks_assets():
    # LOAD BLOCKS
    blocks = {}

    width = 48
    height = 48
    path = join("assets", "Terrain", "Terrain2.png")
    image = pygame.image.load(path).convert()
    block_types2 = ['sand', 'mud', 'ice']
    block_sizes2 = ['big', 'small']

    for w, type in enumerate(block_types2):
        blocks[type] = dict()
        for h, size in enumerate(block_sizes2):
            the_width = 48
            the_height = 48
            if h == 1:
                the_width = 32
                the_height = 32
            trimarea = (w * width + (w * 16), h * height, the_width, the_height)
            sprite = image.subsurface(trimarea)
            if size == 'big':
                sprite = pygame.transform.scale(sprite, (64, 64)).convert()
            blocks[type][size] = sprite

    path = join("assets", "Terrain")
    for name in os.listdir(path):
        image_pth = join("assets", "Terrain", name)
        name = name.replace('.png', '')
        if name in ['Terrain', 'Terrain2']:
            continue
        if 'Long' in name:
            image = pygame.transform.scale(pygame.image.load(image_pth).convert(), (64, 128))
        else:
            if name == 'window':
                image = pygame.transform.scale(pygame.image.load(image_pth).convert_alpha(), (64, 64))
            else:
                image = pygame.image.load(image_pth).convert()
                if "small" in name:
                    image = pygame.transform.scale(image, (32, 32))
                else:
                    image = pygame.transform.scale(image, (64, 64))

        blocks[name] = dict()
        blocks[name]["big"] = image

    return blocks

class Assets:
    # LOAD MUSIC
    SOUNDS = load_sounds("SOUNDS")

    # DECO SPRITES
    DECO_SPRITES = load_sprite_sheets2("Deco", None, 32, 32, False, False)

    # GEM SPRITES
    GEM_SPRITES = load_sprite_sheets2("Items", "Gems", 16, 16, False, True, 32, 32)

    COLLECTED = load_sprite_sheets2("Items", None, 32, 32, False, True, 64, 64)

    # BOMB SPRITES
    BOMB_SPRITES = load_sprite_sheets2("Weapons", "Bomb", 64, 64, True)

    # EXPLOSION SPRITES
    EXPLOSION_SPRITES = load_sprite_sheets("Effects", "Explosion", 192, 192, True)

    # FIRE SPRITES
    FIRE_SPRITES = load_sprite_sheets("Effects", "Fire", 128, 128)

    # EXPRESSION SPRITES
    EXPRESSION_SPRITES = load_sprite_sheets2("Expressions", None, 4, 4, False, False, 15, 15)

    blocks = blocks_assets()
    block_types = [['stone_1', 'grass_1'], ['stone_2', 'grass_2'], ['stone_3', 'grass_3']]
    block_sizes = ['big', 'small']

    DEAD_SPRITES = death()
    ARROW_SPRITES = arrows()
    TREE_SPRITES = trees()
    ENEMY_RECT_SPRITES, ENEMY_SPRITES = create_enemy_sprites()

    TRAPS = {} # TRAPS

# print(get_total_size(Assets))