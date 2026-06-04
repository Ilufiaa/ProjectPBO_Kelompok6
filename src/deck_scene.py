import math
import pygame
from src.constants import *
from src import game_context as ctx
from src.roster import ALL_CHARS, ROLE_COLOR, ROLE_ICON
from src.element import ELEMENT_COLOR
from src.base_scene import BaseScene
from src.draw_utils import (
    draw_text, draw_rounded_rect, UIButton,
    BG_DARK, BG_PANEL, BG_CARD, BG_CARD_HOVER, BG_CARD_SEL,
    TEXT_WHITE, TEXT_MUTED,
    ACCENT_GREEN, ACCENT_BLUE, ACCENT_RED, ACCENT_ORANGE,
    BTN_NORMAL, BTN_ACTIVE, BTN_BORDER,
    HP_BG, HP_HIGH, HP_MID, HP_LOW,
    CARD_RADIUS, get_font,
)
from src.character import _load_image


SIDEBAR_W   = 300
GRID_L      = 16
GRID_R      = WIDTH - SIDEBAR_W - 8
GRID_W      = GRID_R - GRID_L

COLS        = 2
PER_PAGE    = 8
ROWS        = PER_PAGE // COLS         

GAP_X       = 12
GAP_Y       = 10
HEADER_H    = 62
FOOTER_H    = 50                        

_CARD_AREA  = HEIGHT - HEADER_H - FOOTER_H - 8
CARD_H      = (_CARD_AREA - (ROWS - 1) * GAP_Y) // ROWS   
CARD_W      = (GRID_W - (COLS - 1) * GAP_X) // COLS       
THUMB_MAX   = min(CARD_H - 12, 130)    


_MAX_HP_REF = max(cd["hp"] for cd in ALL_CHARS) if ALL_CHARS else 600


class DeckScene(BaseScene):
    def __init__(self):
        super().__init__()  
        self.picked: list = []
        self.go_back      = False
        self._page        = 0
        self._num_pages   = math.ceil(len(ALL_CHARS) / PER_PAGE)

        self._thumbs = {}
        for cd in ALL_CHARS:
            img = _load_image(cd["image"])
            if img:
                s = min(THUMB_MAX / img.get_width(), THUMB_MAX / img.get_height())
                self._thumbs[cd["name"]] = pygame.transform.smoothscale(
                    img, (int(img.get_width() * s), int(img.get_height() * s)))

        self._card_rects = []
        for i in range(PER_PAGE):
            col = i % COLS
            row = i // COLS
            x   = GRID_L + col * (CARD_W + GAP_X)
            y   = HEADER_H + 4 + row * (CARD_H + GAP_Y)
            self._card_rects.append(pygame.Rect(x, y, CARD_W, CARD_H))

        pb_y = HEIGHT - FOOTER_H + (FOOTER_H - 34) // 2
        self._btn_prev = UIButton(
            pygame.Rect(GRID_L,          pb_y, 130, 34), "  Sebelumnya")
        self._btn_next = UIButton(
            pygame.Rect(GRID_L + 140,    pb_y, 130, 34), "Berikutnya  ")

        self.start_btn = UIButton(
            pygame.Rect(WIDTH - SIDEBAR_W + 10, HEIGHT - 66, SIDEBAR_W - 20, 52),
            "  START BATTLE", color=BTN_ACTIVE, disabled=True)

        self._back_btn = UIButton(
            pygame.Rect(8, 8, 120, 32), "  Kembali")
        
        bg_raw   = pygame.image.load("assets/backgrounds/deck.png").convert()
        self.bg  = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    def handle(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self._back_btn.is_clicked(event):
            self.go_back = True
            self.done    = True
            return

        if self._btn_prev.is_clicked(event):
            self._page = max(0, self._page - 1)
            return
        if self._btn_next.is_clicked(event):
            self._page = min(self._num_pages - 1, self._page + 1)
            return

        py = HEADER_H + 8
        for slot_i in range(3):
            slot_r = pygame.Rect(WIDTH - SIDEBAR_W + 6, py, SIDEBAR_W - 12, 148)
            xbtn   = pygame.Rect(slot_r.right - 26, slot_r.y + 6, 20, 20)
            if slot_i < len(self.picked) and xbtn.collidepoint(event.pos):
                self.picked.pop(slot_i)
                return
            py += 154

        if self.start_btn.is_clicked(event):
            if len(self.picked) == 3:
                self.done = True
            return

        page_start = self._page * PER_PAGE
        page_chars = ALL_CHARS[page_start : page_start + PER_PAGE]
        for i, rect in enumerate(self._card_rects):
            if i >= len(page_chars):
                break
            if rect.collidepoint(event.pos):
                cd = page_chars[i]
                if cd in self.picked:
                    self.picked.remove(cd)
                elif len(self.picked) < 3:
                    self.picked.append(cd)
                return

    def draw(self):
        ctx.screen.blit(self.bg, (0, 0))
        mouse = pygame.mouse.get_pos()

        pygame.draw.rect(ctx.screen, BG_PANEL,
                         (WIDTH - SIDEBAR_W, 0, SIDEBAR_W, HEIGHT))
        pygame.draw.line(ctx.screen, (40, 48, 75),
                         (WIDTH - SIDEBAR_W, 0), (WIDTH - SIDEBAR_W, HEIGHT), 1)

        pygame.draw.rect(ctx.screen, BG_PANEL, (0, 0, GRID_R, HEADER_H))
        pygame.draw.line(ctx.screen, (40, 48, 75),
                         (0, HEADER_H), (GRID_R, HEADER_H), 1)
        draw_text(ctx.screen, "PILIH 3 KARAKTER",
                  GRID_R // 2, 14, TEXT_WHITE, size=22, bold=True, display=True, anchor="center")
        count   = len(self.picked)
        cnt_col = ACCENT_GREEN if count == 3 else TEXT_MUTED
        draw_text(ctx.screen, f"{count} / 3 dipilih",
                  GRID_R // 2, 38, cnt_col, size=13, anchor="center")

        page_start = self._page * PER_PAGE
        page_chars = ALL_CHARS[page_start : page_start + PER_PAGE]

        for i, (cd, rect) in enumerate(zip(page_chars, self._card_rects)):
            in_picked = cd in self.picked
            hovered   = rect.collidepoint(mouse)

            if in_picked:  bg, border = BG_CARD_SEL,  ACCENT_GREEN
            elif hovered:  bg, border = BG_CARD_HOVER, ACCENT_BLUE
            else:          bg, border = BG_CARD,       BTN_BORDER

            card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (*bg, 180),  
                 card_surf.get_rect(), border_radius=CARD_RADIUS)
            pygame.draw.rect(card_surf, (*border, 255),
                 card_surf.get_rect(), width=1, border_radius=CARD_RADIUS)
            ctx.screen.blit(card_surf, rect.topleft)

            thumb = self._thumbs.get(cd["name"])
            if thumb:
                ty = rect.y + (CARD_H - thumb.get_height()) // 2
                tx = rect.right - thumb.get_width() - 12
                ctx.screen.blit(thumb, (tx, ty))

            if in_picked:
                idx  = self.picked.index(cd) + 1
                tick = pygame.Rect(rect.x + 6, rect.y + 6, 26, 26)
                draw_rounded_rect(ctx.screen, tick, ACCENT_GREEN, radius=13)
                draw_text(ctx.screen, str(idx),
                          tick.centerx, tick.centery,
                          (10, 14, 28), size=14, bold=True, anchor="center")

            ix = rect.x + 14   

            draw_text(ctx.screen, cd["name"],
                      ix, rect.y + 10, TEXT_WHITE, size=16, bold=True, display=True)

            ecol  = ELEMENT_COLOR.get(cd["element"].value, TEXT_MUTED)
            rcol  = ROLE_COLOR.get(cd["role"], TEXT_MUTED)
            edark = tuple(max(0, c // 3) for c in ecol)
            rdark = tuple(max(0, c // 3) for c in rcol)

            eb = pygame.Rect(ix, rect.y + 34, 80, 18)
            draw_rounded_rect(ctx.screen, eb, edark,
                              radius=9, border_color=ecol, border_width=1)
            draw_text(ctx.screen, cd["element"].value,
                      eb.centerx, eb.centery, ecol,
                      size=11, bold=True, anchor="center")

            rb = pygame.Rect(ix + 86, rect.y + 34, 88, 18)
            draw_rounded_rect(ctx.screen, rb, rdark,
                              radius=9, border_color=rcol, border_width=1)
            draw_text(ctx.screen, f"{ROLE_ICON.get(cd['role'],'')} {cd['role']}",
                      rb.centerx, rb.centery, rcol,
                      size=11, bold=True, anchor="center")

            draw_text(ctx.screen,
                      f"HP {cd['hp']}   ·   ATK {cd['attack']}   ·   DEF {cd['defense']}",
                      ix, rect.y + 62, TEXT_MUTED, size=11)

            sk      = cd["skill"]
            sk_icon = "" if sk["type"] == "heal" else ""
            draw_text(ctx.screen,
                      f"• {cd['basic']['name']}   ·   "
                      f"{sk_icon} {sk['name']}  (CD {sk['cooldown']})",
                      ix, rect.y + 82, TEXT_MUTED, size=11)
            draw_text(ctx.screen, f"  {sk['desc']}",
                      ix, rect.y + 100, (60, 72, 108), size=10)

        pygame.draw.rect(ctx.screen, BG_PANEL,
                         (0, HEIGHT - FOOTER_H, GRID_R, FOOTER_H))
        pygame.draw.line(ctx.screen, (40, 48, 75),
                         (0, HEIGHT - FOOTER_H), (GRID_R, HEIGHT - FOOTER_H), 1)

        self._btn_prev.disabled = (self._page == 0)
        self._btn_next.disabled = (self._page >= self._num_pages - 1)
        self._btn_prev.update(mouse)
        self._btn_next.update(mouse)
        self._btn_prev.draw(ctx.screen)
        self._btn_next.draw(ctx.screen)

        mid_footer_y = HEIGHT - FOOTER_H + FOOTER_H // 2
        draw_text(ctx.screen,
                  f"Halaman  {self._page + 1}  /  {self._num_pages}",
                  GRID_L + 290, mid_footer_y,
                  TEXT_MUTED, size=13, anchor="midleft")

        for p in range(self._num_pages):
            dot_x = GRID_L + 460 + p * 22
            col   = ACCENT_BLUE if p == self._page else (40, 50, 78)
            pygame.draw.circle(ctx.screen, col,
                               (dot_x, mid_footer_y), 6)
            if p == self._page:
                pygame.draw.circle(ctx.screen, ACCENT_BLUE,
                                   (dot_x, mid_footer_y), 6, 2)

        self._draw_sidebar(mouse)
        self.start_btn.disabled = (count != 3)
        self.start_btn.update(mouse)
        self.start_btn.draw(ctx.screen)

        self._back_btn.update(mouse)
        self._back_btn.draw(ctx.screen)

    def _draw_sidebar(self, mouse):
        py = HEADER_H + 8

        draw_text(ctx.screen, "TIM KAMU",
                  WIDTH - SIDEBAR_W // 2, HEADER_H // 2 - 4,
                  TEXT_MUTED, size=14, bold=True, display=True, anchor="center")

        for slot_i in range(3):
            slot_r = pygame.Rect(
                WIDTH - SIDEBAR_W + 6, py, SIDEBAR_W - 12, 148)
            draw_rounded_rect(ctx.screen, slot_r, BG_CARD,
                              radius=10, border_color=(40, 48, 75))

            if slot_i < len(self.picked):
                cd   = self.picked[slot_i]
                ecol = ELEMENT_COLOR.get(cd["element"].value, TEXT_MUTED)
                rcol = ROLE_COLOR.get(cd["role"], TEXT_MUTED)

                img = _load_image(cd["image"])
                if img:
                    s   = min(96 / img.get_width(), 96 / img.get_height())
                    big = pygame.transform.smoothscale(
                        img, (int(img.get_width()*s), int(img.get_height()*s)))
                    ctx.screen.blit(big, (
                        slot_r.right - big.get_width() - 8,
                        slot_r.y + (slot_r.h - big.get_height()) // 2))

                draw_text(ctx.screen, f"#{slot_i+1}",
                          slot_r.x + 10, slot_r.y + 8,
                          TEXT_MUTED, size=11, bold=True)
                draw_text(ctx.screen, cd["name"],
                          slot_r.x + 32, slot_r.y + 8,
                          TEXT_WHITE, size=14, bold=True)

                eb    = pygame.Rect(slot_r.x + 8, slot_r.y + 30, 72, 16)
                edark = tuple(max(0, c // 3) for c in ecol)
                draw_rounded_rect(ctx.screen, eb, edark,
                                  radius=8, border_color=ecol, border_width=1)
                draw_text(ctx.screen, cd["element"].value,
                          eb.centerx, eb.centery, ecol,
                          size=10, bold=True, anchor="center")

                rb    = pygame.Rect(slot_r.x + 86, slot_r.y + 30, 78, 16)
                rdark = tuple(max(0, c // 3) for c in rcol)
                draw_rounded_rect(ctx.screen, rb, rdark,
                                  radius=8, border_color=rcol, border_width=1)
                draw_text(ctx.screen,
                          f"{ROLE_ICON.get(cd['role'],'')} {cd['role']}",
                          rb.centerx, rb.centery, rcol,
                          size=10, bold=True, anchor="center")

                draw_text(ctx.screen,
                          f"HP {cd['hp']}   ATK {cd['attack']}   DEF {cd['defense']}",
                          slot_r.x + 8, slot_r.y + 54, TEXT_MUTED, size=11)

                sk_y = slot_r.y + 72
                draw_text(ctx.screen,
                          f"• {cd['basic']['name']}  (Basic Attack)",
                          slot_r.x + 8, sk_y, TEXT_MUTED, size=10)
                sk_y += 15
                skd  = cd["skill"]
                tag  = (f"+{skd['power']}HP"
                        if skd["type"] == "heal" else f"{skd['power']} dmg")
                draw_text(ctx.screen,
                          f"• {skd['name']}  {tag}  CD{skd['cooldown']}",
                          slot_r.x + 8, sk_y, TEXT_MUTED, size=10)
                sk_y += 14
                draw_text(ctx.screen, f"  {skd['desc']}",
                          slot_r.x + 8, sk_y, (70, 80, 110), size=10)

                xbtn = pygame.Rect(slot_r.right - 26, slot_r.y + 6, 20, 20)
                xcol = (220, 60, 60) if xbtn.collidepoint(mouse) else (140, 40, 40)
                draw_rounded_rect(ctx.screen, xbtn, xcol, radius=5)
                draw_text(ctx.screen, "",
                          xbtn.centerx, xbtn.centery,
                          TEXT_WHITE, size=12, bold=True, anchor="center")
            else:
                draw_text(ctx.screen, f"Slot {slot_i + 1}",
                          slot_r.x + 16, slot_r.centery - 10,
                          (50, 58, 88), size=13, bold=True)
                draw_text(ctx.screen, "— kosong —",
                          slot_r.x + 16, slot_r.centery + 8,
                          (40, 48, 72), size=11)

            py += 154