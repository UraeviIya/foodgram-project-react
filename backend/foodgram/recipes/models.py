from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиенты',
        max_length=50,
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
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Как готовить это блюдо'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег блюда',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1, editable=False,
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1),))
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

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
    amount = models.IntegerField(
        validators=[MinValueValidator(1)]
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
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'{self.recipe.name} {self.user.username}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Избранный рецепт',
        related_name='favorite',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='favorite',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_favorites'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.recipe.name} {self.user.username}'
