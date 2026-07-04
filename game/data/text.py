import pygame
from copy import deepcopy


def show_text(Text, x, y, Spacing, WidthLimit, Font, surface, double=1, overflow='normal'):
    Text += ' '
    if double == 2:
        x = int(x / 2)
        y = int(y / 2)
    original_x = x
    original_y = y
    current_word = ''
    if overflow == 'normal':
        for char in Text:
            if char not in [' ', '\n']:
                try:
                    image = Font[str(char)][1]
                    current_word += str(char)
                except KeyError:
                    pass
            else:
                word_total = 0
                for char2 in current_word:
                    word_total += Font[char2][0]
                    word_total += Spacing
                if word_total + x - original_x > WidthLimit:
                    x = original_x
                    y += Font['Height']
                for char2 in current_word:
                    image = Font[str(char2)][1]
                    surface.blit(
                        pygame.transform.scale(image, (image.get_width() * double, image.get_height() * double)),
                        (x * double, y * double))
                    x += Font[char2][0]
                    x += Spacing
                if char == ' ':
                    x += Font['A'][0]
                    x += Spacing
                else:
                    x = original_x
                    y += Font['Height']
                current_word = ''
            if x - original_x > WidthLimit:
                x = original_x
                y += Font['Height']
        return x, y
    if overflow == 'cut all':
        for char in Text:
            if char not in [' ', '\n']:
                try:
                    image = Font[str(char)][1]
                    surface.blit(
                        pygame.transform.scale(image, (image.get_width() * double, image.get_height() * double)),
                        (x * double, y * double))
                    x += Font[str(char)][0]
                    x += Spacing
                except KeyError:
                    pass
            else:
                if char == ' ':
                    x += Font['A'][0]
                    x += Spacing
                if char == '\n':
                    x = original_x
                    y += Font['Height']
                current_word = ''
            if x - original_x > WidthLimit:
                x = original_x
                y += Font['Height']
        return x, y


def generate_font(FontImage, FontSpacingMain, TileSize, TileSizeY, color):
    font_spacing = deepcopy(FontSpacingMain)
    font_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                  'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.', '-', ',', ':', '+', '\'', '!', '?',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')', '/', '_', '=', '\\', '[', ']', '*', '"',
                  '<', '>', ';']
    font_image = pygame.image.load(FontImage).convert()
    new_surf = pygame.Surface((font_image.get_width(), font_image.get_height())).convert()
    new_surf.fill(color)
    font_image.set_colorkey((0, 0, 0))
    new_surf.blit(font_image, (0, 0))
    font_image = new_surf.copy()
    font_image.set_colorkey((255, 255, 255))
    num = 0
    for char in font_order:
        font_image.set_clip(pygame.Rect(((TileSize + 1) * num), 0, TileSize, TileSizeY))
        character_image = font_image.subsurface(font_image.get_clip())
        font_spacing[char].append(character_image)
        num += 1
    font_spacing['Height'] = TileSizeY
    return font_spacing
