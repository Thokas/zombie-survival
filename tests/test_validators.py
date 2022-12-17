from unittest import TestCase

from validators import validate_int, validate_variety, validate_chance, validate_count


class ValidatorTest(TestCase):

    def test_validate_int(self):
        self.assertEqual(validate_int(''), 'Bitte gebe eine valide Zahl ein')
        self.assertEqual(validate_int('foo'), 'Bitte gebe eine valide Zahl ein')
        self.assertEqual(validate_int('1'), 1)

    def test_validate_count(self):
        self.assertEqual(validate_count(''), 'Bitte gebe eine valide Zahl ein')
        self.assertEqual(validate_count('-1'), 'Bitte gebe eine Zahl größer 0 ein')
        self.assertEqual(validate_count('0'), 'Bitte gebe eine Zahl größer 0 ein')
        self.assertTrue(validate_count('1'))

    def test_validate_variety(self):
        self.assertEqual(validate_variety(''), 'Bitte gebe eine valide Zahl ein')
        self.assertEqual(validate_variety('-1'), 'Bitte gebe eine positive Zahl ein')
        self.assertTrue(validate_variety('0'))
        self.assertTrue(validate_variety('1'))

    def test_validate_chance(self):
        self.assertEqual(validate_chance(''), 'Bitte gebe eine valide Zahl ein')
        self.assertEqual(validate_chance('-1'), 'Bitte gebe eine valide Zahl zwischen 1 und 99 an')
        self.assertEqual(validate_chance('0'), 'Bitte gebe eine valide Zahl zwischen 1 und 99 an')
        self.assertEqual(validate_chance('100'), 'Bitte gebe eine valide Zahl zwischen 1 und 99 an')
        self.assertTrue(validate_chance('1'))
        self.assertTrue(validate_chance('99'))
