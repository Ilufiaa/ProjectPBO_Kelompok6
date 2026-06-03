import pygame
from src.constants import *
from src import game_context as ctx

class PetunjukScene:
    def __init__(self):
        self.done = False

        img_raw   = pygame.image.load("assets/backgrounds/elemenguide.png").convert_alpha()
        self.img  = pygame.transform.scale(img_raw, (WIDTH, HEIGHT))
        self.btn_back = pygame.Rect(20, 20, 110, 38)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:     
                self.done = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.collidepoint(event.pos):  
                self.done = True

    def draw(self):
        ctx.screen.blit(self.img, (0, 0))
        mouse   = pygame.mouse.get_pos()
        hovered = self.btn_back.collidepoint(mouse)
        color   = YELLOW if hovered else WHITE

        pygame.draw.rect(ctx.screen, (30, 30, 50), self.btn_back, border_radius=8)
        pygame.draw.rect(ctx.screen, color, self.btn_back, 2, border_radius=8)

        label = ctx.font.render("Kembali", True, color)
        ctx.screen.blit(label, label.get_rect(center=self.btn_back.center))