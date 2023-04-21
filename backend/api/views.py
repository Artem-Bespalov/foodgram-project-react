from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (
    CustomUserSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    StrippedRecipeSerializer,
    TagSerializer,
)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import MyPaginator


class UserViewSet(UserViewSet):
    """
    Работа с пользователями, подписка и отмена подписок на пользователей
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = MyPaginator

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)

        if request.method == "POST":
            serializer = FollowSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid()
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(Follow, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Работа с тегами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Работа с ингредиентами"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Работа с рецептами(создание и редактирование), добавление рецептов
    в избранное, добавление в корзину и скачивание списка покупок
    """

    queryset = Recipe.objects.all()
    pagination_class = MyPaginator
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        recipe = self.get_object()

        if request.method == "POST":
            serializer = StrippedRecipeSerializer(recipe)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == "DELETE":
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        recipe = self.get_object()

        if request.method == "POST":
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = StrippedRecipeSerializer(recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == "DELETE":
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
