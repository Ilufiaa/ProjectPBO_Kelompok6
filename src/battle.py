from src.character import make_character
from src.roster import STAGE_ENEMIES


_PPOS = [(60, 130), (60, 340), (60, 550)]
_EPOS = [(960, 130), (960, 340), (960, 550)]


def build_battle(picked_data: list, stage: int = 1):
    """
    picked_data: list of roster dict (from ALL_CHARS)
    stage: 1-5
    Returns (player_team, enemy_team) — lists of Character
    """
    player_team = [make_character(d, x, y) for d, (x, y) in zip(picked_data, _PPOS)]
    enemy_data  = STAGE_ENEMIES.get(stage, STAGE_ENEMIES[1])
    enemy_team  = [make_character(d, x, y) for d, (x, y) in zip(enemy_data, _EPOS)]
    return player_team, enemy_team
