from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import CreateDestroyViewSet
from .paginators import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра списка рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """Вюсет подписок."""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return Subscribe.objects.filter(
            user=self.request.user).prefetch_related('author')


class SubscribeView(APIView):
    """Вьюсет для создания и удаления подписок."""
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.filter(
            author=author, user=request.user)
        if subscription.exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        queryset = Subscribe.objects.create(author=author, user=request.user)
        serializer = SubscribeSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        subscription = Subscribe.objects.filter(
            author=author, user=user)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы еще не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет избранных рецептов."""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe': self.kwargs.get('recipe_id')})
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(
            recipe_fev=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        recipe_fev = self.request.user
        if not Favorite.objects.filter(recipe=recipe,
                                       recipe_fev=recipe_fev).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Favorite,
            recipe_fev=recipe_fev,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    """Вьюсет для добваления и удаления рецептов из корзины покупок."""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        context.update({'recipe': recipe})
        context.update({'user': self.request.user})
        return context

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        user = self.request.user
        if not ShoppingCart.objects.filter(recipe=recipe,
                                           user=user).exists():
            return Response({'errors': 'Рецепт не добавлен в список покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingCart,
            user=user,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        if not ShoppingCart.objects.filter(user=request.user).exists():
            return Response({'errors': 'В вашем списке покупок ничего нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        rec_pk = ShoppingCart.objects.filter(
            user=request.user).values('recipe_id')
        ingredients = IngredientRecipe.objects.filter(
            recipe_id__in=rec_pk).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount')).order_by()

        text = 'Список покупок:\n\n'
        for item in ingredients:
            text += (f'{item["ingredient__name"]}: '
                     f'{item["amount"]} '
                     f'{item["ingredient__measurement_unit"]}\n')

        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
