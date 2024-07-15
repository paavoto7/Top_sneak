from os import listdir

import pygame

FPS = 60
SCREEN_BOTTOM = 800
SCREEN_WIDTH = 896

images = {}

def image_loader():
    for imagename in listdir("./assets/images/"):
        images[imagename[0:-4]] = pygame.image.load(f"./assets/images/{imagename}").convert_alpha()

colours = {0: (0,0,0), 1: (211,211,211), 2: (80,80,80), 9:(200,0,0)}

guns = {
    #   [power, mag size, firerate in ms, spread, is automatic]
    "pistol": [30, 30, 500, 2, False],
    "auto_rifle": [75, 50, 100, 5, True],
    "shotgun": [50, 30, 1000, 10, False],
    "sniper": [100, 5, 1500, 0.5, False]
}
