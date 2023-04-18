from api.serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from users.models import User

from .pagination import MyPaginator


class UserViewSet(UserViewSet):
    """Информация о пользователях"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = MyPaginator


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPaginator

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
