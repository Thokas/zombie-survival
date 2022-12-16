from typing import Optional

from names import get_first_name, get_last_name

__all__ = ['Survior', 'Zombie']


class Human:
    _hit_chance: int
    first_name: str
    last_name: str

    def __init__(self, hit_chance: int, first_name: Optional[str] = None, last_name: Optional[str] = None):
        self.hit_chance = hit_chance
        self.first_name = first_name or get_first_name()
        self.last_name = last_name or get_last_name()

    @property
    def hit_chance(self) -> int:
        return self._hit_chance

    @hit_chance.setter
    def hit_chance(self, value: int):
        if value not in range(1, 100):
            raise ValueError('Hit probability must be in range from 1 to 99', value)
        self._hit_chance = value

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


class Survior(Human):
    dead: bool = False
    evaded: bool = False

    @Human.hit_chance.getter
    def hit_chance(self) -> int:
        return self._hit_chance + 3 if self.evaded else self._hit_chance  # Optional

    def __bool__(self):
        """ Quick way to determine if Survivor still is alive """
        return not self.dead


class Zombie(Human):

    def __init__(self, hit_chance: int, first_name: Optional[str] = None, last_name: Optional[str] = None):
        super().__init__(
            hit_chance=hit_chance,
            first_name='Zombie',
            last_name=f'{first_name} {last_name}' if first_name else last_name
        )
        print(f'{self.name}: Grrrrr')
