#!/usr/bin/env python3
import random
import threading
from datetime import datetime, timedelta
from queue import Queue
from typing import Optional, List, NoReturn, Literal

from PyInquirer import prompt, Separator

from models import Humanoid
from validators import validate_variety, validate_count, validate_chance


class ZombieSurvival:
    zombies: 'Queue[Humanoid]'
    survivors: List[Humanoid]

    # Base options
    zombie_count: int
    survivor_count: int
    hit_chance: int
    zombify_chance: int

    # advanced options
    storymode: bool
    zombie_variety: Optional[int]
    weapon_variety: Optional[int]
    armor_variety: Optional[int]

    def __init__(self):
        self.zombies = Queue()
        self.survivors = list()

        self.zombie_count = 20
        self.survivor_count = 5
        self.hit_chance = 60
        self.zombify_chance = 30

        self.storymode = True
        self.zombie_variety = 0
        self.weapon_variety = 0
        self.armor_variety = 0

    def run(self):
        while True:
            selection = self._show_menu()
            if selection == 'start':
                self.start()
            elif selection == 'settings':
                self._show_settings()
            else:
                exit(0)

    def start(self):
        if self.storymode:
            print('Die Nacht bricht an und die Zombies regen sich...')

        self._setup_game()

        execution_time = self._start_fights()

        if self.storymode:
            print(f'Nach grade mal {round(execution_time.total_seconds())} Stunde(n) ist die Schlacht vorbei.')
        else:
            print(f'Dauer: {execution_time}')

        if any(self.survivors):
            survived = [s for s in self.survivors if s]
            if self.storymode:
                died = [s for s in self.survivors if not s]
                if len(survived) == 1:
                    print('Nur ein Überlebender steht noch:')
                else:
                    print(f'{len(survived)} haben überlebt, darunter sind:')
                for survivor in survived:
                    print(f'  {survivor}')
                if died:
                    print(f'{len(died)} sind gefallen, ihre Namen sind:')
                    for dead_survivor in died:
                        print(f'  † {dead_survivor}')
            else:
                print('Gewinner: Überlebende')
                print(f'Anzahl: {len(survived)}')
        else:
            zombies_alive: List[Humanoid] = list(self.zombies.queue)
            if self.storymode:
                print('Leider überwältigten die Zombies alle Überlebenden.')
                print(f'So streifen jetzt {len(zombies_alive)} Zombies weiter durch das Land.')
            else:
                print('Gewinner: Zombies')
                print(f'Anzahl: {len(zombies_alive)}')

    def _setup_game(self) -> NoReturn:
        # setup Surviors
        self.survivors = [
            Humanoid(hit_chance=self.hit_chance, armor_variety=self.armor_variety, weapon_variety=self.weapon_variety)
            for _ in range(0, self.survivor_count)
        ]

        # setup Zombies
        self.zombies = Queue()
        for _ in range(0, self.zombie_count):
            zombie = Humanoid(
                hit_chance=self.zombify_chance,
                is_zombie=True,
                zombie_variety=self.zombie_variety,
                name=str(_ + 1)
            )
            if self.storymode:
                print(f'Zombie {zombie.name}: "Grrrrr"')
            else:
                print('Grrrrr')
            self.zombies.put(zombie)

    def _start_fights(self) -> timedelta:
        start_time = datetime.now()
        fights: List[threading.Thread] = []
        for survivor in self.survivors:
            fight = threading.Thread(
                target=self._fight_execution,
                kwargs=dict(survivor=survivor)
            )
            fights.append(fight)
            fight.start()

        # Wait for all Threads to conclude
        for fight in fights:
            fight.join()

        return datetime.now() - start_time

    def _fight_execution(self, survivor: Humanoid) -> None:
        """ Handles fights between one Survivor and all Zombies """

        while not self.zombies.empty():
            zombie = self.zombies.get()
            if self.storymode:
                print(f'{survivor} greift den Zombie {zombie} an.')

            # Survivor attacks zombie
            if random.randint(1, 100) < survivor.hit_chance:
                if self.storymode:
                    print(f'*Klatsch* {survivor.name} erschlägt den Zombie {zombie.name}.')
                else:
                    print('Klatsch')
                self.zombies.task_done()
                continue
            else:
                if self.storymode:
                    print(f'{survivor.name}: "Mist!"')
                else:
                    print('Mist!')
                self.zombies.put(zombie)

            # Zombie attacks survivor
            if random.randint(1, 100) < (zombie.hit_chance - survivor.defense):
                survivor.zombify(hit_chance=self.zombify_chance, zombie_variety=self.zombie_variety)
                if self.storymode:
                    print(f'{survivor.name} wird von Zombie {zombie.name} gebissen und verwandelt sich.')
                    print(f'Zombie {survivor.name}: "Grrrrr"')
                else:
                    print('Grrrrr')
                self.zombies.put(survivor)
                return
            else:
                survivor.evaded = True  # Optional
                if self.storymode:
                    print(f'{survivor.name}: "Juhu"')
                else:
                    print('Juhu')

    @staticmethod
    def _show_menu() -> Optional[Literal['start', 'settings']]:
        result = prompt({
            'type': 'list',
            'name': 'selection',
            'message': 'Willkommen bei ZombieSurvival',
            'choices': [
                {
                    "name": "Start",
                    "value": "start",
                },
                {
                    "name": "Einstellungen",
                    "value": "settings",
                },
                {
                    "name": "Beenden",
                    "value": None,
                }
            ]
        })
        return result.get('selection')

    def _show_settings(self) -> NoReturn:
        while True:
            if not self._ask_settings():
                return

    def _ask_settings(self) -> bool:
        answer = prompt({
            'type': 'list',
            'name': 'option',
            'message': "Einstellungen",
            'choices': [
                {
                    "name": f"Anzahl Zombies ({self.zombie_count})",
                    "value": {
                        'type': 'input',
                        'name': 'zombie_count',
                        'message': 'Wie viele Zombies soll es am Anfang des Szenarios geben?',
                        'validate': validate_count,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": f"Anzahl Überlebende ({self.survivor_count})",
                    "value": {
                        'type': 'input',
                        'name': 'survivor_count',
                        'message': 'Wie viele Überlebende soll es am Anfang des Szenarios geben?',
                        'validate': validate_count,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": f"Trefferchance Überlebende ({self.hit_chance}%)",
                    "value": {
                        'type': 'input',
                        'name': 'hit_chance',
                        'message': 'Welche Trefferwahrscheinlichkeit haben die Überlebenden um Zombies zu töten?',
                        'validate': validate_chance,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": f"Trefferchance Zombies ({self.zombify_chance}%)",
                    "value": {
                        'type': 'input',
                        'name': 'zombify_chance',
                        'message': 'Wie hoch ist die Wahrscheinlichkeit von einem Zombie verwandelt zu werden?',
                        'validate': validate_chance,
                        'filter': lambda a: int(a)
                    }
                },
                Separator(),
                {
                    "name": f"Storymodus ({'Ja' if self.storymode else 'Nein'})",
                    "value": {
                        'type': 'confirm',
                        'name': 'storymode',
                        'message': 'Soll der Storymodus aktiviert werden?',
                        'default': False,
                    }
                },
                {
                    "name": f"Zombie Variation (+/- {self.zombie_variety}%)",
                    "value": {
                        'type': 'input',
                        'name': 'zombie_variety',
                        'message': 'Wie groß soll die Varianz zwischen einzelnen Zombies sein?',
                        'validate': validate_variety,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": f"Waffen Variation (0 ~ {self.weapon_variety}%)",
                    "value": {
                        'type': 'input',
                        'name': 'weapon_variety',
                        'message': 'Wie groß soll die Varianz der Waffen von Überlebenden sein?',
                        'validate': validate_variety,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": f"Rüstungs Variation (0 ~ {self.armor_variety}%)",
                    "value": {
                        'type': 'input',
                        'name': 'armor_variety',
                        'message': 'Wie groß soll die Varianz der Rüstungen von Überlebenden sein?',
                        'validate': validate_variety,
                        'filter': lambda a: int(a)
                    }
                },
                {
                    "name": "Zurück",
                    "value": None
                }
            ]
        })

        selected_option = answer.get('option')
        if selected_option is None:
            return False

        option_name = selected_option.get('name')
        option_new_value = prompt(selected_option).get(option_name)

        if option_new_value is None:
            return False

        setattr(self, option_name, option_new_value)
        return True


if __name__ == '__main__':  # pragma: no cover
    ZombieSurvival().run()
