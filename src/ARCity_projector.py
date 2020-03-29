import pygame
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2hsv
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1920//2
SCREEN_HEIGHT = 1080//2

def classify_colours(colours):
    # -2 - corner
    # -1 - undefined
    #  0 - white
    #  1 - yellow
    #  2 - blue
    #  3 - purple
    #  4 - brown
    #  5 - green
    hsv = rgb2hsv(colours)
    h = hsv[:,:,0]
    s = hsv[:,:,1]
    v = hsv[:,:,2]
    categories = -1*ones_like(hsv,dtype=np.int)
    categories[v>0.8] = 1
    return categories

def generate_roads(world):
    resolution = 10 # pixels per LEGO stud
    im = np.zeros([world.shape[0]*resolution,world.shape[1]*resolution])
    return im

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # world = classify_colours(colours)
    world = np.array([
        [1,1,1,1,1,1,1],
        [1,2,2,1,3,3,1],
        [1,2,2,1,3,3,1],
        [1,1,1,1,1,1,1],
        [1,2,2,1,4,4,1],
        [1,2,2,1,4,4,1],
        [1,1,1,1,1,1,1],
        ])

    running = True
    while running:
        for event in pygame.event.get(): # Look at every event in the queue
            if event.type == KEYDOWN and event.key == K_ESCAPE: running = False
            elif event.type == QUIT: running = False

        # Fill the screen with white
        screen.fill((255, 255, 255))

        # Create a surface and pass in a tuple containing its length and width
        surf = pygame.Surface((50, 50))

        # Give the surface a color to separate it from the background
        surf.fill((0, 0, 0))
        rect = surf.get_rect()

        # This line says "Draw surf onto the screen at the center"
        screen.blit(surf, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        pygame.display.flip()
        # image = generate_roads(world)

if __name__ == '__main__':
    main()
