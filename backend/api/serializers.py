from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
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
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


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

    def get_is_favorited(self, obj):
        return (
            self.context.get("request").user.is_authenticated
            and Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get("request").user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Связь ингредиентов и их количества для создания рецепта"""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


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

    def add_tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
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
        self.add_tags_and_ingredients(recipe, tags, ingredients)
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
        IngredientInRecipe.objects.filter(
            recipe=instance, ingredient__in=instance.ingredients.all()
        ).delete()
        self.add_tags_and_ingredients(instance, tags, ingredients)
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
        request = self.context.get("request")
        return Follow.objects.filter(user=request.user, author=obj).exists()

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
