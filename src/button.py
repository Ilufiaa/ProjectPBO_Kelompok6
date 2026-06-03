import pygame
from src.constants import *
from src import game_context as ctx

class Button:
    def __init__(self, x, y, w, h, text, disabled=False):
        self.rect     = pygame.Rect(x, y, w, h)
        self.text     = text
        self.disabled = disabled

    def draw(self):
        mouse = pygame.mouse.get_pos()
        if self.disabled:
            color = GRAY
        elif self.rect.collidepoint(mouse):
            color = YELLOW
        else:
            color = WHITE

        pygame.draw.rect(ctx.screen, color, self.rect, border_radius=10)
        pygame.draw.rect(ctx.screen, BLACK, self.rect, 2, border_radius=10)
        lbl = ctx.font.render(self.text, True, BLACK)
        ctx.screen.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.disabled