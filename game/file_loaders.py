import pygame
import sys
from os import listdir, chdir
from os.path import isfile, join

if getattr(sys, 'frozen', False):
    chdir(sys._MEIPASS)

# IMAGE FLIPPER
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# MUSIC LOADER
def load_sounds(dir1):
    path = join("assets", dir1)
    sounds = [f for f in listdir(path) if isfile(join(path, f))]

    all_sounds = {}
    try:
        for snd in sounds:
            sound = pygame.mixer.Sound(join(path, snd))
            all_sounds[snd.replace(".wav", "")] = sound
    except Exception as e:
        print(e)

    return all_sounds


# IMAGE LOADER
def load_sprite_sheets(dir1, dir2=None, width=10, height=10, direction=False, sheet=True):
    if not dir1:
        path = 'assets'
    elif dir2 is not None:
        path = join("assets", dir1, dir2)
    else:
        path = join("assets", dir1)

    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            if not sheet:
                sprites = sprite_sheet
                break

            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            if "Explosion" in dir2:
                sprites.append(surface)
            else:
                sprites.append(surface)

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


# IMAGE LOADER 2
def load_sprite_sheets2(dir1, dir2=None, width=10, height=10, direction=False, sheet=True, expand_width=None,
                        expand_height=None):
    if dir2 is not None:
        path = join("assets", dir1, dir2)
    else:
        path = join("assets", dir1)

    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            if not sheet:
                sprites = sprite_sheet if not expand_width and not expand_height else pygame.transform.scale(
                    sprite_sheet, (expand_width, expand_height))

                break

            trimarea = (i * width, 0, width, height)
            surface = sprite_sheet.subsurface(trimarea)
            sprites.append(surface if not expand_width and not expand_height else pygame.transform.scale(surface, (
                expand_width, expand_height)))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites
