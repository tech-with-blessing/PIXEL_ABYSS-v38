import pygame
import sys
from os import chdir
from pathlib import Path

from .data import text

# Versioning: read VERSION file at repo root
ROOT = Path(__file__).resolve().parents[1]
VERSION = '38.0.0'

if getattr(sys, 'frozen', False):
    chdir(sys._MEIPASS)


pygame.init()

# Initialize joystick
pygame.joystick.init()


class Settings:
    pygame.display.set_caption("PIXEL ABYSS")

    WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h

    if WIDTH > HEIGHT:
        orientation = 'landscape'
    else:
        orientation = 'portrait'

    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF, pygame.RESIZABLE)

    # Fonts
    font_size = 30
    font = pygame.font.Font(None, font_size)
    menu_font = pygame.font.SysFont("impact", 30)
    _font = pygame.font.SysFont("impact", 20)
    health_font = pygame.font.Font(None, 20)
    display_font = pygame.font.Font(None, 50)
    FONT = pygame.font.SysFont("consolas", 48)
    SMALL_FONT = pygame.font.SysFont("consolas", 32)

    font_dat = {'A': [3], 'B': [3], 'C': [3], 'D': [3], 'E': [3], 'F': [3], 'G': [3], 'H': [3], 'I': [3], 'J': [3],
                'K': [3], 'L': [3], 'M': [5], 'N': [3], 'O': [3], 'P': [3], 'Q': [3], 'R': [3], 'S': [3], 'T': [3],
                'U': [3], 'V': [3], 'W': [5], 'X': [3], 'Y': [3], 'Z': [3],
                'a': [3], 'b': [3], 'c': [3], 'd': [3], 'e': [3], 'f': [3], 'g': [3], 'h': [3], 'i': [1], 'j': [2],
                'k': [3], 'l': [3], 'm': [5], 'n': [3], 'o': [3], 'p': [3], 'q': [3], 'r': [2], 's': [3], 't': [3],
                'u': [3], 'v': [3], 'w': [5], 'x': [3], 'y': [3], 'z': [3],
                '.': [1], '-': [3], ',': [2], ':': [1], '+': [3], '\'': [1], '!': [1], '?': [3],
                '0': [3], '1': [3], '2': [3], '3': [3], '4': [3], '5': [3], '6': [3], '7': [3], '8': [3], '9': [3],
                '(': [2], ')': [2], '/': [3], '_': [5], '=': [3], '\\': [3], '[': [2], ']': [2], '*': [3], '"': [3],
                '<': [3], '>': [3], ';': [1]}
    font_ = text.generate_font('data/font/small_font.png', font_dat, 5, 8, (248, 248, 248))
    font_2 = text.generate_font('data/font/small_font.png', font_dat, 5, 8, (112, 240, 77))

    FPS = 60
    GRAVITY = 800

    BG_SOUNDS_VOLUME = 0
    IN_GAME_SOUNDS_VOLUME = 0.1

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 100, 0)
    PURPLE = (255, 0, 255)
    GREEN = (0, 255, 0)
    DARK_BG = (15, 15, 25)
    SKY_BLUE = (135, 206, 235)    
    BG_COLOR = (10, 10, 10)
    PARALLAX = (22, 19, 40)
    
    clock = pygame.time.Clock()
