import pygame

from .constants import SCREEN_CENTER

class Button:
    """Provides a button with an image"""
    def __init__(self, image=None, rect=None, pos=(0,0)) -> None:
        if image:
            self.image = image
            self.rect = self.image.get_rect(midtop=pos)
        else:
            self.rect = rect
        
    def pressed(self, coordinate):
        """Check whether a point collides, e.g. with mouse coordinates"""
        return self.rect.collidepoint(coordinate)


class MenuButton(Button):
    def __init__(self, font_name, cont, pos, font_size=40, colour="black"):
        self.text = Text(font_name, cont, pos, font_size, colour)
        super().__init__(rect=self.text.tRect)


class Text:
    def __init__(self, font_name, cont, pos, font_size=40, colour="black") -> None:
        self.colour = colour
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text = self.font.render(str(cont), True, colour)
        self.tRect = self.text.get_rect()
        self.tRect.center = pos

    def update(self, cont):
        self.text = self.font.render(str(cont), True, self.colour)


class Highlighted:
    def __init__(self, items: list = [None]) -> None:
        self.items = items
        self._current = [items[0], 0]
        self.surface = pygame.surface.Surface(self._current[0].rect.size, pygame.SRCALPHA)
        self.surface.fill((255,255,255,100))
    
    @property
    def current(self):
        return self._current[0]
    
    def add_items(self, items: list) -> None:
        self.items.append(items)

    def change(self, direction):
        if (index := self._current[1]+direction) == len(self.items):
            index = 0
        self._current[0] = self.items[index]
        self._current[1] = self.items.index(self._current[0])


class Menu:
    def __init__(self, game, screen, bg, buttons) -> None:
        self.game = game
        self.screen = screen
        self.bg = bg
        #self.keys = {"up": False, "down": False, "esc": False, "enter": False}
        self.running = True
        self.highlited = Highlighted(buttons)
        self.action = None
        self.next_state = None

    def get_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.highlited.current == self.highlited.items[-1]:
                        self.action = self.highlited.current
                    else:
                        self.action = self.highlited.current
                    self.running = False
                    
                if event.key == pygame.K_UP:
                    self.highlited.change(-1)
                elif event.key == pygame.K_DOWN:
                    self.highlited.change(1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.highlited.items:
                    if button.pressed(pygame.mouse.get_pos()):
                        self.running = False
                        self.action = button
    
    def execute_button(self):
        pass
    
    def render(self):
        self.execute_button()

        self.screen.fill("black")
        self.screen.blit(self.bg, (0, 0))

        """if self.game_over:
            over = Text("impact", "Game Over", self.center, 100, (200, 28, 36))
            self.screen.blit(over.text, over.tRect)"""

        for button in self.highlited.items:
            self.screen.blit(button.text.text, button.rect)

        self.screen.blit(self.highlited.surface, self.highlited.current.rect.topleft)


class MainMenu(Menu):
    """Provides a menu to be used in a game.
    Game over argument decides whether to display start menu or not."""
    def __init__(self, screen, controller, bg=None) -> None:
        
        self.center = SCREEN_CENTER

        self.title = Text("impact", "Title", (self.center[0], self.center[1] - self.center[1] // 2), 100)
        self.start = MenuButton("impact", "Start game", self.center, colour="black")
        self.settings = MenuButton("impact", "Settings", (self.center[0], self.center[1] + self.start.rect.height), colour="black")
        self.exit_menu = MenuButton("impact", "Exit game", (self.center[0], self.center[1] + self.start.rect.height*2), colour="black")

        super().__init__(controller, screen, bg, [self.start, self.settings, self.exit_menu])
        
        #self.button = Button(pygame.image.load("./assets/agent.png"), (center[0], center[1]))
    
    def execute_button(self):
        if self.action:
            match self.action:
                case self.start:
                    self.next_state = "game"
                case self.settings:
                    self.next_state = "settings"
                case self.exit_menu:
                    exit()


class SettingsMenu(Menu):
    def __init__(self, game, screen, bg) -> None:
        self.center = SCREEN_CENTER
        self.start = MenuButton("impact", "Change brightness", self.center, colour="black")
        self.back = MenuButton("impact", "Go back", (self.center[0], self.center[1]+self.start.rect.height), colour="black")
        super().__init__(game, screen, bg, [self.start, self.back])
    
    def execute_button(self):
        if self.action:
            match self.action:
                case self.back:
                    self.next_state = "main menu"
