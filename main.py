import random
import pygame
import csv
import math
from collections import deque

FPS = 60
SCREEN_BOTTOM = 800
SCREEN_WIDTH = 896

colours = {0: (0,0,0,0), 1: (211,211,211), 2: (80,80,80)}


def map_loader():
    with open("map3.csv", "r") as map:
        csv_reader = csv.reader(map)
        return list(csv_reader)


class Player(pygame.sprite.Sprite):
    def __init__(self, tile_width, walls, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(pygame.image.load("./ninja.png").convert_alpha(), 0.2)
        self.rect = self.image.get_rect(center=(100, 150))
        self.move_rect = self.image.get_rect(center=(100, 150))
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = tile_width // 3
        self.dirx = 0
        self.diry = 0
        self.walls = walls

    def move(self, pressed):
        self.velocity_x, self.velocity_y = 0, 0
        self.diry = 0
        self.dirx = 0
        if pressed[pygame.K_w] or pressed[pygame.K_UP]:
            #self.rect.move_ip(0, -self.vel)
            self.velocity_y -= self.vel
            self.diry = -1
            
        elif pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
            #self.rect.move_ip(0, self.vel)
            self.velocity_y += self.vel
            self.diry = 1
            
        if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
            #self.rect.move_ip(-self.vel, 0)
            self.velocity_x -= self.vel
            self.dirx = -1
            
        elif pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
            #self.rect.move_ip(self.vel, 0)
            self.velocity_x += self.vel
            self.dirx = 1
            
        
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)
        
        self.move_rect.y += self.velocity_y
        
        if self.collides():
            self.move_rect.y -= self.velocity_y
            
        self.move_rect.x += self.velocity_x
        if self.collides():
            self.move_rect.x -= self.velocity_x
            
    def collides(self):
        if pygame.sprite.spritecollideany(self, self.walls):
            return True
    
    def update(self):
        x = self.move(pygame.key.get_pressed())
        self.rect = self.move_rect

    def push_back(self):
        self.rect.move_ip(-self.dirx, -self.diry)


class NPC(pygame.sprite.Sprite):
    def __init__(self, walls, tiles, map, *groups) -> None:
        super().__init__(*groups)
        #self.image = pygame.transform.scale_by(pygame.image.load("./agent.png").convert_alpha(), 0.1)
        self.image = pygame.transform.scale(pygame.image.load("./agent.png").convert_alpha(), tiles)
        self.rect = self.image.get_rect(center=(500, 500))
        self.walls = walls
        self.direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.vision_distance = 250
        self.rays = []
        self.in_vision = False
        self.is_hunting = False
        self.tiles = tiles
        self.map = map
        self.path = []
        self.hunt_time = 0
    
    def update(self, player):
        if not self.is_hunting:
            self.seek(player)
            self.rect.x += self.direction[0]
            self.rect.y += self.direction[1]
            self.collides()
            self.calc_rays()
            #self.in_vision = False
        else:
            self.find_path(player)
            self.hunt()
            self.rect.x += self.direction[0]
            self.rect.y += self.direction[1]
            self.calc_rays()


    def collides(self):
        if pygame.sprite.spritecollideany(self, self.walls):
            self.rect.x -= self.direction[0]
            self.rect.y -= self.direction[1]
            if not self.in_vision:
                self.direction = [random.uniform(-self.direction[0], 3), random.uniform(-self.direction[1], 3)]
            
    
    def seek(self, player: Player):
        direction = (player.rect.centerx - self.rect.centerx), (player.rect.centery - self.rect.centery)
        dist = math.dist(self.rect.center, player.rect.center)
        speed = player.vel - 2
        angle = math.degrees(math.atan2(-direction[1], direction[0]))

        direction_angle = -math.degrees(math.atan2(self.direction[1], self.direction[0]))

        if dist < 250 and direction_angle - 80 <= angle <= direction_angle + 80:
            self.direction = [math.cos(math.radians(-angle*1.05)) * speed, math.sin(math.radians(-angle*1.05)) * speed]
            self.in_vision = True
        elif dist < 40:
            self.direction = [math.cos(math.radians(-angle)) * speed, math.sin(math.radians(-angle)) * speed]
            self.in_vision = True
        elif self.in_vision == True:
            self.is_hunting = True
            self.hunt_time = 200000
            self.in_vision = False
        else:
            self.in_vision = False

    def calc_rays(self):
        self.rays.clear()
        angle = 80 # FOV 160
        direction = int(math.degrees(math.atan2(self.direction[1], self.direction[0])))
        for i in range(direction-angle, direction+angle):
            self.rays.append((
                self.rect.centerx+self.vision_distance*math.cos(math.radians(i)),
                self.rect.centery+self.vision_distance*math.sin(math.radians(i)))
                )
    
    def find_path(self, player: Player):
        def is_valid(row, col):
            return 0 <= row < len(self.map[0]) and 0 <= col < len(self.map) and self.map[col][row] == "1"

        def is_closer(row, col):
            return math.dist((row * self.tiles[0], col * self.tiles[1]), player.rect.center)
        
        if self.path == None or len(self.path) != 0 or self.is_hunting == False:
            return
        
        selfpos = int(self.rect.centerx // self.tiles[0]), int(self.rect.centery // self.tiles[1])
        playerpos = int(player.rect.centerx // self.tiles[0]), int(player.rect.centery // self.tiles[1])

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        """pol = int(self.sign(playerpos[0]-selfpos[0])), int(self.sign(playerpos[1]-selfpos[1]))
        directions = [(pol[0], 0), (0, pol[1])]"""
        queue = deque([selfpos])
        visited = deque()
        while queue:
            x, y = queue.popleft()
            if (x, y) == playerpos:
                #lista = [self.map[x][y] for y, x in visited]
                self.path = visited
                return
            closest = []
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                #print(new_x, new_y, is_valid(new_x, new_y))
                if is_valid(new_x, new_y) and (new_x, new_y) not in visited:
                    closest.append((new_x, new_y, is_closer(new_x, new_y)))
            if len(closest) != 0:
                mini = min(closest, key=lambda p:p[2])
                queue.append((mini[0], mini[1]))
                visited.append((mini[0], mini[1]))

        self.path = []
        self.is_hunting = False
    
    def sign(self, x):
        return x // abs(x) if x != 0 else 0
    
    def hunt(self):
        if self.hunt_time == 0 or self.path == None or len(self.path) == 0:
            self.is_hunting = False
            self.direction = [random.uniform(-self.direction[0], 3), random.uniform(-self.direction[1], 3)]
            return
        self.hunt_time -= 1
        #print(path)
        curpos = int(self.rect.centerx // self.tiles[0]), int(self.rect.centery // self.tiles[1])
        newcoord = self.path.popleft()
        #self.rect.x += newcoord[0] - curpos[0]
        #self.rect.y += newcoord[1] - curpos[1]
        self.direction = [newcoord[0] - curpos[0], newcoord[1] - curpos[1]]
        
        """for tile in path:
            new_x = tile[0]-curpos[0]
            new_y = tile[1]-curpos[1]
            
            curpos = (self.rect.x,
            self.rect.y)"""
        #self.is_hunting = False


class Map:
    def __init__(self) -> None:
        self.map = map_loader()


class Wall(pygame.sprite.Sprite):
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)


class Floor(pygame.sprite.Sprite):
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)


def main():
    pygame.init()
    screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
    screen = pygame.display.set_mode(screen_size, pygame.SCALED)
    clock = pygame.time.Clock()
    map = Map()

    TILE_WIDTH = SCREEN_WIDTH / len(map.map[0])
    TILE_HEIGHT = SCREEN_BOTTOM / len(map.map)
    print(TILE_HEIGHT, TILE_WIDTH, len(map.map[0]))

    player_group = pygame.sprite.GroupSingle()
    agents = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    floors = pygame.sprite.Group()

    player = Player(TILE_WIDTH, walls, player_group)
    agent = NPC(walls, (TILE_WIDTH, TILE_HEIGHT), map.map, agents)

    for i, row in enumerate(map.map):
        for j, tile in enumerate(row):
            if tile == "1":
                Floor((j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), floors)
            elif tile == "2":
                Wall((j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), walls)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill("black")

        for i, row in enumerate(map.map):
            for j, tile in enumerate(row):
                #print(i, j)
                pygame.draw.rect(screen, colours[int(tile)], (j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
        
        for ray in agent.rays:
            pygame.draw.line(screen, "white", agent.rect.center, ray)
        
        player.update()
        agents.update(player)
        screen.blit(player.image, player.rect)
        screen.blit(agent.image, agent.rect)
        #agents.draw(screen)
        

        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
