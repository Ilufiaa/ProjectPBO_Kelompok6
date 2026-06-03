import pygame
import math
import random
from src.constants import *
from src import game_context as ctx
from src.skill import Skill
from src.element import Element, ElementChart

_image_cache = {}

def _load_image(path):
    if path in _image_cache:
        return _image_cache[path]
    try:
        img = pygame.image.load(path).convert_alpha()
        _image_cache[path] = img
        return img
    except Exception:
        _image_cache[path] = None
        return None


def _parse_element(elem) -> Element:
    if isinstance(elem, Element):
        return elem
    for e in Element:
        if e.value.lower() == str(elem).lower():
            return e
    return Element.FIRE


class Character:
    def __init__(self, data: dict, x: int, y: int):
        """Build a character from a roster dict entry."""
        self.name    = data["name"]
        self.element = data["element"] if isinstance(data["element"], Element) else _parse_element(data["element"])
        self.role    = data["role"]
        self.max_hp  = data["hp"]
        self.hp      = data["hp"]
        self.attack  = data["attack"]
        self.defense = data["defense"]
        self.x, self.y = x, y
        self.width = self.height = 110  

        self._img_path = data.get("image", "")
        self.image     = _load_image(self._img_path)

        basic_d = data["basic"]
        skill_d = data["skill"]

        self.basic_attack = Skill(
            name      = basic_d["name"],
            power     = basic_d.get("power", 0),
            skill_type= "attack",
            max_cd    = 0,
            desc      = "Serangan dasar",
        )
        self.special_skill = Skill(
            name      = skill_d["name"],
            power     = skill_d["power"],
            skill_type= skill_d["type"],
            max_cd    = skill_d.get("cooldown", 3),
            desc      = skill_d.get("desc", ""),
        )
        self.skills = [self.basic_attack, self.special_skill]

        self.shake_timer = 0

    def is_alive(self):
        return self.hp > 0

    def hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp else 0.0

    def on_turn_start(self):
        for sk in self.skills:
            sk.reduce_cooldown()

    def get_ready_skills(self):
        return [s for s in self.skills if s.is_ready()]

    def calculate_damage(self, base_dmg, target):
        effective  = max(1, base_dmg - target.defense)
        multiplier = ElementChart.get_multiplier(self.element, target.element)
        return math.floor(effective * multiplier), multiplier

    def do_basic_attack(self, target) -> dict:
        dmg, mult = self.calculate_damage(self.attack, target)
        target.take_damage(dmg)
        return {"attacker": self.name, "target": target.name,
                "damage": dmg, "multiplier": mult,
                "skill": self.basic_attack.name, "healed": 0}

    def use_skill(self, target, skill) -> dict:
        skill.use()
        if skill.skill_type == "heal":
            healed = target._do_heal(skill.power)
            return {"attacker": self.name, "target": target.name,
                    "damage": 0, "multiplier": 1.0,
                    "skill": skill.name, "healed": healed}
        else:
            dmg, mult = self.calculate_damage(self.attack + skill.power, target)
            target.take_damage(dmg)
            return {"attacker": self.name, "target": target.name,
                    "damage": dmg, "multiplier": mult,
                    "skill": skill.name, "healed": 0}

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        self.shake_timer = 10

    def _do_heal(self, amount) -> int:
        before  = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


def make_character(data: dict, x: int, y: int) -> Character:
    return Character(data, x, y)
