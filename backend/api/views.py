from api.serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    TagSerializer,
)
from djoser.views import UserViewSet
from recipes.models import Ingredient, Tag
from rest_framework import viewsets
from users.models import User


class UserViewSet(UserViewSet):
    """Информация о пользователях"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
