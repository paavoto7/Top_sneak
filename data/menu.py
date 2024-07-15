import pygame


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
    def __init__(self, items: list) -> None:
        self.items = items
        self._current = [items[0], 0]
        self.surface = pygame.surface.Surface(self._current[0].rect.size, pygame.SRCALPHA)
        self.surface.fill((255,255,255,100))
    
    @property
    def current(self):
        return self._current[0]

    def change(self, direction):
        if (index := self._current[1]+direction) == len(self._current):
            index = 0
        self._current[0] = self.items[index]
        self._current[1] = self.items.index(self._current[0])


def menu(screen: pygame.surface.Surface, clock, FPS, bg=None, game_over=False) -> bool:
    """Provides a menu to be used in a game.
    Game over argument decides whether to display start menu or not."""

    on_pause = True
    center = (screen.get_width() / 2, screen.get_height() / 2)

    #button = Button(pygame.image.load("./assets/agent.png"), (center[0], center[1]))
    title = Text("impact", "Title", (center[0], center[1] - center[1] // 2), 100)
    start = MenuButton("impact", "Start game", center, colour="black")
    quit = MenuButton("impact", "Exit game", (center[0], center[1] + start.rect.height), colour="black")
    highlited = Highlighted([start, quit])

    while on_pause:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if highlited.current == start:
                        on_pause = False
                    elif highlited.current == quit:
                        exit()
                if event.key == pygame.K_UP:
                    highlited.change(-1)
                elif event.key == pygame.K_DOWN:
                    highlited.change(1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start.button.pressed(pygame.mouse.get_pos()):
                    on_pause = False
            if event.type == pygame.QUIT:
                exit()
        
        screen.fill("black")
        screen.blit(bg, (0, 0))

        if game_over:
            over = Text("impact", "Game Over", center, 100, (200, 28, 36))
            screen.blit(over.text, over.tRect)

        screen.blit(start.text.text, start.rect)
        screen.blit(quit.text.text, quit.rect)
        screen.blit(title.text, title.tRect)
        screen.blit(highlited.surface, highlited.current.rect.topleft)
        pygame.display.flip()
        clock.tick(FPS)

    return False
