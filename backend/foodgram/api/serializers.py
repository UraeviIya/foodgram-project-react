from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .validators import (validate_cooking_time, validate_ingredients,
                         validate_tags)


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор рецептов
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для использования с моделью Tag.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Favorite.
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if Favorite.objects.filter(recipe_fev=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном'})
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью User.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Subscribe.
    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscrubed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscrubed',
                  'recipes', 'recipes_count')

    def get_is_subscrubed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.author.recipe.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                raise serializers.ValidationError({
                    'errors': 'recipes_limit должен быть числом'})
        return RecipeToRepresentationSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью IngredientInRecipe.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью Recipe.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, recipe_fev=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(queryset, many=True).data

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        cooking_time = data.get('cooking_time')

        if not tags:
            raise serializers.ValidationError({
                'tags': 'Кажется вы забыли указать тэги'})
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Кажется вы забыли указать ингредиенты'})
        validate_tags(tags, Tag)
        validate_ingredients(ingredients, Ingredient)
        validate_cooking_time(cooking_time)
        data.update({
            'tags': tags,
            'ingredients': ingredients,
            'author': self.context.get('request').user
        })
        return data

    def create(self, validated_data):
        tags = self.validated_data.pop('tags')
        ingredients = self.validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(
            name=self.validated_data.pop('name'),
            image=self.validated_data.pop('image'),
            text=self.validated_data.pop('text'),
            cooking_time=self.validated_data.pop('cooking_time'),
            author=self.validated_data.pop('author'))
        new_recipe.tags.add(*tags)
        bulk_create_data = (
            IngredientRecipe(
                recipe=new_recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.get('id')),
                amount=ingredient.get('amount'))
            for ingredient in ingredients)
        IngredientRecipe.objects.bulk_create(bulk_create_data)
        return new_recipe

    def update(self, instance, validated_data):
        new_tags = self.validated_data.pop('tags')
        new_ingredients = self.validated_data.pop('ingredients')

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        IngredientRecipe.objects.filter(recipe=instance).delete()
        bulk_create_data = (
            IngredientRecipe(
                recipe=instance,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.get('id')),
                amount=ingredient.get('amount'))
            for ingredient in new_ingredients)
        IngredientRecipe.objects.bulk_create(bulk_create_data)

        instance.tags.clear()
        instance.tags.set(new_tags)

        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления и удаления рецепта из списка покупок.
    """
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        data['recipe'] = recipe
        data['user'] = user
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в списке покупок'})
        return data

    def to_representation(self, instance):
        requset = self.context.get('request')
        return RecipeToRepresentationSerializer(
            instance.recipe,
            context={'request': requset}
        ).data
