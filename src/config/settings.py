import pygame

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

# Configurações do jogador
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = -15
PLAYER_DASH_SPEED = 20
PLAYER_DASH_DURATION = 10
PLAYER_DASH_COOLDOWN = 120
PLAYER_ATTACK_DURATION = 5

# Configurações do grappling hook
HOOK_SPEED = 15
HOOK_MAX_DISTANCE = 500
HOOK_ROPE_SPEED = 15
HOOK_COOLDOWN = 30

# Configurações do inimigo
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30
ENEMY_SPEED = 2

# Configurações da moeda
COIN_SIZE = 15
COIN_ANIMATION_SPEED = 0.1
COIN_ANIMATION_RANGE = 3

# Configurações da mira
CROSSHAIR_SIZE = 40
CROSSHAIR_THICKNESS = 3

# Lista de plataformas
PLATFORM_LIST = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Chão
    (50, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 1
    (300, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 2
    (550, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 3
    (800, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 4
    (1050, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 5
    (1300, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 6
    (1550, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 7
    (1800, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 8
    (2050, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 9
    (2300, SCREEN_HEIGHT - 200, 200, 20),  # Plataforma 10
] 