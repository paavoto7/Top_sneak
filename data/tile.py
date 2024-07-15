

import pygame


class Wall(pygame.sprite.Sprite):
    """Represents the boundaries of the playable area.
    Created as sprites for the ease of collision detection."""
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)


class Goal(pygame.sprite.Sprite):
    """Marks the end of the level"""
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)
