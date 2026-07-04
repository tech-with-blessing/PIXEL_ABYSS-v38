import pygame
import random
import math

# Initialise the module
pygame.init()

DISPLAY_SIZE = (1000, 700)
# Set display
WIDTH, HEIGHT = DISPLAY_SIZE
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption("Name of your game here")
pygame.mouse.set_visible(False)

# Constants
BG_COLOR = (0, 1, 4)
PARALLAX = (2, 1, 4)
FPS = 60  # Frames per second

GLOW_CACHE = {}


def glow_img(size, color):
    if (size, color) not in GLOW_CACHE:
        surf = pygame.Surface((size * 2 + 2, size * 2 + 2))
        pygame.draw.circle(surf, color, (surf.get_width() // 2, surf.get_height() // 2), size)
        surf.set_colorkey((0, 0, 0))
        GLOW_CACHE[(size, color)] = surf
    return GLOW_CACHE[(size, color)]


# Game loop variables
running = True
clock = pygame.time.Clock()

bg_stars = []
master_clock = 0
height = 0


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

dt = 0
# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the Background
    window.fill(BG_COLOR)
    display = pygame.Surface(DISPLAY_SIZE, 0, 32)
    display.fill((33, 33, 33))
    master_clock += dt

    bg_stars = parallax_bg(window, WIDTH, HEIGHT, bg_stars, master_clock, threshold=10, height=0, parallax_color=PARALLAX, bg_color=BG_COLOR)
    # window.blit(display, (100, 100), special_flags=pygame.BLEND_RGBA_SUB)
    # Get and draw FPS
    font_size = 30
    font = pygame.font.Font(None, font_size)
    fps = clock.get_fps()
    fps_surface = font.render(f"FPS: {int(fps)} {len(bg_stars)}", True, (255, 255, 255))
    window.blit(fps_surface, (10, 10))

    pygame.display.flip()
    dt = clock.tick(FPS)  # The limit of frames per second

# Quit pygame    
pygame.quit()
