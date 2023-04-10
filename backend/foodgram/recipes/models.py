from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_ingredient_name
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиенты',
        max_length=50,
        validators=[validate_ingredient_name]
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=10,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    COLOR_CHOICES = [
        ('#ffffff', 'Белый'),
        ('#009900', 'Зеленый'),
        ('#ff0000', 'Красный'),
        ('#0000ff', 'Синий'),
    ]

    name = models.CharField(
        verbose_name='Тег',
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тэга',
        choices=COLOR_CHOICES,
    )
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='slug тега',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='recipe')
    name = models.CharField(
        verbose_name='Название', max_length=200,
        validators=[validate_ingredient_name])
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Фотография блюда')
    text = models.TextField(
        verbose_name='Описание')
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги')
    cooking_time = models.PositiveSmallIntegerField(
        default=1, blank=False,
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Должно быть больше 0'),
            MaxValueValidator(600, 'Что-то долго готовится')])
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(fields=['author', 'name'],
                                    name='unique_author_recipename')
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(
                1, message='Минимальное количество ингридиентов 1'),),
        verbose_name='Количество',
    )

    def __str__(self):
        return f'{self.ingredient.name} {self.recipe.name} {self.amount}'


class ShoppingCart(models.Model):
    """Модель рецепта добавленного в корзину."""
    recipe = models.ForeignKey(
        verbose_name='Рецепты в списке покупок',
        related_name='shopping_carts',
        to=Recipe,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        verbose_name='Владелец списка',
        related_name='shopping_carts',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_shopping cart'
            ),
        )

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'{self.recipe.name} {self.user.username}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    recipe_fev = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Добавил в избранное',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'recipe_fev'),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.recipe_fev.username}'
