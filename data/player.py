import pygame
import math

from .gun import Gun
from .constants import images

class Player(pygame.sprite.Sprite):
    def __init__(self, tile_width, walls, bullets, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(images["ninja"], 0.2)
        self.rect = self.image.get_rect(center=(5*tile_width, 60))
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = tile_width // 2 # Move the player half tile
        self.walls = walls # Wall sprites (could be global)
        self.gun = Gun("auto_rifle", bullets)

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
