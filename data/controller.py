import pygame

from .game import Game
from .menu import MainMenu, SettingsMenu

from .constants import SCREEN_WIDTH, SCREEN_BOTTOM, image_loader, FPS, images

class Controller:
    def __init__(self) -> None:
        pygame.init()
        self.screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        image_loader()
        self.running = True
        self.states = {
            "game": Game(self.screen),
            "main menu": MainMenu(self.screen, self, images["menu_bg"]),
            "settings": SettingsMenu(self, self.screen, images["menu_bg"])
        }
        self.current = self.states["main menu"]
    
    def change_state(self):
        if self.current.running == False:
            self.current = self.states[self.current.next_state]
            self.current.running = True
            """if self.current == self.states["main menu"]:
                self.current = self.states["game"]
            else:
                self.current = self.states["main menu"]
                self.states["main menu"].action = None
            self.current.running = True"""

    def main(self):
        while self.running:
            self.change_state()
            self.current.get_event()
            self.current.render()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
