from django.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Создание пользователя"""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "password",
            "username",
            "first_name",
            "last_name",
        )


class CustomUserSerializer(UserSerializer):
    """Получение данных о пользователях"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated and obj.following.filter(user=user).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Связь ингредиентов и их количества для получения рецепта"""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов"""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated and obj.following.filter(user=user).exists()
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and obj.in_favorite.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and obj.in_shopping_cart.filter(user=user).exists()
        )


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Связь ингредиентов и их количества для создания рецепта"""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")

    def validate_amount(self, value):
        if value <= settings.MIN_AMOUNT_WEIGHT_PRODUCT:
            raise ValidationError(
                "Суммарный вес продукта должен быть минимум 1 грамм"
            )
        if value > settings.MAX_AMOUNT_WEIGHT_PRODUCT:
            raise ValidationError(
                "Суммарный вес продукта должен быть максимум 3000 грамм"
            )
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи и обновления рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = CustomUserSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate_cooking_time(self, value):
        if value <= settings.MIN_COOKING_TIME:
            raise ValidationError("Минимальное время приготовления 1 минута")
        if value > settings.MAX_COOKING_TIME:
            raise ValidationError("Максимальное время приготовления 600 минут")
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError("Нужно добавить хотя бы один ингредиент")
        ingredients = [item["id"] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError(
                "У рецепта не может быть два одинаковых ингредиента"
            )
        return value

    def add_ingredients(self, recipe, tags, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, image=image, **validated_data
        )
        recipe.tags.set(tags)
        self.add_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(
            recipe=instance, ingredient__in=instance.ingredients.all()
        ).delete()
        self.add_ingredients(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class StrippedRecipeSerializer(serializers.ModelSerializer):
    """Укороченное представление рецепта"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для подписки"""

    id = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated and obj.following.filter(user=user).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = StrippedRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data
