from prompt_toolkit.validation import Validator, ValidationError

__all__ = ['ValidateCount', 'ValidateChance']


class ValidateCount(Validator):
    def validate(self, document):
        try:
            value = int(document.text)
        except ValueError:
            raise ValidationError(
                message='Bitte gebe eine valide Zahl ein',
                cursor_position=len(document.text)
            )

        if value < 1:
            raise ValidationError(
                message='Bitte gebe eine Zahl größer 0 ein',
                cursor_position=len(document.text)
            )
        return value


class ValidateChance(ValidateCount):
    def validate(self, document):
        chance = super().validate(document)

        if chance not in range(0, 100):
            raise ValidationError(
                message='Bitte gebe eine valide Zahl zwischen 1 und 99 an',
                cursor_position=len(document.text)
            )
        return chance
