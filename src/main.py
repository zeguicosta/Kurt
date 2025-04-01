import pygame
import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import (
    screen, clock, FPS, font, WHITE, BLACK, SKY_BLUE,
    SCREEN_WIDTH, SCREEN_HEIGHT, PLATFORM_LIST
)
from src.utils.camera import Camera
from src.entities.player import Player
from src.entities.entities import Platform, Enemy, Coin, Crosshair, GrapplingHook

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
for i, p in enumerate(PLATFORM_LIST):
    platform = Platform(*p)
    all_sprites.add(platform)
    platforms.add(platform)
    
    # Adicionar inimigos em algumas plataformas (exceto no chão)
    if i > 0:
        # Adicionar 1 inimigo por plataforma (exceto no chão)
        enemy = Enemy(p[0] + p[2] // 2, p[1], platform, p[0], p[0] + p[2] - 30)
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
                for i, p in enumerate(PLATFORM_LIST):
                    platform = Platform(*p)
                    all_sprites.add(platform)
                    platforms.add(platform)
                    
                    # Adicionar inimigos em algumas plataformas (exceto no chão)
                    if i > 0:
                        # Adicionar 1 inimigo por plataforma (exceto no chão)
                        enemy = Enemy(p[0] + p[2] // 2, p[1], platform, p[0], p[0] + p[2] - 30)
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
                player.dash_attack(crosshair.rect.centerx, crosshair.rect.centery, grappling_hooks)
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