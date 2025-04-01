import pygame
import math
from src.config.settings import (
    BLUE, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    PLAYER_JUMP_SPEED, PLAYER_DASH_SPEED,
    PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN,
    PLAYER_ATTACK_DURATION
)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Criar um retângulo simples para o jogador
        self.width, self.height = PLAYER_WIDTH, PLAYER_HEIGHT
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(BLUE)
        
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumping = False
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.facing_right = True
        self.grappling_hook = None
        self.can_grapple = True
        self.grapple_cooldown = 0
        self.is_grappling = False
        
        # Novas variáveis para dash e ataque
        self.is_dashing = False
        self.is_normal_dash = False
        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_duration = PLAYER_DASH_DURATION
        self.dash_timer = 0
        self.can_dash = True
        self.dash_cooldown = 0
        self.attack_box = None
        self.attack_duration = PLAYER_ATTACK_DURATION
        self.attack_timer = 0
        self.can_air_attack = True
        self.dash_direction = pygame.Vector2(0, 0)
        self.attack_button_pressed = False

    def update(self, platforms, enemies, coins):
        dx = 0
        dy = 0

        # Processar teclas (WASD)
        key = pygame.key.get_pressed()
        if not self.is_grappling and not self.is_dashing:
            if key[pygame.K_a]:
                dx -= self.speed
                self.facing_right = False
            if key[pygame.K_d]:
                dx += self.speed
                self.facing_right = True
            if key[pygame.K_SPACE] and not self.jumping:
                self.vel_y = PLAYER_JUMP_SPEED
                self.jumping = True
            if key[pygame.K_LSHIFT] and self.can_dash:
                self.start_normal_dash()

        # Atualizar cooldown do grappling hook
        if not self.can_grapple:
            self.grapple_cooldown -= 1
            if self.grapple_cooldown <= 0:
                self.can_grapple = True

        # Atualizar cooldown do dash
        if not self.can_dash:
            self.dash_cooldown -= 1
            if self.dash_cooldown <= 0:
                self.can_dash = True

        # Atualizar dash
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.is_normal_dash = False
                self.can_dash = False
                self.dash_cooldown = PLAYER_DASH_COOLDOWN
                self.vel_y = 0
                self.image = self.original_image.copy()
            else:
                self.rect.x += self.dash_direction.x
                self.rect.y += self.dash_direction.y
                
                if self.attack_box:
                    self.attack_box.center = self.rect.center
                    
                    for enemy in enemies:
                        if self.attack_box.colliderect(enemy.rect):
                            enemy.kill()
                            self.score += 20

        # Atualizar ataque
        if self.attack_box:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attack_box = None

        # Adicionar gravidade apenas quando não está sendo puxado ou dashing
        if not self.is_grappling and not self.is_dashing:
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

        # Verificar colisão com plataformas
        for platform in platforms:
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.jumping = False
                    self.can_dash = True
                    self.dash_cooldown = 0
                    self.can_air_attack = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                dy = 0

        # Estado de invencibilidade
        if self.invincible and not self.is_dashing:
            self.invincible_timer += 1
            if self.invincible_timer > 60:
                self.invincible = False
                self.invincible_timer = 0
                self.image = self.original_image.copy()
            else:
                if self.invincible_timer % 10 < 5:
                    self.image.fill(WHITE)
                else:
                    self.image = self.original_image.copy()
        
        # Verificar colisão com inimigos
        if not self.invincible and not self.is_dashing:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    self.lives -= 1
                    self.invincible = True
                    if self.rect.centerx < enemy.rect.centerx:
                        self.rect.x -= 50
                    else:
                        self.rect.x += 50
                    self.vel_y = -5
                    if self.lives <= 0:
                        self.kill()
                        return
        
        # Verificar colisão com moedas
        for coin in coins:
            if self.rect.colliderect(coin.rect):
                self.score += 10
                coin.kill()

        # Mover o jogador apenas quando não está sendo puxado ou dashing
        if not self.is_grappling and not self.is_dashing:
            self.rect.x += dx
            self.rect.y += dy

        # Verificar limites da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.jumping = False

    def start_normal_dash(self):
        self.dash_direction = pygame.Vector2(self.dash_speed if self.facing_right else -self.dash_speed, 0)
        self.is_dashing = True
        self.is_normal_dash = True
        self.dash_timer = self.dash_duration
        self.image = self.original_image.copy()
        self.image.set_alpha(128)
        self.can_dash = False
        self.dash_cooldown = PLAYER_DASH_COOLDOWN

    def dash_attack(self, target_x, target_y, grappling_hooks):
        if not self.can_dash or (self.jumping and not self.can_air_attack):
            return

        if self.is_grappling:
            self.is_grappling = False
            for hook in grappling_hooks:
                hook.kill()
            self.can_grapple = True
            self.grapple_cooldown = 0

        angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        self.dash_direction = pygame.Vector2(
            math.cos(angle) * self.dash_speed,
            math.sin(angle) * self.dash_speed
        )
        
        self.is_dashing = True
        self.is_normal_dash = False
        self.dash_timer = self.dash_duration
        
        self.attack_box = pygame.Rect(
            self.rect.centerx - 30,
            self.rect.centery - 30,
            60, 60
        )
        self.attack_timer = self.attack_duration
        self.can_dash = False
        self.dash_cooldown = PLAYER_DASH_COOLDOWN
        
        if self.jumping:
            self.can_air_attack = False
            self.can_dash = False 