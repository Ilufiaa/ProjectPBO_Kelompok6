import pygame
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import src.game_context as ctx
from src.constants import WIDTH, HEIGHT

pygame.init()
ctx.screen   = pygame.display.set_mode((WIDTH, HEIGHT))
# Font 
_pop  = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"
_popb = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_adv  = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf"
import os
ctx.font     = pygame.font.Font(_pop  if os.path.exists(_pop)  else None, 28)
ctx.big_font = pygame.font.Font(_adv  if os.path.exists(_adv)  else None, 70)
ctx.med_font = pygame.font.Font(_adv  if os.path.exists(_adv)  else None, 42)
pygame.display.set_caption("Please don't play This! 🙏")
clock = pygame.time.Clock()

from src.menu_scene     import MenuScene
from src.petunjuk_scene import PetunjukScene
from src.stage_scene    import StageScene
from src.deck_scene     import DeckScene
from src.battle         import build_battle
from src.battle_scene   import BattleScene
from src.result_scene   import ResultScene
from src.save_data      import load_save, save_progress, MAX_LEVEL
from src.sound_manager import SoundManager
ctx.sfx = SoundManager()          

def run_scene(scene):
    while not scene.done:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            scene.handle(event)
        scene.draw()
        pygame.display.update()


while True:
    #Menu 
    ctx.sfx.play_menu_bgm() 
    menu = MenuScene()
    while True:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            menu.handle(event)
        menu.draw()
        pygame.display.update()
        if menu.choice == "mulai":
            break
        elif menu.choice == "petunjuk":
            run_scene(PetunjukScene())
            menu.choice = None

    #Stage select 
    while True:
        stage_scene = StageScene()
        run_scene(stage_scene)
        if getattr(stage_scene, "go_back", False):
            break          
        current_stage = stage_scene.chosen

        
        deck = DeckScene()
        run_scene(deck)
        if getattr(deck, "go_back", False):
            continue       

        ctx.sfx.stop_bgm()
        player_team, enemy_team = build_battle(deck.picked, stage=current_stage)
        battle = BattleScene(player_team, enemy_team)
        while not battle.done:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                battle.handle(event)
            battle.update(dt)
            battle.draw()
            pygame.display.update()

        if getattr(battle, "go_to_menu", False):
            break          

        ctx.sfx.play_menu_bgm()
        result_scene = ResultScene(player_won=(battle.result == "win"))
        run_scene(result_scene)

        if result_scene.choice == "quit":
            pygame.quit(); sys.exit()

        if battle.result == "win":
            save_progress(min(current_stage + 1, MAX_LEVEL))

        if result_scene.choice == "again":
            continue       
        break              