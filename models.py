import random
from typing import List

from names import get_first_name, get_last_name

__all__ = ['Humanoid']


class Humanoid:
    _hit_chance: int
    _hit_modifier: int
    _defense_modifier: int
    _zombie: bool
    name: str
    evaded: bool

    def __init__(
            self,
            hit_chance: int,
            is_zombie: bool = False,
            zombie_variety: int = None,
            weapon_variety: int = None,
            armor_variety: int = None,
            name: str = None
    ):
        self.name = name if name else f'{get_first_name()} {get_last_name()}'
        self.hit_chance = hit_chance
        self._hit_modifier = 0
        self._defense_modifier = 0
        self._zombie = False
        self.evaded = False

        if is_zombie:
            self.zombify(hit_chance=hit_chance, zombie_variety=zombie_variety)
        else:
            # Optional: Setup Weapons/Armors
            self._defense_modifier = random.randint(0, armor_variety) if isinstance(armor_variety, int) else 0
            self._hit_modifier = random.randint(0, weapon_variety) if isinstance(weapon_variety, int) else 0

    def zombify(self, hit_chance: int, zombie_variety: int = None):
        self._zombie = True
        self.hit_chance = hit_chance
        self._hit_modifier = random.randint(-zombie_variety, zombie_variety) if isinstance(zombie_variety, int) else 0

    @property
    def hit_chance(self) -> int:
        chance = self._hit_chance + self._hit_modifier
        if not self._zombie and self.evaded:  # Optional
            chance += 3
        return chance

    @hit_chance.setter
    def hit_chance(self, value: int):
        if value >= 100:
            self._hit_chance = 99
        elif value < 1:
            self._hit_chance = 1
        else:
            self._hit_chance = value

    @property
    def defense(self) -> int:
        return self._defense_modifier

    @property
    def modifier_info(self):
        modifier: List[str] = []
        if self._hit_modifier:
            modifier.append(f'{self._hit_modifier}⚔')
        if self._defense_modifier:
            modifier.append(f'{self._defense_modifier}🛡')

        if modifier:
            return f"({' '.join(modifier)})"
        return ''

    def __bool__(self):
        """ Quick way to determine if Human is still alive """
        return not self._zombie

    def __repr__(self):
        return f'{self.name}{self.modifier_info}'
