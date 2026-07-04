import pygame
import game.main as game
from game import settings as _settings
print("Pixel Abyss version", _settings.VERSION)

level = 5

if __name__ == "__main__":
    game.Game(level).start()
