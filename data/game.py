import random
import pygame

from .tile import Goal, Wall
from .player import Player
from .NPC import NPC
from .map import Map
from .menu import MainMenu

from .constants import SCREEN_WIDTH, SCREEN_BOTTOM, FPS, images, colours

class Game:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.map = Map(self.screen)
        self.TILE_WIDTH = SCREEN_WIDTH / len(self.map.map[0])
        self.TILE_HEIGHT = SCREEN_BOTTOM / len(self.map.map)
        #print(TILE_HEIGHT, TILE_WIDTH, len(map.map[0]))

        self.player_group = pygame.sprite.GroupSingle()
        self.agents = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        self.player = Player(self.TILE_WIDTH, self.walls, self.bullets, self.player_group)
        self.agent = NPC(self.walls, (self.TILE_WIDTH, self.TILE_HEIGHT), self.map.map, self.goals, self.obstacles, self.agents)

        self.running = True
        self.pause = True
        self.add_tiles()

        self.next_state = None
        
    def get_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.next_state = "main menu"
                elif event.key == pygame.K_SPACE:
                    self.running = False
                    self.next_state = "main menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.gun.is_shooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.player.gun.is_shooting = False
                self.player.gun.was_fired = False

    def render(self):
    
        if self.player.gun.is_shooting:
            self.player.shoot()
        
        self.screen.fill("black")

        self.screen.blit(self.map.surface, self.map.rect)
        
        for bullet in self.bullets.sprites():
            if pygame.sprite.spritecollideany(bullet, self.walls):
                bullet.kill()
        
        for enemy in self.agents.sprites():
            for ray in enemy.rays:
                pygame.draw.line(self.screen, "white", self.agent.rect.center, ray)
            if pygame.sprite.spritecollideany(enemy, self.bullets):
                enemy.kill()
        
        if pygame.sprite.spritecollideany(self.player, self.goals):
            MainMenu(self.screen, self.clock, FPS, self, images["menu_bg"])
            self.reset_game(self.player, self.agents, self.TILE_WIDTH)
        
        self.player.update()
        self.agents.update(self.player)
        self.bullets.update()
        self.screen.blit(self.player.image, self.player.rect)
        #self.screen.blit(agent.image, agent.rect)
        self.agents.draw(self.screen)
        self.bullets.draw(self.screen)


    def reset_game(player: Player, agents, tile_width):
        player.rect.center = (5*tile_width, 60)
        for agent in agents.sprites():
            agent.rect.center = (500, 500)
            agent.direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
            agent.rays = []
            agent.in_vision = False
            agent.is_hunting = False
            agent.path = []
            agent.hunt_time = 0

    def add_tiles(self):
        for i, row in enumerate(self.map.map):
            for j, tile in enumerate(row):
                pygame.draw.rect(self.map.surface, colours[int(tile)], (j * self.TILE_WIDTH, i * self.TILE_HEIGHT, self.TILE_WIDTH, self.TILE_HEIGHT))
                if tile == "9":
                    Goal((j * self.TILE_WIDTH, i * self.TILE_HEIGHT, self.TILE_WIDTH, self.TILE_HEIGHT), self.goals)
                elif tile == "2":
                    Wall((j * self.TILE_WIDTH, i * self.TILE_HEIGHT, self.TILE_WIDTH, self.TILE_HEIGHT), self.walls)
        
        self.obstacles.add(self.walls)
