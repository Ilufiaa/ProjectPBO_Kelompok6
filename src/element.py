from enum import Enum

class Element(Enum):
    FIRE      = "Fire"
    WATER     = "Water"
    WIND      = "Wind"
    EARTH     = "Earth"
    LIGHT     = "Light"
    DARK      = "Dark"


class ElementChart:
    _TABLE: dict = {
        (Element.FIRE,      Element.FIRE):    1.0,
        (Element.FIRE,      Element.WIND):      1.0,
        (Element.FIRE,      Element.WATER):     0.5,
        (Element.FIRE,      Element.EARTH):     2.0,
        (Element.FIRE,      Element.LIGHT):     1.0,
        (Element.FIRE,      Element.DARK):     1.0,

        (Element.WATER,     Element.FIRE):      2.0,
        (Element.WATER,     Element.LIGHT): 1.0,
        (Element.WATER,     Element.WATER): 1.0,
        (Element.WATER,     Element.DARK): 1.0,
        (Element.WATER,     Element.WIND): 0.5,
        (Element.WATER,     Element.EARTH): 1.0,

        (Element.WIND,      Element.WIND):    1.0,
        (Element.WIND,      Element.LIGHT): 1.0,
        (Element.WIND,      Element.DARK): 1.0,
        (Element.WIND,      Element.FIRE): 1.0,
        (Element.WIND,      Element.EARTH): 0.5,
        (Element.WIND,      Element.WATER): 2.0,

        (Element.EARTH,     Element.LIGHT): 1.0,
        (Element.EARTH,     Element.DARK):      1.0,
        (Element.EARTH,     Element.WIND):      2.0,
        (Element.EARTH,     Element.FIRE):      0.5,
        (Element.EARTH,     Element.WATER):      0.5,
        (Element.EARTH,     Element.EARTH):      1.0,

        (Element.LIGHT, Element.WATER):     1.0,
        (Element.LIGHT, Element.FIRE):     1.0,
        (Element.LIGHT, Element.EARTH):     1.0,
        (Element.LIGHT, Element.WIND):     1.0,
        (Element.LIGHT, Element.LIGHT):     1.0,
        (Element.LIGHT, Element.EARTH):     1.0,
        (Element.LIGHT, Element.DARK):     2.0,

        (Element.DARK,      Element.LIGHT):     2.0,
        (Element.DARK,     Element.DARK):      1.0,
        (Element.DARK,     Element.FIRE):      1.0,
        (Element.DARK,     Element.WATER):      1.0,
        (Element.DARK,     Element.EARTH):      1.0,
        (Element.DARK,     Element.WIND):      1.0,
    }

    @classmethod
    def get_multiplier(cls, attacker: Element, defender: Element) -> float:
        return cls._TABLE.get((attacker, defender), 1.0)

    @classmethod
    def effectiveness_text(cls, mult: float) -> str:
        if mult >= 2.0:
            return "Super Effective!"
        if mult <= 0.5:
            return "Not very effective..."
        return ""


ELEMENT_COLOR = {
    "Fire":      (255, 100,  60),
    "Water":     ( 60, 160, 255),
    "Earth":      (190, 140, 70),
    "Wind":     (80, 200,  90),
    "Dark":      (76,  0, 153),
    "Light":     (255, 255, 0),
}
