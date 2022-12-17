from datetime import timedelta, datetime
from unittest import mock, TestCase
from unittest.mock import patch, MagicMock, Mock

import main
from models import Humanoid


class ZombieSurvivalTest(TestCase):
    game: main.ZombieSurvival

    def setUp(self) -> None:
        self.game = main.ZombieSurvival()

    def test___init__(self):
        self.assertEqual(self.game.zombie_count, 20)
        self.assertEqual(self.game.survivor_count, 5)
        self.assertEqual(self.game.hit_chance, 60)
        self.assertEqual(self.game.zombify_chance, 30)
        self.assertTrue(self.game.storymode)
        self.assertEqual(self.game.zombie_variety, 0)
        self.assertEqual(self.game.weapon_variety, 0)
        self.assertEqual(self.game.armor_variety, 0)

    @patch('main.ZombieSurvival._show_menu', side_effect=['start', 'start', None])
    @patch('main.ZombieSurvival.start')
    def test_run__loops(self, mock_start, mock_menu):
        with self.assertRaises(SystemExit) as e:
            self.game.run()

        self.assertEqual(e.exception.args[0], 0)
        self.assertEqual(mock_start.call_count, 2)
        self.assertEqual(mock_menu.call_count, 3)

    @patch('main.ZombieSurvival._show_menu', return_value=None)
    def test_run__exit(self, mock_menu: MagicMock):
        with self.assertRaises(SystemExit) as e:
            self.game.run()

        self.assertEqual(e.exception.args[0], 0)
        self.assertEqual(mock_menu.call_count, 1)

    @patch('main.ZombieSurvival._show_menu', side_effect=['start', None])
    @patch('main.ZombieSurvival.start')
    def test_run__option_start(self, mock_start: MagicMock, mock_menu: MagicMock):
        with self.assertRaises(SystemExit) as e:
            self.game.run()

        self.assertEqual(e.exception.args[0], 0)
        self.assertEqual(mock_start.call_count, 1)
        self.assertEqual(mock_menu.call_count, 2)

    @patch('main.ZombieSurvival._show_menu', side_effect=['settings', None])
    @patch('main.ZombieSurvival.start')
    @patch('main.ZombieSurvival._show_settings')
    def test_run__option_settings(self, mock_settings: MagicMock, mock_start: MagicMock,
                                  mock_menu: MagicMock):
        with self.assertRaises(SystemExit) as e:
            self.game.run()

        self.assertEqual(e.exception.args[0], 0)
        self.assertEqual(mock_start.call_count, 0)
        self.assertEqual(mock_settings.call_count, 1)
        self.assertEqual(mock_menu.call_count, 2)

    @patch('main.ZombieSurvival._setup_game')
    @patch('main.ZombieSurvival._start_fights', return_value=timedelta(seconds=1))
    @patch('builtins.print')
    def test_start__win(self, mock_print: MagicMock, mock_fights: MagicMock, mock_setup: MagicMock):
        # setup
        self.game.storymode = False
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]

        # do it
        self.game.start()

        # postcondition
        mock_setup.assert_called_once()
        mock_fights.assert_called_once()
        mock_print.assert_has_calls([
            mock.call('Dauer: 0:00:01'),
            mock.call('Gewinner: Überlebende'),
            mock.call('Anzahl: 1')
        ])

    @patch('main.ZombieSurvival._setup_game')
    @patch('main.ZombieSurvival._start_fights', return_value=timedelta(seconds=2))
    @patch('builtins.print')
    def test_start__lose(self, mock_print: MagicMock, mock_fights: MagicMock, mock_setup: MagicMock):
        # setup
        self.game.storymode = False
        survivor = Humanoid(hit_chance=2)
        survivor.zombify(hit_chance=1)
        self.game.survivors = [survivor]
        self.game.zombies.put(survivor)

        # do it
        self.game.start()

        # postcondition
        mock_setup.assert_called_once()
        mock_fights.assert_called_once()
        mock_print.assert_has_calls([
            mock.call('Dauer: 0:00:02'),
            mock.call('Gewinner: Zombies'),
            mock.call('Anzahl: 1')
        ])

    @patch('main.ZombieSurvival._setup_game')
    @patch('main.ZombieSurvival._start_fights', return_value=timedelta(seconds=3))
    @patch('builtins.print')
    def test_start__storymode_win_single(self, mock_print: MagicMock, mock_fights: MagicMock, mock_setup: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=3)
        survivor2 = Humanoid(hit_chance=3)
        survivor2._zombie = True
        self.game.survivors = [survivor, survivor2]

        # do it
        self.game.start()

        # postcondition
        mock_setup.assert_called_once()
        mock_fights.assert_called_once()
        mock_print.assert_has_calls([
            mock.call('Die Nacht bricht an und die Zombies regen sich...'),
            mock.call('Nach grade mal 3 Stunde(n) ist die Schlacht vorbei.'),
            mock.call('Nur ein Überlebender steht noch:'),
            mock.call(f'  {survivor}'),
            mock.call('1 sind gefallen, ihre Namen sind:'),
            mock.call(f'  † {survivor2}')
        ])

    @patch('main.ZombieSurvival._setup_game')
    @patch('main.ZombieSurvival._start_fights', return_value=timedelta(seconds=3))
    @patch('builtins.print')
    def test_start__storymode_win_multi(self, mock_print: MagicMock, mock_fights: MagicMock, mock_setup: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=6)
        survivor2 = Humanoid(hit_chance=1)
        self.game.survivors = [survivor, survivor2]

        # do it
        self.game.start()

        # postcondition
        mock_setup.assert_called_once()
        mock_fights.assert_called_once()
        mock_print.assert_has_calls([
            mock.call('Die Nacht bricht an und die Zombies regen sich...'),
            mock.call('Nach grade mal 3 Stunde(n) ist die Schlacht vorbei.'),
            mock.call('2 haben überlebt, darunter sind:'),
            mock.call(f'  {survivor}'),
            mock.call(f'  {survivor2}')
        ])

    @patch('main.ZombieSurvival._setup_game')
    @patch('main.ZombieSurvival._start_fights', return_value=timedelta(seconds=4))
    @patch('builtins.print')
    def test_start__storymode_lose(self, mock_print: MagicMock, mock_fights: MagicMock, mock_setup: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=5)
        survivor._zombie = True
        self.game.zombies.put(survivor)
        survivor2 = Humanoid(hit_chance=10)
        survivor2._zombie = True
        self.game.zombies.put(survivor2)
        self.game.survivors = [survivor, survivor2]

        # do it
        self.game.start()

        # postcondition
        mock_setup.assert_called_once()
        mock_fights.assert_called_once()
        mock_print.assert_has_calls([
            mock.call('Die Nacht bricht an und die Zombies regen sich...'),
            mock.call('Nach grade mal 4 Stunde(n) ist die Schlacht vorbei.'),
            mock.call('Leider überwältigten die Zombies alle Überlebenden.'),
            mock.call('So streifen jetzt 2 Zombies weiter durch das Land.')
        ])

    @patch('builtins.print')
    def test__setup_game(self, mock_print: MagicMock):
        # setup
        self.game.storymode = False
        self.game.survivor_count = 1
        self.game.zombie_count = 1

        # precondition
        self.assertEqual(len(list(self.game.zombies.queue)), 0)
        self.assertEqual(len(self.game.survivors), 0)

        # do it
        self.game._setup_game()

        # postcondition
        self.assertEqual(len(list(self.game.zombies.queue)), 1)
        self.assertEqual(len(self.game.survivors), 1)
        mock_print.assert_called_once_with('Grrrrr')

    @patch('builtins.print')
    def test__setup_game__storymode(self, mock_print: MagicMock):
        # setup
        self.game.storymode = True
        self.game.survivor_count = 5
        self.game.zombie_count = 3

        # precondition
        self.assertEqual(len(self.game.survivors), 0)
        self.assertEqual(len(list(self.game.zombies.queue)), 0)

        # do it
        self.game._setup_game()

        # postcondition
        self.assertEqual(len(self.game.survivors), 5)
        self.assertEqual(len(list(self.game.zombies.queue)), 3)
        mock_print.assert_has_calls([
            mock.call('Zombie 1: "Grrrrr"'),
            mock.call('Zombie 2: "Grrrrr"'),
            mock.call('Zombie 3: "Grrrrr"'),
        ])

    @patch('main.datetime')
    @patch('threading.Thread')
    @patch('main.ZombieSurvival._fight_execution')
    def test__start_fights(self, mock_fight: MagicMock, mock_thread: MagicMock, mock_datetime: MagicMock):
        # setup
        date_now = datetime.now()
        mock_datetime.now = MagicMock(side_effect=[date_now, date_now + timedelta(seconds=10)])
        survivor = Humanoid(hit_chance=5)
        survivor2 = Humanoid(hit_chance=6)
        survivor3 = Humanoid(hit_chance=9)
        self.game.survivors = [survivor, survivor2, survivor3]

        # do it
        result = self.game._start_fights()

        # postcondition
        mock_thread.assert_has_calls([
            mock.call(target=mock_fight, kwargs=dict(survivor=survivor)),
            mock.call().start(),
            mock.call(target=mock_fight, kwargs=dict(survivor=survivor2)),
            mock.call().start(),
            mock.call(target=mock_fight, kwargs=dict(survivor=survivor3)),
            mock.call().start(),
            mock.call().join(),
            mock.call().join(),
            mock.call().join(),
        ])
        self.assertEqual(result, timedelta(seconds=10))

    @patch('builtins.print')
    def test__fight_execution__no_zombie(self, mock_print: MagicMock):
        # setup
        self.game.storymode = False
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_not_called()

    @patch('random.randint', Mock(return_value=0))
    @patch('builtins.print')
    def test__fight_execution__kill_zombie(self, mock_print: MagicMock):
        # setup
        self.game.storymode = False
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]
        zombie = Humanoid(hit_chance=0, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_called_once_with('Klatsch')

    @patch('random.randint', Mock(side_effect=[100, 0, 5]))  # Last value to prevent exception in zombification
    @patch('builtins.print')
    def test__fight_execution__zombie_bites(self, mock_print: MagicMock):
        # setup
        self.game.storymode = False
        zombie = Humanoid(hit_chance=1, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_has_calls([
            mock.call('Mist!'),
            mock.call('Grrrrr'),
        ])

    @patch('random.randint', side_effect=[100, 100, 0])
    @patch('builtins.print')
    def test__fight_execution__zombie_misses(self, mock_print: MagicMock, mock_randint: MagicMock):
        # setup
        self.game.storymode = False
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]
        zombie = Humanoid(hit_chance=1, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        self.assertTrue(survivor.evaded)
        self.assertEqual(mock_randint.call_count, 3)
        mock_print.assert_has_calls([
            mock.call('Mist!'),
            mock.call('Juhu'),
            mock.call('Klatsch'),
        ])

    @patch('random.randint', Mock(side_effect=[100, 0]))
    @patch('builtins.print')
    def test__fight_execution__storymode_no_zombie(self, mock_print: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=100)
        self.game.survivors = [survivor]

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_not_called()

    @patch('random.randint', Mock(return_value=0))
    @patch('builtins.print')
    def test__fight_execution__storymode_kill_zombie(self, mock_print: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=100)
        self.game.survivors = [survivor]
        zombie = Humanoid(hit_chance=0, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_has_calls([
            mock.call(f'{survivor} greift den Zombie {zombie} an.'),
            mock.call(f'*Klatsch* {survivor.name} erschlägt den Zombie {zombie.name}.'),
        ])

    @patch('builtins.print')
    def test__fight_execution__storymode_zombie_bites(self, mock_print: MagicMock):
        # setup
        self.game.storymode = True
        survivor = Humanoid(hit_chance=0)
        self.game.survivors = [survivor]
        zombie = Humanoid(hit_chance=100, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        mock_print.assert_has_calls([
            mock.call(f'{survivor} greift den Zombie {zombie} an.'),
            mock.call(f'{survivor.name}: "Mist!"'),
            mock.call(f'{survivor.name} wird von Zombie {zombie.name} gebissen und verwandelt sich.'),
            mock.call(f'Zombie {survivor.name}: "Grrrrr"')
        ])

    @patch('random.randint', side_effect=[100, 100, 0])
    @patch('builtins.print')
    def test__fight_execution__storymode_zombie_misses(self, mock_print: MagicMock, mock_randint: MagicMock):
        # setup
        self.game.storymode = True
        zombie = Humanoid(hit_chance=1, is_zombie=True, name='Foo')
        self.game.zombies.put(zombie)
        survivor = Humanoid(hit_chance=1)
        self.game.survivors = [survivor]

        # do it
        self.game._fight_execution(survivor=survivor)

        # postcondition
        self.assertTrue(survivor.evaded)
        self.assertEqual(mock_randint.call_count, 3)
        mock_print.assert_has_calls([
            mock.call(f'{survivor} greift den Zombie {zombie} an.'),
            mock.call(f'{survivor.name}: "Mist!"'),
            mock.call(f'{survivor.name}: "Juhu"'),
            mock.call(f'{survivor} greift den Zombie {zombie} an.'),
            mock.call(f'*Klatsch* {survivor.name} erschlägt den Zombie {zombie.name}.'),
        ])

    @patch('main.prompt', return_value=dict())
    def test__show_menu__no_selection(self, mock_prompt: MagicMock):
        # do it
        result = self.game._show_menu()

        # postcondition
        self.assertIsNone(result)
        mock_prompt.assert_called_once()

    @patch('main.prompt', return_value=dict(selection='foo'))
    def test__show_menu(self, mock_prompt: MagicMock):
        # do it
        result = self.game._show_menu()

        # postcondition
        self.assertEqual(result, 'foo')
        mock_prompt.assert_called_once()
        prompt_args = mock_prompt.call_args.args[0]
        self.assertSetEqual(set(prompt_args.keys()), {'type', 'name', 'message', 'choices'})
        self.assertEqual(prompt_args['type'], 'list')
        self.assertEqual(prompt_args['name'], 'selection')
        self.assertEqual(prompt_args['message'], 'Willkommen bei ZombieSurvival')
        self.assertEqual(len(prompt_args['choices']), 3)
        self.assertEqual(prompt_args['choices'][0], {"name": "Start", "value": "start"})
        self.assertEqual(prompt_args['choices'][1], {"name": "Einstellungen", "value": "settings"})
        self.assertEqual(prompt_args['choices'][2], {"name": "Beenden", "value": None})

    @patch('main.ZombieSurvival._ask_settings', side_effect=[True, True, False])
    def test__show_settings__loops_asking(self, mock_ask_settings: MagicMock):
        # do it
        self.game._show_settings()

        # postcondition
        mock_ask_settings.assert_has_calls([
            mock.call(),
            mock.call(),
            mock.call()
        ])

    @patch('main.prompt', return_value=dict())
    def test__ask_settings__no_selection(self, mock_prompt: MagicMock):
        # do it
        result = self.game._ask_settings()

        # postcondition
        mock_prompt.assert_called_once()
        self.assertFalse(result)

    @patch('main.prompt', side_effect=[dict(option={'name': 'foo'}), dict(foo=None)])
    def test__ask_settings__selection_with_no_change(self, mock_prompt: MagicMock):
        # do it
        result = self.game._ask_settings()

        # postcondition
        mock_prompt.assert_called_with(dict(name='foo'))
        self.assertFalse(result)

    @patch('main.prompt', side_effect=[dict(option={'name': 'foo'}), dict(foo='bar')])
    def test__ask_settings__selection_with_change(self, mock_prompt: MagicMock):
        # do it
        result = self.game._ask_settings()

        # postcondition
        mock_prompt.assert_called_with(dict(name='foo'))
        self.assertTrue(result)
        self.assertEqual(getattr(self.game, 'foo'), 'bar')
