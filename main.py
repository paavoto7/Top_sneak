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


class Player(pygame.sprite.Sprite):
    def __init__(self, tile_width, walls, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(images["ninja"], 0.2)
        self.rect = self.image.get_rect(center=(5*tile_width, 60))
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = tile_width // 2 # Move the player half tile
        self.walls = walls # Wall sprites (could be global)
        self.gun = Gun("auto_rifle")

    def move(self, pressed):
        # Calculate players velocity based on key presses
        self.velocity_x, self.velocity_y = 0, 0
        if pressed[pygame.K_w] or pressed[pygame.K_UP]:
            self.velocity_y -= self.vel
            
        elif pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
            self.velocity_y += self.vel
            
        if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
            self.velocity_x -= self.vel
            
        elif pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
            self.velocity_x += self.vel
        
        # Normalize diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)
        
        # Update the temporary rect and check collisions
        self.rect.y += self.velocity_y      
        if self.collides():
            self.rect.y -= self.velocity_y
            
        self.rect.x += self.velocity_x
        if self.collides():
            self.rect.x -= self.velocity_x
            
    def collides(self):
        # Check for collision with any of the walls
        if pygame.sprite.spritecollideany(self, self.walls):
            return True
    
    def shoot(self):
        # Call fire and calculate shooting angle based on mouse position
        mouse_pos = pygame.mouse.get_pos() - pygame.Vector2(self.rect.center)
        angle = math.degrees(math.atan2(mouse_pos[1], mouse_pos[0]))
        self.gun.fire(self.rect.center, angle)
        
    def update(self):
        self.move(pygame.key.get_pressed())


class NPC(pygame.sprite.Sprite):
    def __init__(self, walls, tiles, map, *groups) -> None:
        super().__init__(*groups)
        self.image = pygame.transform.scale(images["agent"], tiles)
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
        """Update player position based on whether hunting is on.
        Takes player as argument for scan method.
        """
        if not self.is_hunting:
            self.scan(player)
            self.rect.x += self.direction[0]
            self.rect.y += self.direction[1]
            self.collides()
            #self.in_vision = False
        else:
            self.find_path(player)
            self.hunt()
            self.rect.x += self.direction[0]
            self.rect.y += self.direction[1]
        self.calc_rays()


    def collides(self):
        # Check for collision and update position accordingly
        if pygame.sprite.spritecollideany(self, self.walls) or pygame.sprite.spritecollideany(self, goals):
            self.rect.x -= self.direction[0]
            self.rect.y -= self.direction[1]
            if not self.in_vision: # Set new direction if player not seen
                self.direction = [random.uniform(-self.direction[0], 3), random.uniform(-self.direction[1], 3)]

            
    
    def scan(self, player: Player):
        """Scan for the player in the vision cone.
        """
        
        def actual_distance(angle):
            # Calculates the actual distance between the angles
            # angle - 360*math.floor((angle + 180) * (1/360))
            return (angle + 180) % 360 - 180
        
        # Calculate direction vector from enemy to player
        direction = (player.rect.centerx - self.rect.centerx), (player.rect.centery - self.rect.centery)

        # Calculate angle between enemy and the player
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        
        # Calculate angle of enemy's current direction
        direction_angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        #print(direction_angle- angle, angular_distance_degrees(direction_angle- angle))
        
        dist = math.dist(self.rect.center, player.rect.center)
        speed = player.vel - 2

        # Check for player in vision cone
        #if dist < 250 and direction_angle - 40 <= angle <= direction_angle + 40:
        if dist < 250 and - 40 < actual_distance(direction_angle - angle) < 40:
            self.direction = [
                math.cos(math.radians(-angle*1.05)) * speed,
                math.sin(math.radians(-angle*1.05)) * speed
                ]
            self.in_vision = True

        # Check for player in immediate vicinity
        elif dist < 5:
            self.direction = [
                math.cos(math.radians(-angle)) * speed,
                math.sin(math.radians(-angle)) * speed
                ]
            self.in_vision = True

        # Start hunting the player
        elif self.in_vision == True:
            self.is_hunting = True
            self.hunt_time = 250
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
        
        queue = deque([selfpos])
        visited = deque()
        while queue:
            x, y = queue.popleft()
            if (x, y) == playerpos:
                self.path = visited
                return
            closest = []
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
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

        curpos = self.rect.centerx / self.tiles[0], self.rect.centery / self.tiles[1]
        newcoord = self.path.popleft()

        self.direction = [newcoord[0] - curpos[0], newcoord[1] - curpos[1]]


class Gun():
    def __init__(self, name):
        self.image = pygame.transform.scale_by(images["revolver"], 0.1)
        self.name = name
        stats = guns[name]
        self.power = stats[0]
        self.mag_size = stats[1]
        self.fire_rate = stats[2] # per second
        self.spread = stats[3]
        self.is_auto = stats[4]
        self.was_fired = False
        self.is_shooting = False
        self.last_shot = - self.fire_rate
    
    def fire(self, center, angle):
        time_now = pygame.time.get_ticks()
        if self.is_shooting and time_now - self.last_shot > self.fire_rate:
            self.last_shot = time_now

            new_angle = angle + random.uniform(-self.spread, self.spread)
            if self.is_auto:
                Projectile(center, self.power, new_angle, bullets)

            elif self.was_fired == False:
                self.was_fired = True
                if self.name == "shotgun":
                    angle = angle - self.spread
                    for _ in range(5):
                        angle = angle + self.spread // 5
                        Projectile(center, self.power, angle, bullets)
                else:
                    Projectile(center, self.power, new_angle, bullets)
        

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, vel, angle, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(images["bullet"], 0.04)
        self.image = pygame.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=position)
        self.velocity = vel
        self.angle = angle
    
    def update(self):
        x = (math.cos(math.radians(self.angle)) * self.velocity, math.sin(math.radians(self.angle)) * self.velocity)
        self.rect.x += x[0]
        self.rect.y += x[1]


class Map:
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.map = self.load()
        self.surface = pygame.surface.Surface((screen.get_width(), screen.get_height()))
        self.surface.fill("black")
        self.rect = self.surface.get_rect()
    
    def load(self):
        with open("map3.csv", "r") as map:
            csv_reader = csv.reader(map)
            return list(csv_reader)


class Wall(pygame.sprite.Sprite):
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)


class Goal(pygame.sprite.Sprite):
    def __init__(self, bounds, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(*bounds)


def reset_game(player: Player, agents: pygame.sprite.Group, tile_width):
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
