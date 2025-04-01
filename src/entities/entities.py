import pygame
import math
from src.config.settings import (
    GREEN, RED, YELLOW, WHITE,
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED,
    COIN_SIZE, COIN_ANIMATION_SPEED, COIN_ANIMATION_RANGE,
    CROSSHAIR_SIZE, CROSSHAIR_THICKNESS,
    HOOK_SPEED, HOOK_MAX_DISTANCE, HOOK_ROPE_SPEED
)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform, min_x, max_x):
        super().__init__()
        self.width, self.height = ENEMY_WIDTH, ENEMY_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height
        self.platform = platform
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.min_x = min_x
        self.max_x = max_x
    
    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.rect.right > self.max_x or self.rect.left < self.min_x:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = COIN_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_counter = 0
        self.original_y = y
    
    def update(self):
        self.animation_counter += COIN_ANIMATION_SPEED
        self.rect.y = self.original_y + int(math.sin(self.animation_counter) * COIN_ANIMATION_RANGE)

class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = CROSSHAIR_SIZE
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2, CROSSHAIR_THICKNESS)
        pygame.draw.line(self.image, WHITE, (0, self.size // 2), (self.size, self.size // 2), CROSSHAIR_THICKNESS)
        pygame.draw.line(self.image, WHITE, (self.size // 2, 0), (self.size // 2, self.size), CROSSHAIR_THICKNESS)
        
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()

    def update(self, camera):
        mouse_pos = pygame.mouse.get_pos()
        world_pos = pygame.Vector2(mouse_pos) - camera.scroll
        self.rect.center = world_pos

class GrapplingHook(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, player):
        super().__init__()
        self.player = player
        self.width, self.height = 10, 10
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        angle = math.atan2(target_y - y, target_x - x)
        self.speed = HOOK_SPEED
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        self.max_distance = HOOK_MAX_DISTANCE
        self.initial_x = x
        self.initial_y = y
        
        self.attached = False
        self.attached_point = None
        self.rope_length = 0
        self.rope_speed = HOOK_ROPE_SPEED

    def update(self, platforms):
        if not self.attached:
            self.rect.x += self.dx
            self.rect.y += self.dy
            
            distance = math.sqrt((self.rect.centerx - self.initial_x)**2 + 
                               (self.rect.centery - self.initial_y)**2)
            if distance > self.max_distance:
                self.kill()
                self.player.can_grapple = True
                self.player.is_grappling = False
                return
            
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.attached = True
                    self.attached_point = (self.rect.centerx, self.rect.centery)
                    self.player.is_grappling = True
                    return
        else:
            dx = self.attached_point[0] - self.player.rect.centerx
            dy = self.attached_point[1] - self.player.rect.centery
            
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                dx = dx / distance * self.rope_speed
                dy = dy / distance * self.rope_speed
                
                self.player.rect.x += dx
                self.player.rect.y += dy
                
                self.player.vel_y = 0
                self.player.jumping = False
            
            if distance < 5:
                self.kill()
                self.player.can_grapple = True
                self.player.is_grappling = False 