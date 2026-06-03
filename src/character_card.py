import pygame
from src.draw_utils import (
    draw_card, draw_text, draw_hp_bar, draw_element_badge,
    draw_rounded_rect, get_font,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, ACCENT_ORANGE, ACCENT_PURPLE,
    TEXT_MUTED, TEXT_WHITE, BTN_BORDER,
    CARD_RADIUS, ANIM_FLASH, BG_CARD,
)
from src.roster import ROLE_COLOR, ROLE_ICON
from src.element import ELEMENT_COLOR

CARD_W = 270
CARD_H = 210


class CharacterCard:
    W = CARD_W
    H = CARD_H

    def __init__(self, character, x, y):
        self.character = character
        self.rect      = pygame.Rect(x, y, self.W, self.H)
        self.selected  = False
        self.hovered   = False
        self._flash_ms = 0
        self._img_scaled = self._scale_img()

    def _scale_img(self):
        img = self.character.image
        if not img:
            return None
        max_s = 100
        iw, ih = img.get_size()
        s = min(max_s / iw, max_s / ih)
        return pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))

    def trigger_flash(self):
        self._flash_ms = ANIM_FLASH

    def update(self, dt, mouse_pos):
        if self._flash_ms > 0:
            self._flash_ms = max(0, self._flash_ms - dt)
        self.hovered = (self.rect.collidepoint(mouse_pos)
                        and self.character.is_alive())

    def draw(self, surf):
        c    = self.character
        dead = not c.is_alive()
        flash_alpha = int(200 * (self._flash_ms / ANIM_FLASH)) if self._flash_ms > 0 else 0
        draw_card(surf, self.rect,
                  selected=self.selected, hovered=self.hovered,
                  dead=dead, flash_alpha=flash_alpha)

        img = self._img_scaled
        if img:
            if dead:
                dark = img.copy()
                dark.fill((60, 60, 60, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(dark, (self.rect.right - img.get_width() - 6, self.rect.y + 6))
            else:
                surf.blit(img, (self.rect.right - img.get_width() - 6, self.rect.y + 6))

        if dead:
            draw_text(surf, "DEFEATED", self.rect.centerx, self.rect.centery,
                      ACCENT_RED, size=18, bold=True, anchor="center")
            return

        elem_name = c.element.value
        ecol  = ELEMENT_COLOR.get(elem_name, TEXT_MUTED)
        rcol  = ROLE_COLOR.get(c.role, TEXT_MUTED)

        draw_text(surf, c.name, self.rect.x + 10, self.rect.y + 8,
                  TEXT_WHITE, size=15, bold=True)

        ebadge = pygame.Rect(self.rect.x + 8, self.rect.y + 30, 80, 16)
        edark  = tuple(max(0, x // 3) for x in ecol)
        draw_rounded_rect(surf, ebadge, edark, radius=8, border_color=ecol, border_width=1)
        draw_text(surf, elem_name, ebadge.centerx, ebadge.centery,
                  ecol, size=11, bold=True, anchor="center")

        rbadge = pygame.Rect(self.rect.x + 94, self.rect.y + 30, 80, 16)
        rdark  = tuple(max(0, x // 3) for x in rcol)
        draw_rounded_rect(surf, rbadge, rdark, radius=8, border_color=rcol, border_width=1)
        draw_text(surf, f"{ROLE_ICON.get(c.role,'')} {c.role}",
                  rbadge.centerx, rbadge.centery,
                  rcol, size=11, bold=True, anchor="center")

        draw_text(surf, "HP", self.rect.x + 10, self.rect.y + 54, TEXT_MUTED, size=11)
        draw_hp_bar(surf,
                    self.rect.x + 10, self.rect.y + 68,
                    width=self.W - 16, height=10,
                    current=c.hp, maximum=c.max_hp, show_text=False)
        draw_text(surf, f"{c.hp} / {c.max_hp}",
                  self.rect.x + 10, self.rect.y + 82, TEXT_MUTED, size=11)

        draw_text(surf, f"ATK {c.attack}",
                  self.rect.x + 10, self.rect.y + 100, TEXT_MUTED, size=11)
        draw_text(surf, f"DEF {c.defense}",
                  self.rect.x + 90, self.rect.y + 100, TEXT_MUTED, size=11)

        sy = self.rect.y + 120
        for sk in c.skills:
            ready  = sk.is_ready()
            s_col  = ACCENT_BLUE if ready else TEXT_MUTED
            cd_lbl = "READY" if ready else f"CD {sk.cooldown}"
            tp_lbl = "♥" if sk.skill_type == "heal" else "⚔"
            draw_text(surf, f"{tp_lbl} {sk.name}",
                      self.rect.x + 10, sy, s_col, size=11)
            draw_text(surf, cd_lbl,
                      self.rect.right - 8, sy, s_col, size=11, anchor="topright")
            sy += 18

    def is_clicked(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
            and self.character.is_alive()
        )
