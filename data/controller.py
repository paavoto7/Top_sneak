import pygame

from .game import Game
from .menu import MainMenu, PauseMenu, SettingsMenu

from .constants import SCREEN_WIDTH, SCREEN_BOTTOM, image_loader, FPS, images

class Controller:
    def __init__(self) -> None:
        pygame.init()
        self.screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        image_loader()
        self.running = True
        game = Game(self.screen)
        self.states = {
            "game": game,
            "main menu": MainMenu(self.screen, images["menu_bg"]),
            "settings": SettingsMenu(self.screen, images["menu_bg"]),
            "pause menu": PauseMenu(self.screen, game.reset_game)
        }

        self.current = self.states["main menu"]
    
    def change_state(self):
        if self.current.running == False:
            self.current = self.states[self.current.next_state]
            self.current.running = True

    def main(self):
        while self.running:
            self.change_state()
            self.current.get_event()
            self.current.render()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
