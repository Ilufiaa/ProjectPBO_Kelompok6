from __future__ import annotations
import os
import pygame
from src.constants import *
from src.element import ELEMENT_COLOR

BG_DARK       = (12,  14,  23)
BG_PANEL      = (20,  24,  40)
BG_CARD       = (28,  33,  52) 
BG_CARD_HOVER = (38,  44,  68) 
BG_CARD_SEL   = (50,  60,  95) 

TEXT_WHITE    = (255, 255, 255)
TEXT_MUTED    = (255, 255, 255)

HP_HIGH  = ( 72, 199, 142)
HP_MID   = (255, 193,  69)
HP_LOW   = (231,  76,  60)
HP_BG    = ( 40,  44,  60)

ACCENT_BLUE   = ( 88, 166, 255)
ACCENT_ORANGE = (255, 160,  60)
ACCENT_RED    = (231,  76,  60)
ACCENT_GREEN  = ( 72, 199, 142)
ACCENT_PURPLE = (163, 113, 247)

BTN_NORMAL  = ( 38,  44,  68)
BTN_HOVER   = ( 58,  68, 105)
BTN_ACTIVE  = ( 80,  95, 145)
BTN_DISABLE = ( 28,  33,  50)
BTN_BORDER  = ( 70,  80, 120)

CARD_RADIUS = 10
BTN_RADIUS  = 8
ANIM_FLASH  = 300

_ASSETS_FONTS    = "assets/fonts"
_LORA_BOLD       = os.path.join(_ASSETS_FONTS, "Lora-Variable.ttf")
_POPPINS_REGULAR = os.path.join(_ASSETS_FONTS, "Poppins-Regular.ttf")
_POPPINS_BOLD    = os.path.join(_ASSETS_FONTS, "Poppins-Bold.ttf")

_SYS_POPPINS_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_SYS_POPPINS_REG  = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"

_fonts: dict = {}

def _resolve(path, fallback_sys=""):
    if os.path.exists(path):
        return path
    if fallback_sys and os.path.exists(fallback_sys):
        return fallback_sys
    return None

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = ("body", size, bold)
    if key not in _fonts:
        path = _resolve(_POPPINS_BOLD if bold else _POPPINS_REGULAR,
                        _SYS_POPPINS_BOLD if bold else _SYS_POPPINS_REG)
        try:
            f = pygame.font.Font(path, size) if path else pygame.font.SysFont("freesans", size, bold=bold)
        except Exception:
            f = pygame.font.SysFont("freesans", size, bold=bold)
        _fonts[key] = f
    return _fonts[key]

def get_display_font(size: int, bold: bool = True) -> pygame.font.Font:
    key = ("display", size, bold)
    if key not in _fonts:
        path = _resolve(_LORA_BOLD, "")
        try:
            f = pygame.font.Font(path, size) if path else get_font(size, bold)
        except Exception:
            f = get_font(size, bold)
        _fonts[key] = f
    return _fonts[key]


def draw_rounded_rect(surf, rect, color, radius=CARD_RADIUS,
                      border_color=None, border_width=1):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)


def draw_text(surf, text, x, y, color=TEXT_WHITE, size=16,
              bold=False, anchor="topleft", display=False,
              shadow=False, shadow_color=(0, 0, 0)) -> pygame.Rect:
    font   = get_display_font(size, bold) if display else get_font(size, bold)
    if shadow:
        s = font.render(str(text), True, shadow_color)
        sr = s.get_rect(); setattr(sr, anchor, (x + 2, y + 3))
        surf.blit(s, sr)
    render = font.render(str(text), True, color)
    rect   = render.get_rect()
    setattr(rect, anchor, (x, y))
    surf.blit(render, rect)
    return rect


def draw_hp_bar(surf, x, y, width, height, current, maximum, show_text=True):
    ratio  = max(0.0, current / maximum) if maximum else 0.0
    filled = int(width * ratio)
    if ratio > 0.5:    bar_col = HP_HIGH
    elif ratio > 0.25: bar_col = HP_MID
    else:              bar_col = HP_LOW
    draw_rounded_rect(surf, pygame.Rect(x, y, width, height), HP_BG, radius=height // 2)
    if filled > 0:
        draw_rounded_rect(surf, pygame.Rect(x, y, filled, height), bar_col, radius=height // 2)
    if show_text:
        draw_text(surf, f"{current}/{maximum}", x + width + 8, y, TEXT_MUTED, size=13, anchor="midleft")


def draw_element_badge(surf, element_name, cx, cy):
    color = ELEMENT_COLOR.get(element_name, TEXT_MUTED)
    rect  = pygame.Rect(cx - 44, cy - 11, 88, 22)
    dark  = tuple(max(0, c // 3) for c in color)
    draw_rounded_rect(surf, rect, dark, radius=11, border_color=color, border_width=1)
    draw_text(surf, element_name, cx, cy, color, size=12, bold=True, anchor="center")


def draw_card(surf, rect, selected=False, hovered=False, dead=False, flash_alpha=0):
    if dead:             col = (18, 20, 32)
    elif selected:       col = BG_CARD_SEL
    elif hovered:        col = BG_CARD_HOVER
    else:                col = BG_CARD
    border = ACCENT_BLUE if selected else BTN_BORDER
    draw_rounded_rect(surf, rect, col, radius=CARD_RADIUS, border_color=border)
    if flash_alpha > 0:
        flash = pygame.Surface(rect.size, pygame.SRCALPHA)
        flash.fill((231, 76, 60, min(flash_alpha, 160)))
        surf.blit(flash, rect.topleft)


class UIButton:
    def __init__(self, rect: pygame.Rect, label: str,
                 sub_label: str = "", color=BTN_NORMAL, disabled: bool = False):
        self.rect      = rect
        self.label     = label
        self.sub_label = sub_label
        self.color     = color
        self.disabled  = disabled
        self._hovered  = False

    def update(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos) and not self.disabled

    def draw(self, surf):
        if self.disabled:
            col, border, tcol = BTN_DISABLE, (40, 48, 75), TEXT_MUTED
        elif self._hovered:
            col, border, tcol = BTN_HOVER, ACCENT_BLUE, TEXT_WHITE
        else:
            col, border, tcol = self.color, BTN_BORDER, TEXT_WHITE
        draw_rounded_rect(surf, self.rect, col, radius=BTN_RADIUS, border_color=border)
        cx = self.rect.centerx
        if self.sub_label:
            draw_text(surf, self.label,     cx, self.rect.centery - 9,  tcol,       size=15, bold=True, display=True, anchor="center")
            draw_text(surf, self.sub_label, cx, self.rect.centery + 10, TEXT_MUTED, size=11,                          anchor="center")
        else:
            draw_text(surf, self.label, cx, self.rect.centery, tcol, size=15, bold=True, display=True, anchor="center")

    def is_clicked(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
            and not self.disabled
        )
    
class GameButton:
    """
    Tombol bergaya game: pill-shape, outline tebal, efek 3D (highlight atas,
    bayangan bawah), teks dengan outline.
    """

    def __init__(self, rect: pygame.Rect, label: str,
                 base_color=(210, 150, 20),
                 hover_color=(255, 195, 50),
                 border_color=(65, 30, 5)):
        self.rect         = rect
        self.label        = label
        self.base_color   = base_color
        self.hover_color  = hover_color
        self.border_color = border_color
        self._hovered     = False

    @staticmethod
    def _lighten(c, a=40): return tuple(min(255, x + a) for x in c)
    @staticmethod
    def _darken(c, a=40):  return tuple(max(0,   x - a) for x in c)

    def update(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf: pygame.Surface):
        col    = self.hover_color if self._hovered else self.base_color
        r      = self.rect
        radius = r.height // 2          

        sh_surf = pygame.Surface((r.width + 4, r.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh_surf, (0, 0, 0, 90),
                         sh_surf.get_rect(), border_radius=radius + 2)
        surf.blit(sh_surf, (r.x - 2, r.y + 6))

        br = r.inflate(10, 10)
        pygame.draw.rect(surf, self.border_color, br, border_radius=radius + 5)

        pygame.draw.rect(surf, col, r, border_radius=radius)

        dark_col = self._darken(col, 45)
        bot_h    = r.height // 2
        bot_surf = pygame.Surface((r.width, bot_h), pygame.SRCALPHA)
        pygame.draw.rect(bot_surf, (*dark_col, 210),
                         bot_surf.get_rect(),
                         border_bottom_left_radius=radius,
                         border_bottom_right_radius=radius)
        surf.blit(bot_surf, (r.x, r.y + bot_h))

        sh_h     = r.height // 3
        shine_s  = pygame.Surface((r.width - 24, sh_h), pygame.SRCALPHA)
        pygame.draw.rect(shine_s, (255, 255, 255, 75),
                         shine_s.get_rect(), border_radius=sh_h // 2)
        surf.blit(shine_s, (r.x + 12, r.y + 6))

        cx, cy = r.center
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2),
                       (-2, 0),  (2, 0),  (0, -2), (0, 2)]:
            draw_text(surf, self.label, cx + dx, cy + dy,
                      self.border_color, size=20, bold=True,
                      display=True, anchor="center")
        draw_text(surf, self.label, cx, cy,
                  (255, 252, 220), size=20, bold=True,
                  display=True, anchor="center")

    def is_clicked(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
