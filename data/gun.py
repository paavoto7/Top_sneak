import pygame
import random
import math

from .constants import guns, images

class Gun():
    def __init__(self, name, bullets):
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
        self.bullets = bullets
    
    def fire(self, center, angle):
        time_now = pygame.time.get_ticks()
        if self.is_shooting and time_now - self.last_shot > self.fire_rate:
            self.last_shot = time_now

            new_angle = angle + random.uniform(-self.spread, self.spread)
            if self.is_auto:
                Projectile(center, self.power, new_angle, self.bullets)

            elif self.was_fired == False:
                self.was_fired = True
                if self.name == "shotgun":
                    angle = angle - self.spread
                    for _ in range(5):
                        angle = angle + self.spread // 5
                        Projectile(center, self.power, angle, self.bullets)
                else:
                    Projectile(center, self.power, new_angle, self.bullets)
        

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
