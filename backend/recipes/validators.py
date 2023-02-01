from django.core.exceptions import ValidationError


def validate_amount(value):
    if value < 1:
        raise ValidationError('Количество не может быть меньше 1')
    if value > 2999:
        raise ValidationError('Количество не может быть больше 2999')


def validate_cooking_time(value):
    if value < 0:
        raise ValidationError(
            'Время приготовления не может быть отрицательным')
    if value > 900:
        raise ValidationError(
            'Время приготовления не может быть больше 900')
