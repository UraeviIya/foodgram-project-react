from django.contrib import admin

from .models import (Ingredient, IngredientRecipe, Recipe, ShoppingCart,
                     Tag, Favorite)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Панель управление рецептами"""
    list_display = (
        'id',
        'name',
        'text',
        'author',
        'favorite',
        'pub_date'
    )
    readonly_fields = ('favorite',)
    search_fields = (
        'shopping_carts__user',
        'shopping_carts__author',
        'recipe__tags',
    )
    list_filter = (
        'name',
        'author',
    )
    inlines = (IngredientRecipeInline,)
    ordering = ('name',)
    empty_value_display = '-пусто-'

    def favorite(self, obj):
        return obj.favorite.all().count()
    favorite.short_description = 'Раз в избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Панель управление тегами """
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
    """Панель управление ингредиентами"""
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
    """Панель управления ингредиентами в рецептах"""
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe',
        'ingredient',
    )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Панель управления корзиной с рецептами"""
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
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    list_display = (
        'recipe',
        'recipe_fev',
    )
    list_filter = ('recipe_fev',)
