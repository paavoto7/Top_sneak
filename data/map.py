import pygame
import csv
import json

class Map:
    def __init__(self, screen, map_name) -> None:
        self.map = self._load(map_name)
        self.surface = pygame.surface.Surface((screen.get_width(), screen.get_height()))
        self.surface.fill("black")
        self.rect = self.surface.get_rect()
    
    def _load(self, map_name):
        with open(f"assets/maps/{map_name}.csv", "r") as map:
            csv_reader = csv.reader(map)
            return list(csv_reader)


class Level:
    def __init__(self, screen, level_num=1) -> None:
        self.level_num = level_num
        self.load()
        self.map = Map(screen, f"level_{self.level_num}_map")

    def load(self, level_num=1):
        if self.level_num != level_num:
            self.level_num = level_num
        with open("assets/maps/leveldata.json", "r") as level_data:
            data = json.load(level_data)[f"level_{self.level_num}"]
            self.gun = data["gun"]
            self.player_position = data["player_positionx"], data["player_positionx"]
