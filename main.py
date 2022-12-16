#!/usr/bin/env python3
import random
import threading
from datetime import datetime, timedelta
from queue import Queue
from typing import TypedDict, Optional, List, NoReturn

from PyInquirer import prompt

from models import Zombie, Survior
from validators import ValidateCount, ValidateChance


class GameParameters(TypedDict):
    zombie_count: int
    suvivor_count: int
    hit_chance: int
    zombify_chance: int


class ZombieSurvival:
    parameters: GameParameters
    zombies: 'Queue[Zombie]'
    survivors: List[Survior]

    def __init__(self):
        self.parameters = self.ask_game_parameters()
        if not self.parameters:
            return

        print('Die Nacht bricht an und die Zombies regen sich...')

        self.setup_game()

        execution_time = self.start_fights()

        print(f'Nach grade mal {round(execution_time.total_seconds(), 2)}s ist die Schlacht vorbei.')

        if any(self.survivors):
            survived = [s for s in self.survivors if not s.dead]
            died = [s for s in self.survivors if s.dead]
            print(f'{len(survived)} haben überlebt, darunter sind:')
            for survivor in survived:
                print(f'  {survivor.name}')
            if died:
                print(f'{len(died)} sind gefallen, ihre Namen sind:')
                for dead in died:
                    print(f'  † {dead.name}')
        else:
            zombies_alive: List[Zombie] = []
            while not self.zombies.empty():
                zombies_alive.append(self.zombies.get())

            print('Leider überwältigten die Zombies alle Überlebenden.')
            print(f'So streifen jetzt {len(zombies_alive)} Zombies weiter durch das Land.')

        print('### ENDE ###')

    def setup_game(self) -> NoReturn:
        # setup Surviors
        self.survivors = [
            Survior(hit_chance=self.parameters['hit_chance'])
            for _ in range(0, self.parameters['suvivor_count'])
        ]

        # setup Zombies
        self.zombies = Queue()
        print(self.parameters)
        for number in range(1, self.parameters['zombie_count'] + 1):
            self.zombies.put(Zombie(hit_chance=self.parameters['zombify_chance'], last_name=f'{number}'))

    def start_fights(self) -> timedelta:
        start_time = datetime.now()
        fights: List[threading.Thread] = []
        for survivor in self.survivors:
            fight = threading.Thread(
                target=self.fight_execution,
                kwargs=dict(survivor=survivor)
            )
            fights.append(fight)
            fight.start()

        # Wait for all Threads to conclude
        for fight in fights:
            fight.join()

        return datetime.now() - start_time

    def fight_execution(self, survivor: Survior) -> None:
        """ Handles fights between one Survivor and all Zombies """

        while not self.zombies.empty():
            zombie = self.zombies.get()
            print(f'{survivor.name} greift {zombie.name} an.')

            # Survivor attacks zombie
            if random.randint(1, 100) < survivor.hit_chance:
                print(f'*Klatsch*, {survivor.name} erschlägt {zombie.name}.')
                self.zombies.task_done()
                continue
            else:
                print(f'{survivor.name}: "Mist!"')
                self.zombies.put(zombie)

            # Zombie attacks survivor
            if random.randint(1, 100) < zombie.hit_chance:
                print(f'{survivor.name} wird von {zombie.name} gebissen und verwandelt sich.')
                survivor.dead = True
                new_zombie = Zombie(hit_chance=self.parameters['zombify_chance'], first_name=survivor.first_name, last_name=survivor.last_name)
                self.zombies.put(new_zombie)
                return
            else:
                survivor.evaded = True  # Optional
                print(f'{survivor.name}: "Juhu"')

    @staticmethod
    def ask_player_to_play() -> bool:
        result = prompt({
            'type': 'list',
            'name': 'play',
            'message': 'Willkommen bei ZombieSurvival',
            'choices': [
                {
                    "name": "Start",
                    "value": True,
                },
                {
                    "name": "Beenden",
                    "value": False,
                }
            ]
        })
        return result.get('play', False)

    @staticmethod
    def ask_game_parameters() -> Optional[GameParameters]:
        return prompt([
            {
                'type': 'input',
                'name': 'zombie_count',
                'message': 'Wie viele Zombies soll es am Anfang des Szenarios geben?',
                'validate': ValidateCount,
                'filter': lambda a: int(a)
            },
            {
                'type': 'input',
                'name': 'suvivor_count',
                'message': 'Wie viele Überlebende soll es am Anfang des Szenarios geben?',
                'validate': ValidateCount,
                'filter': lambda a: int(a)
            },
            {
                'type': 'input',
                'name': 'hit_chance',
                'message': 'Welche Trefferwahrscheinlichkeit haben die Überlebenden um Zombies zu töten?',
                'validate': ValidateChance,
                'filter': lambda a: int(a)
            },
            {
                'type': 'input',
                'name': 'zombify_chance',
                'message': 'Wie hoch ist die Wahrscheinlichkeit von einem Zombie verwandelt zu werden?',
                'validate': ValidateChance,
                'filter': lambda a: int(a)
            },
        ])


if __name__ == '__main__':
    close = False
    while not close:
        if ZombieSurvival.ask_player_to_play():
            ZombieSurvival()
        else:
            close = True
    exit(0)
