from unittest import TestCase, mock

from models import Humanoid


class ValidatorTest(TestCase):

    def test___init____base_survivor(self):
        survivor = Humanoid(hit_chance=1)

        self.assertIsInstance(survivor.name, str)
        self.assertTrue(survivor.name)
        self.assertEqual(survivor.hit_chance, 1)
        self.assertEqual(survivor._hit_modifier, 0)
        self.assertEqual(survivor._defense_modifier, 0)
        self.assertFalse(survivor._zombie)
        self.assertFalse(survivor.evaded)

    def test___init____base_survivor_3_extra_chance_after_evade(self):
        survivor = Humanoid(hit_chance=1)

        # precondition
        self.assertEqual(survivor.hit_chance, 1)
        self.assertFalse(survivor.evaded)

        # do it
        survivor.evaded = True

        # postcondition
        self.assertEqual(survivor.hit_chance, 1 + 3)
        self.assertTrue(survivor.evaded)

    @mock.patch('random.randint', mock.Mock(return_value=5))
    def test___init____survivor_with_armor(self):
        survivor = Humanoid(hit_chance=1, armor_variety=10)

        self.assertIsInstance(survivor.name, str)
        self.assertTrue(survivor.name)
        self.assertEqual(survivor.hit_chance, 1)
        self.assertEqual(survivor._hit_modifier, 0)
        self.assertEqual(survivor._defense_modifier, 5)
        self.assertFalse(survivor._zombie)
        self.assertFalse(survivor.evaded)

    @mock.patch('random.randint', mock.Mock(return_value=5))
    def test___init____survivor_with_weapon(self):
        survivor = Humanoid(hit_chance=1, weapon_variety=10)

        self.assertIsInstance(survivor.name, str)
        self.assertTrue(survivor.name)
        self.assertEqual(survivor.hit_chance, 1 + 5)  # modifer applied
        self.assertEqual(survivor._hit_modifier, 5)
        self.assertEqual(survivor._defense_modifier, 0)
        self.assertFalse(survivor._zombie)
        self.assertFalse(survivor.evaded)

    def test___init____base_zombie(self):
        survivor = Humanoid(hit_chance=1, is_zombie=True)

        self.assertTrue(survivor.name)
        self.assertIsInstance(survivor.name, str)
        self.assertEqual(survivor.hit_chance, 1)
        self.assertEqual(survivor._hit_modifier, 0)
        self.assertEqual(survivor._defense_modifier, 0)
        self.assertTrue(survivor._zombie)
        self.assertFalse(survivor.evaded)

    @mock.patch('random.randint', mock.Mock(return_value=3))
    def test___init____variety_zombie(self):
        survivor = Humanoid(hit_chance=1, is_zombie=True, zombie_variety=10)

        self.assertTrue(survivor.name)
        self.assertIsInstance(survivor.name, str)
        self.assertEqual(survivor.hit_chance, 1 + 3)
        self.assertEqual(survivor._hit_modifier, 3)
        self.assertEqual(survivor._defense_modifier, 0)
        self.assertTrue(survivor._zombie)
        self.assertFalse(survivor.evaded)

    def test_hit_chance__setter_bounds(self):
        survivor = Humanoid(hit_chance=1)

        for x in range(-5, 101):
            survivor.hit_chance = x
            if x > 99:
                self.assertEqual(survivor._hit_chance, 99)
            elif x < 1:
                self.assertEqual(survivor._hit_chance, 1)
            else:
                self.assertEqual(survivor._hit_chance, x)

    def test_defense(self):
        survivor = Humanoid(hit_chance=1)
        mock_value = mock.MagicMock()
        survivor._defense_modifier = mock_value

        self.assertEqual(survivor.defense, mock_value)

    def test_modifier_info__no_modifiers(self):
        survivor = Humanoid(hit_chance=1)

        self.assertEqual(survivor.modifier_info, '')

    def test_modifier_info__only_hit_modifier(self):
        survivor = Humanoid(hit_chance=1)
        survivor._hit_modifier = 3

        self.assertEqual(survivor.modifier_info, '(3⚔)')

    def test_modifier_info__only_defense_modifier(self):
        survivor = Humanoid(hit_chance=1)
        survivor._defense_modifier = 3

        self.assertEqual(survivor.modifier_info, '(3🛡)')

    def test_modifier_info__modifiers(self):
        survivor = Humanoid(hit_chance=1)
        survivor._hit_modifier = 5
        survivor._defense_modifier = 3

        self.assertEqual(survivor.modifier_info, '(5⚔ 3🛡)')

    def test___bool__(self):
        survivor = Humanoid(hit_chance=1)

        self.assertTrue(survivor)
        survivor._zombie = True
        self.assertFalse(survivor)

    def test___repr__(self):
        survivor = Humanoid(hit_chance=1)

        self.assertEqual(str(survivor), f'{survivor.name}{survivor.modifier_info}')
