import re

from django.core.exceptions import ValidationError


def validate_ingredients(ingredients_list, val_model):
    if len(ingredients_list) < 1:
        raise ValidationError(
            'Блюдо должно содержать хотя бы 1 ингредиент')
    unique_list = []
    for ingredient in ingredients_list:
        if not ingredient.get('id'):
            raise ValidationError('Укажите id ингредиента')
        ingredient_id = ingredient.get('id')
        if not val_model.objects.filter(pk=ingredient_id).exists():
            raise ValidationError(
                f'{ingredient_id}- ингредиент с таким id не найден')
        for ingredient in unique_list:
            if ingredient['id'] in ingredients_list:
                raise ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_list.append(ingredient['id'])
        if int(ingredient) < 1:
            raise ValidationError(
                f'Количество {ingredient} должно быть больше 1')


def validate_tags(tags_list, val_model):
    for tag in tags_list:
        if not val_model.objects.filter(pk=tag).exists():
            raise ValidationError(f'{tag} - Такого тэга не существует')


def validate_cooking_time(value):
    if not value or int(value) < 1:
        raise ValidationError({
            'cooking_time': 'Укажите время приготовления'})


def validate_ingredient_name(value):
    reg = r'^[\w%,"\'«»&()]+\Z'
    listik = value.split()
    for item in listik:
        if not re.fullmatch(reg, item):
            raise ValidationError({
                'Недопустимое значение имени {item}'})
