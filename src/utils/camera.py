import pygame
from src.config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

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