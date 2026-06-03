from __future__ import annotations
import pygame
from src.draw_utils import get_font, ACCENT_GREEN, ACCENT_RED, ACCENT_ORANGE, TEXT_MUTED, TEXT_WHITE


class FloatingText:
    def __init__(self, text, x, y, color=TEXT_WHITE,
                 size=22, bold=True, lifetime_ms=1100, speed=0.07):
        self.text       = text
        self.x          = float(x)
        self.y          = float(y)
        self.color      = color
        self.lifetime   = lifetime_ms
        self._remaining = lifetime_ms
        self.speed      = speed
        self._font      = get_font(size, bold)

    @property
    def alive(self):
        return self._remaining > 0

    def update(self, dt):
        self._remaining -= dt
        self.y -= self.speed * dt

    def draw(self, surf):
        if not self.alive:
            return
        alpha  = max(0, min(255, int(255 * (self._remaining / self.lifetime))))
        render = self._font.render(self.text, True, self.color)
        render.set_alpha(alpha)
        rx = int(self.x) - render.get_width() // 2
        ry = int(self.y) - render.get_height() // 2

        shadow = self._font.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(alpha // 2)
        for ox, oy in ((-1, 1), (1, 1), (0, 2)):
            surf.blit(shadow, (rx + ox, ry + oy))
        surf.blit(render, (rx, ry))


class FloatingTextManager:
    def __init__(self):
        self._texts: list[FloatingText] = []

    def spawn(self, text, x, y, color=TEXT_WHITE, size=22, bold=True,
              lifetime_ms=1100, speed=0.07):
        self._texts.append(FloatingText(text, x, y, color, size, bold, lifetime_ms, speed))

    def spawn_damage(self, damage, cx, cy, multiplier=1.0):
        if multiplier >= 2.0:
            col, sz = ACCENT_ORANGE, 34
            self.spawn("Super Effective!", cx, cy - 36, ACCENT_ORANGE, size=15, lifetime_ms=1300)
        elif multiplier <= 0.5:
            col, sz = TEXT_MUTED, 20
            self.spawn("Not very effective...", cx, cy - 32, TEXT_MUTED, size=13, lifetime_ms=1000)
        else:
            col, sz = ACCENT_RED, 28
        self.spawn(f"-{damage}", cx, cy, col, size=sz, lifetime_ms=1200)

    def spawn_heal(self, amount, cx, cy):
        self.spawn(f"+{amount} HP", cx, cy, ACCENT_GREEN, size=22)

    def spawn_status(self, text, cx, cy, color=TEXT_WHITE):
        self.spawn(text, cx, cy, color, size=15, bold=False, lifetime_ms=900)

    def update(self, dt):
        for ft in self._texts:
            ft.update(dt)
        self._texts = [ft for ft in self._texts if ft.alive]

    def draw(self, surf):
        for ft in self._texts:
            ft.draw(surf)

    def clear(self):
        self._texts.clear()
