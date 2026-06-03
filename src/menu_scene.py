import pygame
from src.constants import *
from src import game_context as ctx
from src.draw_utils import (
    draw_text, GameButton,
    ACCENT_BLUE, TEXT_WHITE,
)


class MenuScene:
    def __init__(self):
        self.choice = None
        bg_raw  = pygame.image.load("assets/backgrounds/menubaru.png").convert()
        self.bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

        cx  = WIDTH  // 2
        cy  = HEIGHT // 2
        bw  = 340       
        bh  = 64        
        gap = 24         

        self._btn_mulai = GameButton(
            rect         = pygame.Rect(cx - bw // 2, cy + 40,        bw, bh),
            label        = "  MULAI",
            base_color   = (210, 145, 15),   
            hover_color  = (255, 195, 45),   
            border_color = (65,  30,  5),   
        )

        self._btn_petunjuk = GameButton(
            rect         = pygame.Rect(cx - bw // 2, cy + 40 + bh + gap, bw, bh),
            label        = "  PETUNJUK",
            base_color   = (30,  110, 200),  
            hover_color  = (60,  150, 255),  
            border_color = (10,  35,  80),  
        )

        self._btns = [
            ("mulai",    self._btn_mulai),
            ("petunjuk", self._btn_petunjuk),
        ]

    def handle(self, event):
        for key, btn in self._btns:
            if btn.is_clicked(event):
                self.choice = key
                return

    def draw(self):
        ctx.screen.blit(self.bg, (0, 0))

        cx = WIDTH // 2

        mp = pygame.mouse.get_pos()
        for _, btn in self._btns:
            btn.update(mp)
            btn.draw(ctx.screen)
