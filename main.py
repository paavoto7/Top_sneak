import random
import pygame
import csv
import math
from collections import deque
from os import listdir

from menu import menu

FPS = 60
SCREEN_BOTTOM = 800
SCREEN_WIDTH = 896

images = {}

def image_loader():
    for imagename in listdir("./assets/"):
        images[imagename[0:-4]] = pygame.image.load(f"./assets/{imagename}").convert_alpha()

colours = {0: (0,0,0), 1: (211,211,211), 2: (80,80,80), 9:(200,0,0)}

guns = {
    #   [power, mag size, firerate in ms, spread, is automatic]
    "pistol": [30, 30, 500, 2, False],
    "auto_rifle": [75, 50, 100, 5, True],
    "shotgun": [50, 30, 1000, 10, False],
    "sniper": [100, 5, 1500, 0.5, False]
}










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


bullets = pygame.sprite.Group()
goals = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

def main():
    pygame.init()
    screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
    screen = pygame.display.set_mode(screen_size, pygame.SCALED)
    clock = pygame.time.Clock()
    map = Map(screen)
    image_loader()

    TILE_WIDTH = SCREEN_WIDTH / len(map.map[0])
    TILE_HEIGHT = SCREEN_BOTTOM / len(map.map)
    print(TILE_HEIGHT, TILE_WIDTH, len(map.map[0]))

    player_group = pygame.sprite.GroupSingle()
    agents = pygame.sprite.Group()
    walls = pygame.sprite.Group()

    player = Player(TILE_WIDTH, walls, player_group)
    agent = NPC(walls, (TILE_WIDTH, TILE_HEIGHT), map.map, agents)

    for i, row in enumerate(map.map):
        for j, tile in enumerate(row):
            pygame.draw.rect(map.surface, colours[int(tile)], (j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
            if tile == "9":
                Goal((j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), goals)
            elif tile == "2":
                Wall((j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), walls)
    
    obstacles.add(walls)
    running = True
    pause = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    pause = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.gun.is_shooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                player.gun.is_shooting = False
                player.gun.was_fired = False

        if pause:
            pause = menu(screen, clock, FPS, images["menu_bg"])

        player.shoot()
        
        screen.fill("black")

        screen.blit(map.surface, map.rect)
        
        for bullet in bullets.sprites():
            if pygame.sprite.spritecollideany(bullet, walls):
                bullet.kill()
        
        for enemy in agents.sprites():
            for ray in enemy.rays:
                pygame.draw.line(screen, "white", agent.rect.center, ray)
            if pygame.sprite.spritecollideany(enemy, bullets):
                enemy.kill()
        
        if pygame.sprite.spritecollideany(player, goals):
            menu(screen, clock, FPS, images["menu_bg"], game_over=True)
            reset_game(player, agents, TILE_WIDTH)
        
        player.update()
        agents.update(player)
        bullets.update()
        screen.blit(player.image, player.rect)
        #screen.blit(agent.image, agent.rect)
        agents.draw(screen)
        bullets.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
