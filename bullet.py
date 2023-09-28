import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.bullet_width = 5
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)

        self.rect = pygame.Rect(0, 0, self.bullet_width, self.bullet_height)
        self.rect.midtop = ai_game.star_ship.rect.midtop

        self.y = float(self.rect.y)

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.bullet_color, self.rect)
