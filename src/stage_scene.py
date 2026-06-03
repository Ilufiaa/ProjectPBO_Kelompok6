import pygame
import math
from src.constants import *
from src import game_context as ctx
from src.save_data import load_save, MAX_LEVEL
from src.roster import STAGE_ENEMIES, ROLE_COLOR, ROLE_ICON
from src.element import ELEMENT_COLOR
from src.draw_utils import (
    draw_text, draw_rounded_rect, UIButton,
    BG_DARK, BG_PANEL, BG_CARD, BG_CARD_HOVER,
    TEXT_WHITE, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED,
    ACCENT_ORANGE, BTN_ACTIVE, BTN_BORDER, CARD_RADIUS,
    draw_hp_bar,
)
from src.character import _load_image

NODE_POSITIONS = [
    (180, 520),
    (380, 360),
    (580, 460),
    (780, 280),
    (980, 380),
]
NODE_R = 46

C_BG_TOP    = (18, 22, 38)
C_BG_BOT    = (10, 14, 28)
C_PATH      = (50, 60, 90)
C_PATH_D    = (30, 36, 60)
C_UNLOCK    = (88, 166, 255)
C_UNLOCK_D  = (40,  80, 160)
C_LOCK      = (50,  55,  75)
C_LOCK_D    = (30,  34,  55)
C_DONE      = (72, 199, 142)
C_DONE_D    = (30, 100,  60)
C_STAR      = (255, 210,   0)

STAGE_NAMES = {1: "Gerbang Awal", 2: "Hutan Terlarang", 3: "Reruntuhan Kuno",
               4: "Puncak Badai", 5: "Istana Akhir"}
STAGE_DIFF  = {1: "Mudah", 2: "Normal", 3: "Sedang", 4: "Sulit", 5: "Sangat Sulit"}
DIFF_COLOR  = {
    "Mudah":        ACCENT_GREEN,
    "Normal":       (88, 166, 255),
    "Sedang":       ACCENT_ORANGE,
    "Sulit":        ACCENT_RED,
    "Sangat Sulit": (200, 50, 200),
}

PREVIEW_W = 340


def _star_points(cx, cy, r_out, r_in, n=5):
    pts = []
    for i in range(n * 2):
        r   = r_out if i % 2 == 0 else r_in
        ang = math.radians(-90 + i * 180 / n)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _draw_path(surf, p1, p2, done=False):
    x1, y1 = p1; x2, y2 = p2
    dist  = math.hypot(x2-x1, y2-y1)
    steps = int(dist // 16)
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 0.5) / steps
        ax = int(x1 + (x2-x1)*t0); ay = int(y1 + (y2-y1)*t0)
        bx = int(x1 + (x2-x1)*t1); by = int(y1 + (y2-y1)*t1)
        col = C_DONE if done else C_PATH
        pygame.draw.line(surf, C_PATH_D, (ax, ay), (bx, by), 5)
        pygame.draw.line(surf, col,      (ax, ay), (bx, by), 2)


def _draw_node(surf, cx, cy, level, state, hover, font_m):
    r = NODE_R + 5 if hover and state != "locked" else NODE_R
    if state == "unlocked" and hover:
        glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (88, 166, 255, 40), (r*2, r*2), r*2)
        surf.blit(glow, (cx - r*2, cy - r*2))

    if state == "done":
        outer, inner = C_DONE_D, C_DONE
    elif state == "unlocked":
        outer, inner = C_UNLOCK_D, C_UNLOCK
    else:
        outer, inner = C_LOCK_D, C_LOCK

    pygame.draw.circle(surf, outer, (cx, cy), r)
    pygame.draw.circle(surf, inner, (cx, cy), r - 4)
    pygame.draw.circle(surf, (255,255,255,20), (cx, cy), r - 4, 1)

    if state == "locked":
        lbl = font_m.render("", True, (120, 125, 145))
    else:
        lbl = font_m.render(str(level), True, (10, 14, 28))
    surf.blit(lbl, lbl.get_rect(center=(cx, cy)))

    if state == "done":
        for i in range(3):
            sx = cx - 16 + i * 16
            sy = cy + NODE_R + 8
            pygame.draw.polygon(surf, C_STAR, _star_points(sx, sy, 7, 3))


class StageScene:
    def __init__(self):
        self.chosen   = None
        self.done     = False
        self.go_back  = False
        save          = load_save()
        self.unlocked = save["unlocked"]
        self._hovered_stage = None
        self._thumb_cache = {}
        self._preload_thumbs()
        self._back_btn = UIButton(pygame.Rect(8, 8, 120, 32), "  Kembali")

        bg_raw   = pygame.image.load("assets/backgrounds/menustage.png").convert()
        self.bg  = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    def _preload_thumbs(self):
        for stage, enemies in STAGE_ENEMIES.items():
            self._thumb_cache[stage] = []
            for e in enemies:
                img = _load_image(e["image"])
                if img:
                    s = min(64 / img.get_width(), 64 / img.get_height())
                    self._thumb_cache[stage].append(
                        pygame.transform.smoothscale(
                            img, (int(img.get_width()*s), int(img.get_height()*s))))
                else:
                    self._thumb_cache[stage].append(None)

    def _state(self, level):
        if level < self.unlocked: return "done"
        elif level == self.unlocked: return "unlocked"
        else: return "locked"

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_btn.is_clicked(event):
                self.go_back = True
                self.done    = True
                return
            mx, my = event.pos
            for i, (cx, cy) in enumerate(NODE_POSITIONS):
                level = i + 1
                if self._state(level) == "locked": continue
                if math.hypot(mx - cx, my - cy) <= NODE_R + 5:
                    self.chosen = level
                    self.done   = True
                    return

    def draw(self):
        ctx.screen.blit(self.bg, (0, 0)) 
        W, H = WIDTH, HEIGHT
        mx, my = pygame.mouse.get_pos()

        pygame.draw.rect(ctx.screen, BG_PANEL, (W - PREVIEW_W, 0, PREVIEW_W, H))
        pygame.draw.line(ctx.screen, (40, 48, 75), (W - PREVIEW_W, 0), (W - PREVIEW_W, H), 1)

        for i in range(len(NODE_POSITIONS) - 1):
            done = self._state(i + 1) == "done"
            _draw_path(ctx.screen, NODE_POSITIONS[i], NODE_POSITIONS[i+1], done)

        self._hovered_stage = None
        for i, (cx, cy) in enumerate(NODE_POSITIONS):
            level  = i + 1
            state  = self._state(level)
            hover  = math.hypot(mx - cx, my - cy) <= NODE_R + 5
            if hover and state != "locked":
                self._hovered_stage = level
            _draw_node(ctx.screen, cx, cy, level, state, hover, ctx.med_font)

            lbl_y = cy + NODE_R + (22 if state == "done" else 12)
            col   = TEXT_WHITE if state != "locked" else TEXT_MUTED
            draw_text(ctx.screen, STAGE_NAMES.get(level, f"Stage {level}"),
                      cx, lbl_y, col, size=13, bold=True, display=True, anchor="center")
            diff  = STAGE_DIFF.get(level, "")
            dcol  = DIFF_COLOR.get(diff, TEXT_MUTED)
            draw_text(ctx.screen, diff, cx, lbl_y + 18, dcol, size=11, anchor="center")

        pygame.draw.rect(ctx.screen, BG_PANEL, (0, 0, W - PREVIEW_W, 52))
        pygame.draw.line(ctx.screen, (40,48,75), (0,52), (W-PREVIEW_W, 52), 1)
        draw_text(ctx.screen, "PILIH STAGE",
                  (W - PREVIEW_W) // 2, 14,
                  TEXT_WHITE, size=20, bold=True, display=True, anchor="center")
        draw_text(ctx.screen, "Klik node untuk memilih",
                  (W - PREVIEW_W) // 2, 36,
                  TEXT_MUTED, size=12, anchor="center")

        self._draw_preview(self._hovered_stage)

        mx, my = pygame.mouse.get_pos()
        self._back_btn.update((mx, my))
        self._back_btn.draw(ctx.screen)

    def _draw_preview(self, stage):
        W, H = WIDTH, HEIGHT
        px   = W - PREVIEW_W + 12
        py   = 16

        if stage is None:
            draw_text(ctx.screen, "INFO STAGE",
                      W - PREVIEW_W // 2, py + 10,
                      TEXT_MUTED, size=16, bold=True, anchor="center")
            draw_text(ctx.screen, "Hover node untuk",
                      W - PREVIEW_W // 2, py + 50,
                      TEXT_MUTED, size=13, anchor="center")
            draw_text(ctx.screen, "melihat detail musuh",
                      W - PREVIEW_W // 2, py + 68,
                      TEXT_MUTED, size=13, anchor="center")
            return

        enemies   = STAGE_ENEMIES.get(stage, [])
        thumbs    = self._thumb_cache.get(stage, [])
        state     = self._state(stage)
        diff      = STAGE_DIFF.get(stage, "")
        diff_col  = DIFF_COLOR.get(diff, TEXT_MUTED)

        draw_text(ctx.screen, STAGE_NAMES.get(stage, f"Stage {stage}"),
                  W - PREVIEW_W // 2, py + 8,
                  TEXT_WHITE, size=17, bold=True, display=True, anchor="center")
        draw_text(ctx.screen, f"Stage {stage}  ·  {diff}",
                  W - PREVIEW_W // 2, py + 30,
                  diff_col, size=12, anchor="center")

        if state == "locked":
            status_col, status_txt = ACCENT_RED,    " Terkunci"
        elif state == "done":
            status_col, status_txt = ACCENT_GREEN,  " Selesai"
        else:
            status_col, status_txt = ACCENT_BLUE,   " Tersedia"
        sbadge = pygame.Rect(W - PREVIEW_W + 20, py + 46, PREVIEW_W - 40, 22)
        dark   = tuple(max(0, c // 3) for c in status_col)
        draw_rounded_rect(ctx.screen, sbadge, dark, radius=11,
                          border_color=status_col, border_width=1)
        draw_text(ctx.screen, status_txt,
                  sbadge.centerx, sbadge.centery,
                  status_col, size=12, bold=True, anchor="center")

        py += 80
        draw_text(ctx.screen, "MUSUH :", px, py, TEXT_MUTED, size=12, bold=True)
        py += 20

        for i, (enemy, thumb) in enumerate(zip(enemies, thumbs)):
            card_r = pygame.Rect(W - PREVIEW_W + 6, py, PREVIEW_W - 12, 158)
            ecol   = ELEMENT_COLOR.get(enemy["element"].value, TEXT_MUTED)
            rcol   = ROLE_COLOR.get(enemy["role"], TEXT_MUTED)
            dark_e = tuple(max(0, c // 4) for c in ecol)
            draw_rounded_rect(ctx.screen, card_r, dark_e, radius=CARD_RADIUS,
                              border_color=ecol, border_width=1)

            if thumb:
                s   = min(68 / thumb.get_width(), 68 / thumb.get_height()) if thumb.get_width() > 68 else 1
                timg = pygame.transform.smoothscale(
                    thumb, (int(thumb.get_width()*s), int(thumb.get_height()*s)))
                ctx.screen.blit(timg, (card_r.right - timg.get_width() - 6,
                                       card_r.y + (card_r.h - timg.get_height()) // 2))

            draw_text(ctx.screen, enemy["name"],
                      card_r.x + 10, card_r.y + 8,
                      TEXT_WHITE, size=13, bold=True, display=True)

            ebadge = pygame.Rect(card_r.x + 8, card_r.y + 28, 72, 14)
            dark_b = tuple(max(0, c // 3) for c in ecol)
            draw_rounded_rect(ctx.screen, ebadge, dark_b, radius=7,
                              border_color=ecol, border_width=1)
            draw_text(ctx.screen, enemy["element"].value,
                      ebadge.centerx, ebadge.centery,
                      ecol, size=10, bold=True, anchor="center")

            rbadge = pygame.Rect(card_r.x + 86, card_r.y + 28, 72, 14)
            rdark  = tuple(max(0, c // 3) for c in rcol)
            draw_rounded_rect(ctx.screen, rbadge, rdark, radius=7,
                              border_color=rcol, border_width=1)
            draw_text(ctx.screen, f"{ROLE_ICON.get(enemy['role'],'')} {enemy['role']}",
                      rbadge.centerx, rbadge.centery,
                      rcol, size=10, bold=True, anchor="center")

            draw_hp_bar(ctx.screen,
                        card_r.x + 8, card_r.y + 48,
                        width=PREVIEW_W - 80, height=7,
                        current=enemy["hp"], maximum=enemy["hp"], show_text=False)
            draw_text(ctx.screen, f"HP {enemy['hp']}",
                      card_r.x + 8, card_r.y + 58, TEXT_MUTED, size=10)
            draw_text(ctx.screen,
                      f"ATK {enemy['attack']}  DEF {enemy['defense']}",
                      card_r.x + 8, card_r.y + 72, TEXT_MUTED, size=10)

            sk_y = card_r.y + 90
            draw_text(ctx.screen,
                      f"• {enemy['basic']['name']} (Basic)",
                      card_r.x + 8, sk_y, TEXT_MUTED, size=10)
            sk_y += 15
            skd = enemy["skill"]
            tag = f"+{skd['power']}HP" if skd["type"] == "heal" else f"{skd['power']}dmg"
            draw_text(ctx.screen, f"• {skd['name']}  {tag}  CD{skd['cooldown']}",
                      card_r.x + 8, sk_y, TEXT_MUTED, size=10)
            sk_y += 15
            draw_text(ctx.screen, f"  {skd['desc']}",
                      card_r.x + 8, sk_y, (80, 90, 120), size=10)

            py += 164

        if state != "locked":
            draw_text(ctx.screen, "Klik node untuk mulai →",
                      W - PREVIEW_W // 2, H - 24,
                      ACCENT_BLUE, size=12, bold=True, anchor="center")
