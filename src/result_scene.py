import pygame
from src.constants import *
from src import game_context as ctx
from src.draw_utils import (
    draw_text, draw_rounded_rect, UIButton,
    BG_DARK, BG_PANEL, TEXT_WHITE, TEXT_MUTED,
    ACCENT_GREEN, ACCENT_RED, BTN_ACTIVE, BTN_NORMAL, CARD_RADIUS,
)


class ResultScene:
    def __init__(self, player_won: bool):
        self.player_won = player_won
        self.done       = False
        self.choice     = None
        cx = WIDTH // 2
        cy = HEIGHT // 2
        self._again_btn = UIButton(pygame.Rect(cx - 120, cy + 80, 240, 54), "  Main Lagi", color=BTN_ACTIVE)
        self._quit_btn  = UIButton(pygame.Rect(cx - 120, cy + 148, 240, 54), "  Keluar",   color=BTN_NORMAL)

    def handle(self, event):
        if self._again_btn.is_clicked(event):
            self.choice = "again"; self.done = True
        if self._quit_btn.is_clicked(event):
            self.choice = "quit";  self.done = True

    def draw(self):
        ctx.screen.fill(BG_DARK)
        W, H = WIDTH, HEIGHT
        col     = ACCENT_GREEN if self.player_won else ACCENT_RED
        heading = "  KEMENANGAN!" if self.player_won else "  KEKALAHAN"
        sub     = ("Tim kamu berhasil mengalahkan semua musuh!"
                   if self.player_won else "Seluruh tim kamu telah dikalahkan.")
        panel = pygame.Rect(W // 2 - 300, H // 2 - 160, 600, 360)
        draw_rounded_rect(ctx.screen, panel, BG_PANEL, radius=18, border_color=col, border_width=2)
        draw_text(ctx.screen, heading, W // 2, H // 2 - 110, col, size=50, bold=True, display=True, anchor="center")
        draw_text(ctx.screen, sub,     W // 2, H // 2 - 40,  TEXT_MUTED, size=17, anchor="center")
        mp = pygame.mouse.get_pos()
        self._again_btn.update(mp); self._again_btn.draw(ctx.screen)
        self._quit_btn.update(mp);  self._quit_btn.draw(ctx.screen)
