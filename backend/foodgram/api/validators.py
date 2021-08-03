from django.core.exceptions import ValidationError 


def amount_validator(value):
    if value < 1:
        raise ValidationError('Количество не может быть меньше 1!')

def cooking_time_validator(value):
    if value < 1:
        raise ValidationError('Время приготовления не может быть меньше 1!')
