from typing import Union, Literal

__all__ = ['validate_variety', 'validate_count', 'validate_chance']


def validate_int(value: str) -> Union[str, int]:
    try:
        return int(value)
    except ValueError:
        return 'Bitte gebe eine valide Zahl ein'


def validate_count(value: str) -> Union[str, Literal[True]]:
    value = validate_int(value)
    if not isinstance(value, int):
        return value

    if value < 1:
        return 'Bitte gebe eine Zahl größer 0 ein'
    return True


def validate_variety(value: str) -> Union[str, Literal[True]]:
    value = validate_int(value)
    if not isinstance(value, int):
        return value

    if value < 0:
        return 'Bitte gebe eine positive Zahl ein'
    return True


def validate_chance(value: str) -> Union[str, Literal[True]]:
    value = validate_int(value)
    if not isinstance(value, int):
        return value

    if value not in range(0, 100):
        return 'Bitte gebe eine valide Zahl zwischen 1 und 99 an'
    return True
