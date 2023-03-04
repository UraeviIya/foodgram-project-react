from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Панель управление рецептами """
    list_display = (
        'id',
        'name',
        'text',
        'author',
    )
    search_fields = (
        'name',
        'author',
        'tags',
    )
    list_filter = (
        'name',
        'author',
        # 'tags__slug',
    )
    ordering = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Панель управление тегами """
    list_display = (
        'name',
        'color',
        'slug',
        'id'
    )
    search_fields = (
        'name',
        'slug'
    )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Панель управление ингредиентами"""
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = ('name', )
    empty_value_display = '-пусто-'
    ordering = ('name',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """ Панель управления ингредиентами в рецептах"""
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe',
        'ingredient',
    )
    # list_filter = ('recipe', 'ingredient', )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ Панель управления корзиной с рецептами"""
    list_display = (
        'recipe',
        'user',
        'date_added',
    )
    search_fields = (
        'recipe',
        'user',
        'date_added',
    )
    # list_filter = ('recipe', 'user', 'date_added',)
    empty_value_display = '-пусто-'
