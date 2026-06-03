from __future__ import annotations
import math
import pygame
from src.constants import *
from src import game_context as ctx
from src.draw_utils import (
    draw_text, draw_rounded_rect,
    UIButton, get_font,
    BG_DARK, BG_PANEL,
    TEXT_WHITE, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_ORANGE, ACCENT_RED, ACCENT_GREEN, ACCENT_PURPLE,
    BTN_NORMAL, BTN_DISABLE, BTN_ACTIVE, BTN_BORDER,
    HP_HIGH, HP_MID, HP_LOW, HP_BG,
    CARD_RADIUS,
)
from src.element import ELEMENT_COLOR
from src.roster import ROLE_COLOR, ROLE_ICON
from src.floating_text import FloatingTextManager
from src.character import Character
from src.sound_manager import SoundManager

TOP_H      = 36
ACTION_H   = 120
IMG_SIZE   = 130     
HP_BAR_W   = 140
HP_BAR_H   = 10
AI_DELAY   = 950      
BTN_W      = 220
BTN_H      = 88

TARGET_ENEMY  = "enemy"
TARGET_ALLY   = "ally"


class BattleState:
    PLAYER_ACTION = "player_action"
    PLAYER_TARGET = "player_target"   
    AI_TURN       = "ai_turn"
    RESULT_PAUSE  = "result_pause"
    OVER          = "over"
    PAUSED        = "paused"

class CharacterSprite:
    """Tampilan karakter di battle: gambar, HP bar, nama, badge. Tanpa kotak."""

    ANIM_FLASH = 300

    def __init__(self, character: Character, cx: int, cy: int):
        self.character  = character
        self.cx         = cx      
        self.cy         = cy      
        self._flash_ms  = 0
        self._shake_ms = 0
        self.selected   = False
        self.hovered    = False
        self._img       = self._make_img()
        
        self.rect = pygame.Rect(cx - IMG_SIZE // 2, cy - IMG_SIZE // 2,
                                IMG_SIZE, IMG_SIZE)

    def _make_img(self):
        img = self.character.image
        if not img:
            return None
        s = min(IMG_SIZE / img.get_width(), IMG_SIZE / img.get_height())
        return pygame.transform.smoothscale(
            img, (int(img.get_width()*s), int(img.get_height()*s)))

    def trigger_flash(self):
        self._flash_ms = self.ANIM_FLASH

    def trigger_shake(self):
        self._shake_ms = 300   

    def update(self, dt, mouse_pos):
        if self._flash_ms > 0:
            self._flash_ms = max(0, self._flash_ms - dt)
        if self._shake_ms > 0:                  
            self._shake_ms = max(0, self._shake_ms - dt)
        self.hovered = (self.rect.collidepoint(mouse_pos)
                        and self.character.is_alive())

    def draw(self, surf):
        c    = self.character
        dead = not c.is_alive()

        img = self._img
        if img:
            iw, ih   = img.get_size()
            shake_offset = int(6 * math.sin(self._shake_ms * 0.08)) if self._shake_ms > 0 else 0
            draw_x   = self.cx - iw // 2 + shake_offset
            draw_y   = self.cy - ih // 2

            if dead:
                dark = img.copy()
                dark.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(dark, (draw_x, draw_y))
            else:
                
                if self._flash_ms > 0:
                    alpha = int(170 * self._flash_ms / self.ANIM_FLASH)
                    surf.blit(img, (draw_x, draw_y))
                    flash = pygame.Surface((iw, ih), pygame.SRCALPHA)
                    flash.fill((220, 50, 50, alpha))
                    surf.blit(flash, (draw_x, draw_y))
                else:
                    surf.blit(img, (draw_x, draw_y))

                
                if self.selected:
                    glow = pygame.Surface((iw + 10, ih + 10), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (*ACCENT_BLUE, 60),
                                     (0, 0, iw + 10, ih + 10), border_radius=12)
                    surf.blit(glow, (draw_x - 5, draw_y - 5))

                
                if self.hovered and not self.selected:
                    glow = pygame.Surface((iw + 8, ih + 8), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (*ACCENT_ORANGE, 50),
                                     (0, 0, iw + 8, ih + 8), border_radius=10)
                    surf.blit(glow, (draw_x - 4, draw_y - 4))
        else:
            
            pygame.draw.circle(surf, (60, 70, 100), (self.cx, self.cy), IMG_SIZE // 2)

        if dead:
            draw_text(surf, "DEFEATED", self.cx, self.cy,
                      ACCENT_RED, size=16, bold=True, anchor="center")
            return

        img_top    = self.cy - IMG_SIZE // 2
        img_bottom = self.cy + IMG_SIZE // 2

        draw_text(surf, c.name,
              self.cx, img_top - 28,
              TEXT_WHITE, size=12, bold=True, display=True, anchor="midtop")

        bar_x  = self.cx - HP_BAR_W // 2
        bar_y  = img_top - 12
        ratio  = c.hp / c.max_hp if c.max_hp else 0
        filled = int(HP_BAR_W * ratio)
        hp_col = HP_HIGH if ratio > 0.5 else HP_MID if ratio > 0.25 else HP_LOW
        pygame.draw.rect(surf, HP_BG,
                     (bar_x, bar_y, HP_BAR_W, HP_BAR_H),
                     border_radius=HP_BAR_H // 2)
        if filled > 0:
            pygame.draw.rect(surf, hp_col,
                         (bar_x, bar_y, filled, HP_BAR_H),
                         border_radius=HP_BAR_H // 2)

        ecol  = ELEMENT_COLOR.get(c.element.value, TEXT_MUTED)
        rcol  = ROLE_COLOR.get(c.role, TEXT_MUTED)
        edark = tuple(max(0, x // 3) for x in ecol)
        rdark = tuple(max(0, x // 3) for x in rcol)

        badge_y = img_bottom + 5
        eb = pygame.Rect(self.cx - 76, badge_y, 70, 14)
        draw_rounded_rect(surf, eb, edark, radius=7, border_color=ecol, border_width=1)
        draw_text(surf, c.element.value,
              eb.centerx, eb.centery, ecol, size=9, bold=True, anchor="center")

        rb = pygame.Rect(self.cx + 6, badge_y, 70, 14)
        draw_rounded_rect(surf, rb, rdark, radius=7, border_color=rcol, border_width=1)
        draw_text(surf, f"{ROLE_ICON.get(c.role,'')} {c.role}",
              rb.centerx, rb.centery, rcol, size=9, bold=True, anchor="center")

        draw_text(surf, f"{c.hp} / {c.max_hp}",
              self.cx, badge_y + 17,
              TEXT_MUTED, size=10, anchor="midtop")

    def is_clicked(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
            and self.character.is_alive()
        )

class BattleScene:
    def __init__(self, player_team, enemy_team):
        self.player_team = player_team
        self.enemy_team  = enemy_team
        self.done        = False
        self.result      = None

        self.floats = FloatingTextManager()
        self._sfx   = SoundManager()
        self._sfx.play_bgm()   

        self._player_sprites = self._make_sprites(player_team, side="left")
        self._enemy_sprites  = self._make_sprites(enemy_team,  side="right")
        self._sprite_map     = {s.character.name: s
                                for s in self._player_sprites + self._enemy_sprites}

        self._turn_order = []
        for p, e in zip(player_team, enemy_team):
            self._turn_order.append(p)
            self._turn_order.append(e)
        self._turn_idx = 0
        self._turn_num = 1

        self._state          = BattleState.PLAYER_ACTION
        self._action_btns:   list[UIButton] = []
        self._pending_skill  = None
        self._target_mode    = TARGET_ENEMY   
        self._pause_t        = 0
        self._ai_t           = 0
        self._last_result    = None
        self._state_before_pause = None
        self.go_to_menu      = False          

        bg_raw   = pygame.image.load("assets/backgrounds/battlescene.jpeg").convert()
        self.bg  = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
       
        self._pause_btn = UIButton(
            pygame.Rect(8, 4, 28, 28), "⏸", color=BTN_NORMAL)

        
        _pcx, _pcy = WIDTH // 2, HEIGHT // 2
        self._resume_btn = UIButton(
            pygame.Rect(0, 0, 220, 52), "  Lanjutkan", color=BTN_ACTIVE)
        self._resume_btn.rect.center = (_pcx, _pcy - 4)
        self._exit_btn = UIButton(
            pygame.Rect(0, 0, 220, 52), "  Keluar ke Menu", color=(80, 30, 30))
        self._exit_btn.rect.center = (_pcx, _pcy + 62)

        self._begin_turn()

    @property
    def _map_top(self):  return TOP_H + 4
    @property
    def _map_bot(self):  return HEIGHT - ACTION_H
    @property
    def _map_h(self):    return self._map_bot - self._map_top

    def _make_sprites(self, team, side):
        n      = len(team)
        slot_h = self._map_h // n
        margin = 160   

        if side == "left":
            cx = margin
        else:
            cx = WIDTH - margin

        sprites = []
        for i, ch in enumerate(team):
            cy = self._map_top + i * slot_h + slot_h // 2
            sprites.append(CharacterSprite(ch, cx, cy))
        return sprites

   
    def _current(self):
        self._skip_dead()
        if not any(c.is_alive() for c in self._turn_order):
            return None
        return self._turn_order[self._turn_idx]

    def _skip_dead(self):
        for _ in range(len(self._turn_order)):
            if self._turn_order[self._turn_idx].is_alive():
                return
            self._turn_idx = (self._turn_idx + 1) % len(self._turn_order)

    def _advance_turn(self):
        self._turn_num += 1
        self._turn_idx  = (self._turn_idx + 1) % len(self._turn_order)
        self._skip_dead()

    def _begin_turn(self):
        actor = self._current()
        if not actor: return
        actor.on_turn_start()

        for sp in self._player_sprites + self._enemy_sprites:
            sp.selected = (sp.character is actor)

        is_player = actor in self.player_team
        col = ACCENT_BLUE if is_player else ACCENT_ORANGE
        self.floats.spawn(
            f"{actor.name}'s turn",
            WIDTH // 2, self._map_top + self._map_h // 2,
            col, size=18, bold=True, lifetime_ms=800, speed=0.02)

        if is_player:
            self._build_action_buttons(actor)
            self._state = BattleState.PLAYER_ACTION
        else:
            self._ai_t  = AI_DELAY
            self._state = BattleState.AI_TURN

    def _build_action_buttons(self, actor):
        total_w = 2 * BTN_W + 24
        sx      = WIDTH // 2 - total_w // 2
        by      = HEIGHT - ACTION_H + (ACTION_H - BTN_H) // 2

        spec  = actor.special_skill
        ready = spec.is_ready()
        is_heal = spec.skill_type == "heal"

        sub0 = "Selalu siap · Menyerang musuh"
        if is_heal:
            sub1 = f" Heal +{spec.power}HP · {'RDY' if ready else 'CD '+str(spec.cooldown)}"
        else:
            sub1 = f" {spec.power} dmg · {'RDY' if ready else 'CD '+str(spec.cooldown)}"

        self._action_btns = [
            UIButton(pygame.Rect(sx,               by, BTN_W, BTN_H),
                     f" {actor.basic_attack.name}", sub0),
            UIButton(pygame.Rect(sx + BTN_W + 24,  by, BTN_W, BTN_H),
                     f" {spec.name}", sub1,
                     color=BTN_ACTIVE if ready else BTN_DISABLE,
                     disabled=not ready),
        ]

   
    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self._state == BattleState.PAUSED:
                self._state = self._state_before_pause
                return
            elif self._state == BattleState.PLAYER_TARGET:
                self._state = BattleState.PLAYER_ACTION
                self._pending_skill = None
                return
            elif self._state not in (BattleState.OVER,):
                self._state_before_pause = self._state
                self._state = BattleState.PAUSED
                return

        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3
                and self._state == BattleState.PLAYER_TARGET):
            self._state = BattleState.PLAYER_ACTION
            self._pending_skill = None
            return

        if self._state == BattleState.PAUSED:
            mouse = pygame.mouse.get_pos()
            self._resume_btn.update(mouse)
            self._exit_btn.update(mouse)
            if self._resume_btn.is_clicked(event):
                self._state = self._state_before_pause
                return
            if self._exit_btn.is_clicked(event):
                self._sfx.stop_bgm()   
                self.go_to_menu = True
                self.done       = True
                return
            return   

        if self._pause_btn.is_clicked(event) and self._state != BattleState.OVER:
            self._state_before_pause = self._state
            self._state = BattleState.PAUSED
            return

        if self._state == BattleState.PLAYER_ACTION:
            actor = self._current()
            if not actor: return
            for i, btn in enumerate(self._action_btns):
                if btn.is_clicked(event):
                    sk = actor.basic_attack if i == 0 else actor.special_skill
                    self._pending_skill = sk
                    self._target_mode = TARGET_ALLY if sk.skill_type == "heal" else TARGET_ENEMY
                    self._state = BattleState.PLAYER_TARGET
                    return

        elif self._state == BattleState.PLAYER_TARGET:
            actor = self._current()
            if not actor: return
            if self._target_mode == TARGET_ENEMY:
                for sp in self._enemy_sprites:
                    if sp.is_clicked(event):
                        result = actor.use_skill(sp.character, self._pending_skill)
                        self._resolve(result, sp)
                        return
            else:
                for sp in self._player_sprites:
                    if sp.is_clicked(event):
                        result = actor.use_skill(sp.character, self._pending_skill)
                        self._resolve_heal(result, sp)
                        return

        if self._state == BattleState.OVER:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._sfx.stop_bgm()   
                self.done = True

    def _resolve(self, result, target_sp):
        self._last_result = result
        self._sfx.play(result["attacker"])   
        if result["damage"] > 0:
            self._sfx.play_hit(is_heal=False)  
        target_sp.trigger_flash()
        target_sp.trigger_shake()

        cx, cy = target_sp.cx, target_sp.cy - IMG_SIZE // 2

        if result["damage"] > 0:
            self.floats.spawn_damage(result["damage"], cx, cy, result["multiplier"])
        if result["skill"]:
            atk_sp = self._sprite_map.get(result["attacker"])
            if atk_sp:
                self.floats.spawn_status(result["skill"],
                                         atk_sp.cx, atk_sp.cy - IMG_SIZE // 2 + 20,
                                         ACCENT_PURPLE)
        if not target_sp.character.is_alive():
            self.floats.spawn("DEFEATED", cx, cy - 20,
                              ACCENT_RED, size=26, lifetime_ms=1600)
        self._pause_t = 1400
        self._state   = BattleState.RESULT_PAUSE

    def _resolve_heal(self, result, target_sp):
        self._last_result = result
        self._sfx.play(result["attacker"])   
        self._sfx.play_hit(is_heal=True)       
        cx, cy = target_sp.cx, target_sp.cy - IMG_SIZE // 2
        if result["healed"] > 0:
            self.floats.spawn_heal(result["healed"], cx, cy)
        if result["skill"]:
            atk_sp = self._sprite_map.get(result["attacker"])
            if atk_sp:
                self.floats.spawn_status(result["skill"],
                                         atk_sp.cx, atk_sp.cy - IMG_SIZE // 2 + 20,
                                         ACCENT_PURPLE)
        self._pause_t = 1200
        self._state   = BattleState.RESULT_PAUSE

    def _ai_act(self):
        actor = self._current()
        if not actor: return
        alive_players = [c for c in self.player_team if c.is_alive()]
        alive_allies  = [c for c in self.enemy_team  if c.is_alive()]
        if not alive_players: return

        spec = actor.special_skill

        if spec.skill_type == "heal" and spec.is_ready():
            if alive_allies:
                weakest = min(alive_allies, key=lambda c: c.hp_ratio())
                if weakest.hp_ratio() < 0.7:
                    result = actor.use_skill(weakest, spec)
                    sp = self._sprite_map.get(weakest.name)
                    if sp: self._resolve_heal(result, sp)
                    return

        target = min(alive_players, key=lambda c: c.hp)
        t_sp   = self._sprite_map.get(target.name)
        if spec.skill_type == "attack" and spec.is_ready():
            result = actor.use_skill(target, spec)
        else:
            result = actor.do_basic_attack(target)
        if t_sp:
            self._resolve(result, t_sp)

    def update(self, dt):
        if self._state == BattleState.PAUSED:
            return   
        mp = pygame.mouse.get_pos()
        for sp in self._player_sprites + self._enemy_sprites:
            sp.update(dt, mp)
        for btn in self._action_btns:
            btn.update(mp)
        self.floats.update(dt)

        if all(not c.is_alive() for c in self.enemy_team):
            if self._state != BattleState.OVER:
                self._state, self.result = BattleState.OVER, "win"
            return
        if all(not c.is_alive() for c in self.player_team):
            if self._state != BattleState.OVER:
                self._state, self.result = BattleState.OVER, "lose"
            return

        if self._state == BattleState.AI_TURN:
            self._ai_t -= dt
            if self._ai_t <= 0:
                self._ai_act()

        elif self._state == BattleState.RESULT_PAUSE:
            self._pause_t -= dt
            if self._pause_t <= 0:
                self._advance_turn()
                self._begin_turn()

    def draw(self):
        ctx.screen.blit(self.bg, (0, 0)) 
        self._draw_bg()

        for sp in self._player_sprites + self._enemy_sprites:
            sp.draw(ctx.screen)

        if self._state == BattleState.PLAYER_TARGET:
            self._draw_target_hints()

        self.floats.draw(ctx.screen)
        self._draw_top_bar()
        self._draw_action_panel()

        if self._state == BattleState.OVER:
            self._draw_game_over()

        if self._state != BattleState.OVER:
            self._pause_btn.update(pygame.mouse.get_pos())
            self._pause_btn.draw(ctx.screen)

        if self._state == BattleState.PAUSED:
            self._draw_pause_overlay()

    def _draw_bg(self):
        ov = pygame.Surface((WIDTH, self._map_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 80))   
        ctx.screen.blit(ov, (0, self._map_top))
        pygame.draw.line(ctx.screen, (35, 42, 68),
                         (WIDTH // 2, self._map_top + 10),
                         (WIDTH // 2, self._map_bot - 10), 1)

        draw_text(ctx.screen, "TIM KAMU",
                  WIDTH // 4, self._map_top + 12,
                  (28, 55, 95), size=11, bold=True, display=True, anchor="center")
        draw_text(ctx.screen, "MUSUH",
                  WIDTH * 3 // 4, self._map_top + 12,
                  (75, 25, 45), size=11, bold=True, display=True, anchor="center")

    def _draw_top_bar(self):
        pygame.draw.rect(ctx.screen, BG_PANEL, (0, 0, WIDTH, TOP_H))
        pygame.draw.line(ctx.screen, (40, 48, 75), (0, TOP_H), (WIDTH, TOP_H), 1)

        actor = self._current()
        if actor:
            col = ACCENT_BLUE if actor in self.player_team else ACCENT_ORANGE
            draw_text(ctx.screen,
                      f"Turn {self._turn_num}  ·  Giliran: {actor.name}",
                      WIDTH // 2, TOP_H // 2,
                      col, size=14, bold=True, display=True, anchor="center")

        p_hp = sum(c.hp for c in self.player_team)
        p_mx = sum(c.max_hp for c in self.player_team)
        e_hp = sum(c.hp for c in self.enemy_team)
        e_mx = sum(c.max_hp for c in self.enemy_team)
        draw_text(ctx.screen, f"Tim ❤ {p_hp}/{p_mx}",
                  14, TOP_H // 2, ACCENT_GREEN, size=12, anchor="midleft")
        draw_text(ctx.screen, f"Musuh ❤ {e_hp}/{e_mx}",
                  WIDTH - 14, TOP_H // 2, ACCENT_RED, size=12, anchor="midright")

    def _draw_action_panel(self):
        pygame.draw.rect(ctx.screen, BG_PANEL,
                         (0, HEIGHT - ACTION_H, WIDTH, ACTION_H))
        pygame.draw.line(ctx.screen, BTN_BORDER,
                         (0, HEIGHT - ACTION_H), (WIDTH, HEIGHT - ACTION_H), 1)

        if self._state == BattleState.PLAYER_ACTION:
            for btn in self._action_btns:
                btn.draw(ctx.screen)
            draw_text(ctx.screen, "Pilih aksi",
                      WIDTH // 2, HEIGHT - ACTION_H + 7,
                      TEXT_MUTED, size=11, anchor="center")

        elif self._state == BattleState.PLAYER_TARGET:
            actor = self._current()
            sk    = self._pending_skill
            if sk and sk.skill_type == "heal":
                msg = f"♥  {sk.name}  —  Klik TEMAN untuk di-heal  |  Klik Kanan / Esc: batal"
                col = ACCENT_GREEN
            else:
                msg = f"⚔  Pilih target — klik kartu MUSUH  |  Klik Kanan / Esc: batal"
                col = ACCENT_ORANGE
            draw_text(ctx.screen, msg,
                      WIDTH // 2, HEIGHT - ACTION_H // 2,
                      col, size=15, bold=True, anchor="center")

        elif self._state == BattleState.RESULT_PAUSE and self._last_result:
            r  = self._last_result
            if r["damage"] > 0:
                eff = ""
                if r["multiplier"] >= 2.0:   eff = "  ⚡ Super Effective!"
                elif r["multiplier"] <= 0.5: eff = "  💤 Not very effective"
                msg = f"{r['attacker']}  ▶  {r['skill']}  ▶  {r['target']}  —  {r['damage']} DMG{eff}"
                col = ACCENT_ORANGE if r["multiplier"] >= 2.0 else TEXT_WHITE
            else:
                msg = f"{r['attacker']}  ▶  {r['skill']}  —  +{r['healed']} HP dipulihkan"
                col = ACCENT_GREEN
            draw_text(ctx.screen, msg,
                      WIDTH // 2, HEIGHT - ACTION_H // 2,
                      col, size=14, bold=True, anchor="center")

        elif self._state == BattleState.AI_TURN:
            actor = self._current()
            draw_text(ctx.screen,
                      f"{actor.name if actor else 'Musuh'} sedang berpikir…",
                      WIDTH // 2, HEIGHT - ACTION_H // 2,
                      ACCENT_ORANGE, size=14, anchor="center")

    def _draw_target_hints(self):
        """Panah dan glow ke karakter yang bisa diklik."""
        if self._target_mode == TARGET_ENEMY:
            targets = [(sp, ACCENT_ORANGE) for sp in self._enemy_sprites
                       if sp.character.is_alive()]
        else:
            targets = [(sp, ACCENT_GREEN) for sp in self._player_sprites
                       if sp.character.is_alive()]

        for sp, col in targets:
            r = IMG_SIZE // 2 + 8
            glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*col, 45), (r, r), r)
            pygame.draw.circle(glow, (*col, 80), (r, r), r, 2)
            ctx.screen.blit(glow, (sp.cx - r, sp.cy - r))

            ay = sp.cy + IMG_SIZE // 2 + 8
            ax = sp.cx
            pygame.draw.polygon(ctx.screen, col, [
                (ax, ay), (ax - 10, ay + 16), (ax + 10, ay + 16)])

    def _draw_pause_overlay(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        ctx.screen.blit(ov, (0, 0))

        cx, cy = WIDTH // 2, HEIGHT // 2
        panel  = pygame.Rect(cx - 140, cy - 130, 280, 260)
        draw_rounded_rect(ctx.screen, panel, BG_PANEL, radius=18,
                          border_color=ACCENT_BLUE, border_width=2)

        # Ikon & judul
        draw_text(ctx.screen, "⏸", cx, cy - 95,
                  TEXT_MUTED, size=30, bold=True, anchor="center")
        draw_text(ctx.screen, "GAME PAUSED", cx, cy - 58,
                  TEXT_WHITE, size=20, bold=True, display=True, anchor="center")
        pygame.draw.line(ctx.screen, (40, 50, 90),
                         (cx - 100, cy - 40), (cx + 100, cy - 40), 1)

        mouse = pygame.mouse.get_pos()
        self._resume_btn.update(mouse)
        self._exit_btn.update(mouse)
        self._resume_btn.draw(ctx.screen)
        self._exit_btn.draw(ctx.screen)

        draw_text(ctx.screen, "atau tekan  Esc  untuk lanjut",
                  cx, cy + 108, TEXT_MUTED, size=11, anchor="center")

    def _draw_game_over(self):
        self._sfx.stop_bgm()   
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        ctx.screen.blit(ov, (0, 0))
        if self.result == "win":
            heading, sub, col = "✔  KEMENANGAN!", "Tim kamu berhasil mengalahkan semua musuh!", ACCENT_GREEN
        else:
            heading, sub, col = "✘  KEKALAHAN", "Seluruh tim kamu telah dikalahkan.", ACCENT_RED
        panel = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 140, 600, 280)
        draw_rounded_rect(ctx.screen, panel, BG_PANEL, radius=18,
                          border_color=col, border_width=2)
        draw_text(ctx.screen, heading, WIDTH // 2, HEIGHT // 2 - 80,
                  col, size=44, bold=True, display=True, anchor="center")
        draw_text(ctx.screen, sub, WIDTH // 2, HEIGHT // 2 - 20,
                  TEXT_MUTED, size=16, anchor="center")
        draw_text(ctx.screen, "Klik di mana saja untuk lanjut",
                  WIDTH // 2, HEIGHT // 2 + 40, TEXT_MUTED, size=14, anchor="center")
