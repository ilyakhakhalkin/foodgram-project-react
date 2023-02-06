from django.core.exceptions import ValidationError

from foodgram.settings import (MAX_COOKING_TIME,
                               MIN_COOKING_TIME,
                               MAX_INGREDIENT_AMOUNT,
                               MIN_INGREDIENT_AMOUNT)


def validate_amount(value):
    if value < MIN_INGREDIENT_AMOUNT:
        raise ValidationError(
            F'Количество не может быть меньше {MIN_INGREDIENT_AMOUNT}'
        )
    if value > MAX_INGREDIENT_AMOUNT:
        raise ValidationError(
            F'Количество не может быть больше {MAX_INGREDIENT_AMOUNT}'
        )


def validate_cooking_time(value):
    if value < MIN_COOKING_TIME:
        raise ValidationError(
            f'''Время приготовления не может быть меньше {MIN_COOKING_TIME} минуты'''
        )
    if value > MAX_COOKING_TIME:
        raise ValidationError(
            f'Время приготовления не может быть больше {MAX_COOKING_TIME}'
        )
