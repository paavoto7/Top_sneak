import pygame
import csv

class Map:
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.map = self.load()
        self.surface = pygame.surface.Surface((screen.get_width(), screen.get_height()))
        self.surface.fill("black")
        self.rect = self.surface.get_rect()
    
    def load(self):
        with open("assets/maps/map3.csv", "r") as map:
            csv_reader = csv.reader(map)
            return list(csv_reader)
