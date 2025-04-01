import pygame
import sys
import os
import random
import math

# Inicialização do Pygame
pygame.init()
pygame.mouse.set_visible(False)  # Esconder o cursor do mouse

# Configurações da tela
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Jogo de Plataforma")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)  # Azul mais claro
DARK_BLUE = (0, 0, 180)
GREEN = (34, 139, 34)  # Verde floresta
RED = (220, 20, 60)    # Vermelho crimson
YELLOW = (255, 215, 0)  # Ouro
SKY_BLUE = (135, 206, 235)

# Clock para controle de FPS
clock = pygame.time.Clock()
FPS = 60

# Carregar fontes
font = pygame.font.SysFont('Arial', 24)

# Classe da câmera
class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scroll = pygame.Vector2(0, 0)
        self.target_scroll = pygame.Vector2(0, 0)
        self.smooth_factor = 0.1  # Fator de suavização (menor = mais suave)

    def apply(self, entity):
        return entity.rect.move(self.scroll)

    def apply_point(self, point):
        return point + self.scroll

    def update(self, target):
        # Calcular a posição desejada da câmera
        self.target_scroll.x = -(target.rect.centerx - self.width // 2)
        self.target_scroll.y = -(target.rect.centery - self.height // 2)
        
        # Interpolar suavemente entre a posição atual e a desejada
        self.scroll.x += (self.target_scroll.x - self.scroll.x) * self.smooth_factor
        self.scroll.y += (self.target_scroll.y - self.scroll.y) * self.smooth_factor

# Classe do jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Criar um retângulo simples para o jogador
        self.width, self.height = 30, 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(BLUE)
        
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumping = False
        self.speed = 5
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
        self.dash_speed = 20
        self.dash_duration = 10  # frames
        self.dash_timer = 0
        self.can_dash = True
        self.dash_cooldown = 0
        self.attack_box = None
        self.attack_duration = 5  # frames
        self.attack_timer = 0
        self.can_air_attack = True
        self.dash_direction = pygame.Vector2(0, 0)  # Nova variável para direção do dash
        self.attack_button_pressed = False  # Nova variável para controlar o estado do botão de ataque

    def update(self, platforms, enemies, coins):
        dx = 0
        dy = 0

        # Processar teclas (WASD)
        key = pygame.key.get_pressed()
        if not self.is_grappling and not self.is_dashing:  # Só permite movimento quando não está sendo puxado ou dashing
            if key[pygame.K_a]:  # A para esquerda
                dx -= self.speed
                self.facing_right = False
            if key[pygame.K_d]:  # D para direita
                dx += self.speed
                self.facing_right = True
            if key[pygame.K_SPACE] and not self.jumping:  # Barra de espaço para pular
                self.vel_y = -15
                self.jumping = True
            if key[pygame.K_LSHIFT] and self.can_dash:  # Shift para dash normal
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
                self.dash_cooldown = 120  # 2 segundos de cooldown
                self.vel_y = 0
                # Restaurar opacidade normal
                self.image = self.original_image.copy()
            else:
                # Aplicar movimento do dash
                self.rect.x += self.dash_direction.x
                self.rect.y += self.dash_direction.y
                
                # Atualizar posição da caixa de ataque
                if self.attack_box:
                    self.attack_box.center = self.rect.center
                    
                    # Verificar colisão com inimigos durante o ataque
                    for enemy in enemies:
                        if self.attack_box.colliderect(enemy.rect):
                            enemy.kill()
                            self.score += 20  # Pontuação extra por matar inimigos

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
            # Colisão horizontal
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            
            # Colisão vertical
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # Verifica se está caindo (colisão por cima da plataforma)
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.jumping = False
                    # Resetar cooldown do dash e permitir ataque no ar ao tocar no chão
                    self.can_dash = True
                    self.dash_cooldown = 0
                    self.can_air_attack = True
                # Verifica se está pulando (colisão por baixo da plataforma)
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                dy = 0

        # Estado de invencibilidade (após dano)
        if self.invincible and not self.is_dashing:  # Não piscar durante o dash
            self.invincible_timer += 1
            if self.invincible_timer > 60:  # 1 segundo de invencibilidade
                self.invincible = False
                self.invincible_timer = 0
                self.image = self.original_image.copy()
            else:
                # Piscar durante invencibilidade
                if self.invincible_timer % 10 < 5:
                    self.image.fill(WHITE)
                else:
                    self.image = self.original_image.copy()
        
        # Verificar colisão com inimigos
        if not self.invincible and not self.is_dashing:  # Não tomar dano durante o dash
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    self.lives -= 1
                    self.invincible = True
                    # Knockback
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
        # Calcular direção do dash baseado na direção que o jogador está olhando
        self.dash_direction = pygame.Vector2(self.dash_speed if self.facing_right else -self.dash_speed, 0)
        
        # Iniciar dash
        self.is_dashing = True
        self.is_normal_dash = True
        self.dash_timer = self.dash_duration
        
        # Tornar o jogador mais transparente durante o dash
        self.image = self.original_image.copy()
        self.image.set_alpha(128)  # 50% de opacidade
        
        self.can_dash = False
        self.dash_cooldown = 120  # 2 segundos de cooldown

    def dash_attack(self, target_x, target_y):
        if not self.can_dash or (self.jumping and not self.can_air_attack):
            return

        # Cancelar hook se estiver sendo puxado
        if self.is_grappling:
            self.is_grappling = False
            for hook in grappling_hooks:
                hook.kill()
            self.can_grapple = True
            self.grapple_cooldown = 0

        # Calcular direção do dash
        angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        self.dash_direction = pygame.Vector2(
            math.cos(angle) * self.dash_speed,
            math.sin(angle) * self.dash_speed
        )
        
        # Iniciar dash
        self.is_dashing = True
        self.is_normal_dash = False
        self.dash_timer = self.dash_duration
        
        # Criar caixa de ataque maior
        self.attack_box = pygame.Rect(
            self.rect.centerx - 30,
            self.rect.centery - 30,
            60, 60
        )
        self.attack_timer = self.attack_duration
        self.can_dash = False
        self.dash_cooldown = 120  # 2 segundos de cooldown
        
        # Se estiver no ar, desabilitar ataque no ar
        if self.jumping:
            self.can_air_attack = False
            self.can_dash = False  # Desabilita o dash até tocar no chão

# Classe da plataforma
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Classe do inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform, min_x, max_x):
        super().__init__()
        self.width, self.height = 30, 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height
        self.platform = platform
        self.speed = 2
        self.direction = 1
        self.min_x = min_x
        self.max_x = max_x
    
    def update(self):
        self.rect.x += self.speed * self.direction
        
        # Mudar direção ao atingir limites
        if self.rect.right > self.max_x or self.rect.left < self.min_x:
            self.direction *= -1

# Classe da moeda
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 15
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_counter = 0
        self.original_y = y
    
    def update(self):
        # Animação de flutuação
        self.animation_counter += 0.1
        self.rect.y = self.original_y + int(math.sin(self.animation_counter) * 3)

# Classe da mira
class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 40  # Aumentado de 20 para 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Desenhar a mira (círculo com cruz)
        pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2, 3)  # Aumentado espessura
        pygame.draw.line(self.image, WHITE, (0, self.size // 2), (self.size, self.size // 2), 3)  # Aumentado espessura
        pygame.draw.line(self.image, WHITE, (self.size // 2, 0), (self.size // 2, self.size), 3)  # Aumentado espessura
        
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()

    def update(self, camera):
        # Atualizar posição considerando o offset da câmera
        mouse_pos = pygame.mouse.get_pos()
        world_pos = pygame.Vector2(mouse_pos) - camera.scroll
        self.rect.center = world_pos

# Classe do Grappling Hook
class GrapplingHook(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, player):
        super().__init__()
        self.player = player
        self.width, self.height = 10, 10
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Calcular direção e velocidade
        angle = math.atan2(target_y - y, target_x - x)
        self.speed = 15
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        # Limite de distância
        self.max_distance = 500
        self.initial_x = x
        self.initial_y = y
        
        # Estado do hook
        self.attached = False
        self.attached_point = None
        self.rope_length = 0
        self.rope_speed = 15  # Aumentado para ser mais rápido

    def update(self, platforms):
        if not self.attached:
            # Mover o hook
            self.rect.x += self.dx
            self.rect.y += self.dy
            
            # Verificar distância máxima
            distance = math.sqrt((self.rect.centerx - self.initial_x)**2 + 
                               (self.rect.centery - self.initial_y)**2)
            if distance > self.max_distance:
                self.kill()
                self.player.can_grapple = True  # Resetar o cooldown
                self.player.is_grappling = False
                return
            
            # Verificar colisão com plataformas
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.attached = True
                    self.attached_point = (self.rect.centerx, self.rect.centery)
                    self.player.is_grappling = True
                    return
        else:
            # Puxar o jogador em direção ao ponto de conexão
            dx = self.attached_point[0] - self.player.rect.centerx
            dy = self.attached_point[1] - self.player.rect.centery
            
            # Normalizar o vetor de direção
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                # Aplicar força de puxão
                dx = dx / distance * self.rope_speed
                dy = dy / distance * self.rope_speed
                
                # Mover o jogador
                self.player.rect.x += dx
                self.player.rect.y += dy
                
                # Resetar velocidade vertical quando conectado
                self.player.vel_y = 0
                self.player.jumping = False
            
            # Verificar se o jogador chegou perto o suficiente do ponto de conexão
            if distance < 5:
                self.kill()
                self.player.can_grapple = True  # Resetar o cooldown
                self.player.is_grappling = False

# Criar sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
grappling_hooks = pygame.sprite.Group()

# Criar câmera
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# Criar jogador
player = Player(100, 100)
all_sprites.add(player)

# Criar mira
crosshair = Crosshair()
all_sprites.add(crosshair)

# Criar plataformas
platform_list = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Chão
    (100, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 1
    (400, SCREEN_HEIGHT - 300, 200, 20),  # Plataforma 2
    (200, SCREEN_HEIGHT - 400, 200, 20),  # Plataforma 3
    (600, SCREEN_HEIGHT - 250, 200, 20),  # Plataforma 4
    (800, SCREEN_HEIGHT - 350, 200, 20),  # Plataforma 5
    (1000, SCREEN_HEIGHT - 450, 200, 20),  # Plataforma 6
    (1200, SCREEN_HEIGHT - 300, 200, 20),  # Plataforma 7
    (1400, SCREEN_HEIGHT - 400, 200, 20),  # Plataforma 8
    (1600, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 9
    (1800, SCREEN_HEIGHT - 350, 200, 20),  # Plataforma 10
    (2000, SCREEN_HEIGHT - 500, 200, 20),  # Plataforma 11
    (2200, SCREEN_HEIGHT - 250, 200, 20),  # Plataforma 12
    (2400, SCREEN_HEIGHT - 400, 200, 20),  # Plataforma 13
    (2600, SCREEN_HEIGHT - 300, 200, 20),  # Plataforma 14
    (2800, SCREEN_HEIGHT - 450, 200, 20),  # Plataforma 15
]

for i, p in enumerate(platform_list):
    platform = Platform(*p)
    all_sprites.add(platform)
    platforms.add(platform)
    
    # Adicionar inimigos em algumas plataformas (exceto no chão)
    if i > 0:
        # Adicionar 2 inimigos por plataforma (exceto no chão)
        for j in range(2):
            enemy = Enemy(p[0] + (j+1) * (p[2] // 3), p[1], platform, p[0], p[0] + p[2] - 30)
            all_sprites.add(enemy)
            enemies.add(enemy)
    
    # Adicionar moedas em cada plataforma
    for j in range(3):  # 3 moedas por plataforma
        coin_x = p[0] + (j+1) * (p[2] // 4)
        coin_y = p[1] - 30
        coin = Coin(coin_x, coin_y)
        all_sprites.add(coin)
        coins.add(coin)

# Loop principal do jogo
running = True
game_over = False

while running:
    # Limitar FPS
    clock.tick(FPS)
    
    # Processar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC para sair
                running = False
            elif event.key == pygame.K_r:  # R para reiniciar
                # Reiniciar jogo
                all_sprites.empty()
                platforms.empty()
                enemies.empty()
                coins.empty()
                
                # Recriar jogador
                player = Player(100, 100)
                all_sprites.add(player)
                
                # Recriar mira
                crosshair = Crosshair()
                all_sprites.add(crosshair)
                
                # Recriar plataformas, inimigos e moedas
                for i, p in enumerate(platform_list):
                    platform = Platform(*p)
                    all_sprites.add(platform)
                    platforms.add(platform)
                    
                    # Adicionar inimigos em algumas plataformas (exceto no chão)
                    if i > 0:
                        # Adicionar 2 inimigos por plataforma (exceto no chão)
                        for j in range(2):
                            enemy = Enemy(p[0] + (j+1) * (p[2] // 3), p[1], platform, p[0], p[0] + p[2] - 30)
                            all_sprites.add(enemy)
                            enemies.add(enemy)
                    
                    # Adicionar moedas em cada plataforma
                    for j in range(3):  # 3 moedas por plataforma
                        coin_x = p[0] + (j+1) * (p[2] // 4)
                        coin_y = p[1] - 30
                        coin = Coin(coin_x, coin_y)
                        all_sprites.add(coin)
                        coins.add(coin)
                
                grappling_hooks.empty()  # Limpar os hooks ao reiniciar
                player.can_grapple = True
                player.grapple_cooldown = 0
                game_over = False
            elif event.key == pygame.K_s and player.can_grapple:  # S para atirar o grappling hook
                # Criar novo grappling hook na direção da mira
                hook = GrapplingHook(
                    player.rect.centerx,
                    player.rect.centery,
                    crosshair.rect.centerx,
                    crosshair.rect.centery,
                    player
                )
                all_sprites.add(hook)
                grappling_hooks.add(hook)
                player.can_grapple = False
                player.grapple_cooldown = 30  # 0.5 segundos de cooldown
                player.is_grappling = False  # Resetar o estado de grappling
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not player.attack_button_pressed:  # Botão esquerdo do mouse para dash attack
                player.attack_button_pressed = True
                player.dash_attack(crosshair.rect.centerx, crosshair.rect.centery)
            elif event.button == 3 and player.can_grapple:  # Botão direito do mouse para grappling hook
                # Criar novo grappling hook na direção da mira
                hook = GrapplingHook(
                    player.rect.centerx,
                    player.rect.centery,
                    crosshair.rect.centerx,
                    crosshair.rect.centery,
                    player
                )
                all_sprites.add(hook)
                grappling_hooks.add(hook)
                player.can_grapple = False
                player.grapple_cooldown = 30  # 0.5 segundos de cooldown
                player.is_grappling = False  # Resetar o estado de grappling
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Botão esquerdo do mouse
                player.attack_button_pressed = False
    
    if not game_over:
        # Atualizar
        player.update(platforms, enemies, coins)
        
        enemies.update()
        coins.update()
        crosshair.update(camera)
        grappling_hooks.update(platforms)
        
        # Verificar fim de jogo
        if player.lives <= 0:
            game_over = True
    
    # Renderizar
    # Fundo mais simples
    screen.fill(SKY_BLUE)
    
    # Atualizar câmera
    camera.update(player)
    
    # Desenhar linhas dos grappling hooks com offset da câmera
    for hook in grappling_hooks:
        if hook.attached:
            start_pos = camera.apply_point(pygame.Vector2(player.rect.centerx, player.rect.centery))
            end_pos = camera.apply_point(pygame.Vector2(hook.attached_point[0], hook.attached_point[1]))
            pygame.draw.line(screen, WHITE, start_pos, end_pos, 2)
    
    # Desenhar sprites com offset da câmera
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    
    # Desenhar UI (pontuação e vidas) sem offset da câmera
    score_text = font.render(f'Pontuação: {player.score}', True, WHITE)
    lives_text = font.render(f'Vidas: {player.lives}', True, WHITE)
    
    # Adicionar fundo simples para o texto
    pygame.draw.rect(screen, BLACK, (5, 5, score_text.get_width() + 10, score_text.get_height() + 5))
    pygame.draw.rect(screen, BLACK, (5, 35, lives_text.get_width() + 10, lives_text.get_height() + 5))
    
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    
    # Mostrar tela de game over
    if game_over:
        # Retângulo simples para o game over
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3, 
                                          SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        
        go_text = font.render('GAME OVER - Pressione R para reiniciar', True, WHITE)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(go_text, go_rect)
    
    # Atualizar tela
    pygame.display.flip()

# Finalizar Pygame
pygame.quit()
sys.exit() 