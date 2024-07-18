from collections import deque
import pygame
import random
import math

from .constants import images

class NPC(pygame.sprite.Sprite):
    def __init__(self, walls, tiles, map, goals, obstacles, *groups) -> None:
        super().__init__(*groups)
        self.image = pygame.transform.scale(images["agent"], tiles)
        self.rect = self.image.get_rect(center=(500, 500))
        self.walls = walls
        self.direction = pygame.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        self.vision_distance = 250
        self.rays = []
        self.in_vision = False
        self.is_hunting = False
        self.tiles = tiles
        self.map = map
        self.path = []
        self.hunt_time = 0
        self.goals = goals
        self.obstacles = obstacles
    
    def update(self, player):
        """Update player position based on whether hunting is on.
        Takes player as argument for scan method.
        """
        if not self.is_hunting:
            self.scan(player)
            #self.rect.x += self.direction[0]
            #self.rect.y += self.direction[1]
            self.rect.center += self.direction
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
        if pygame.sprite.spritecollideany(self, self.walls) or pygame.sprite.spritecollideany(self, self.goals):
            #self.rect.x -= self.direction[0]
            #self.rect.y -= self.direction[1]
            self.rect.center -= self.direction
            if not self.in_vision: # Set new direction if player not seen
                self.direction.update(random.uniform(-self.direction[0], 3), random.uniform(-self.direction[1], 3))
    
    def scan(self, player):
        """Scan for the player in the vision cone.
        """
        
        def actual_distance(angle):
            # Calculates the actual distance between the angles
            # angle - 360*math.floor((angle + 180) * (1/360))
            return (angle + 180) % 360 - 180
  
        # Calculate direction vector from enemy to player
        direction = (player.rect.centerx - self.rect.centerx), (player.rect.centery - self.rect.centery)

        # angle_between = self.direction.angle_to(direction) This would work but I need the angle below

        # Calculate angle between enemy and the player
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        
        # Calculate angle of enemy's current direction
        # direction_angle = math.degrees(math.atan2(-self.direction[1], self.direction[0])) Previous
        direction_angle = self.direction.angle_to((1, 0)) # (1, 0) is the pos x-axis
        
        dist = math.dist(self.rect.center, player.rect.center)
        speed = player.vel - 2

        # Check for player in vision cone
        #if dist < 250 and direction_angle - 40 <= angle <= direction_angle + 40:
        if dist < 250 and - 60 < actual_distance(direction_angle - angle) < 60 and not self.view_obstructed(player):
            self.direction.update(
                math.cos(math.radians(-angle*1.05)) * speed,
                math.sin(math.radians(-angle*1.05)) * speed
            )
            self.in_vision = True

        # Check for player in immediate vicinity
        elif dist < 5:
            self.direction.update(
                math.cos(math.radians(-angle)) * speed,
                math.sin(math.radians(-angle)) * speed
            )
            self.in_vision = True

        # Start hunting the player
        elif self.in_vision == True:
            self.is_hunting = True
            self.hunt_time = 250
            self.in_vision = False
        else:
            self.in_vision = False
    
    def view_obstructed(self, player):
        """Checks if the player is hiding behind an obstacle or wall.
        Uses a variation of Bresenham's algorithm (https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)"""
        x1, y1 = int(self.rect.centerx / self.tiles[0]), int(self.rect.centery / self.tiles[1])
        x2, y2 = int(player.rect.centerx / self.tiles[0]), int(player.rect.centery / self.tiles[1])
        dx = x2 - x1
        dy = y2 - y1
        
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        d = 2 * dy - dx
        y = y1
        
        l_x2 = x2
        direction = 1
        if dx < 0:
            direction = -1
            l_x2 -= 1
        else:
            l_x2 += 1

        # With a larger map this algorithm will get very expensive
        for x in range(x1, l_x2, direction):
            for obstacle in self.obstacles:
                if obstacle.rect.collidepoint(x * self.tiles[0], y * self.tiles[1]):
                    return True
            if d > 0:
                y += yi
                d += (2 * (dy-dx))
            else:
                d += 2* dy
        return False

    def calc_rays(self):
        """Calculates the ending point of the rays to be drawn.
        The rays represent the enemy FOV and are later drawn in the main loop."""
        self.rays.clear()
        angle = 80 # FOV 160
        # direction = int(math.degrees(math.atan2(self.direction[1], self.direction[0])))
        direction_angle = -int(self.direction.angle_to((1, 0)))
        for i in range(direction_angle - angle, direction_angle + angle):
            self.rays.append((
                self.rect.centerx+self.vision_distance*math.cos(math.radians(i)),
                self.rect.centery+self.vision_distance*math.sin(math.radians(i)))
                )
    
    def find_path(self, player):
        """Used for finding the path to the player.
        Uses Breadth first search with a heuristic."""

        def is_valid(row, col):
            # Determines whether tile in bounds and is a wall
            return 0 <= row < len(self.map[0]) and 0 <= col < len(self.map) and self.map[col][row] == "1"
        
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
                    # Calculates the coordinate for the new point and the distance from that to the player
                    is_closer = math.dist((new_x * self.tiles[0], new_y * self.tiles[1]), player.rect.center)
                    closest.append((new_x, new_y, is_closer))
                    
            if len(closest) != 0:
                mini = min(closest, key=lambda p:p[2])
                queue.append((mini[0], mini[1]))
                visited.append((mini[0], mini[1]))

        self.path = []
        self.is_hunting = False
    
    def sign(self, x):
        return x // abs(x) if x != 0 else 0
    
    def hunt(self):
        # Used for moving to the players position after lsoing sight of them
        if self.hunt_time == 0 or self.path == None or len(self.path) == 0:
            self.is_hunting = False
            self.direction.update(random.uniform(-self.direction[0], 3), random.uniform(-self.direction[1], 3))
        else:
            self.hunt_time -= 1

            curpos = self.rect.centerx / self.tiles[0], self.rect.centery / self.tiles[1]
            newcoord = self.path.popleft()

            self.direction.update(newcoord[0] - curpos[0], newcoord[1] - curpos[1])
