from django.core.exceptions import ValidationError


def color_validator(color):
    if color[0] != '#':
        raise ValidationError("Шестнадцатиричный код цвета начинается с '#'.")
    return color
