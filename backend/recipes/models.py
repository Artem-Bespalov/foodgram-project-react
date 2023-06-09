from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User
from foodgram.settings import (
    MAX_COOKING_TIME,
    MIN_COOKING_TIME,
    DEFAULT_COOKING_TIME,
    MAX_AMOUNT_WEIGHT_PRODUCT,
    MIN_AMOUNT_WEIGHT_PRODUCT,
)


class Tag(models.Model):
    """Модель тегов"""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тега",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет в HEX",
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Уникальный слаг",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = (
            models.UniqueConstraint(
                name="Ингредиент должен быть уникален для рецепта",
                fields=["name", "measurement_unit"],
            ),
        )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингредиенты рецепта",
        through="IngredientInRecipe",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=DEFAULT_COOKING_TIME,
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME, "Минимальное время приготовления 1 минута"
            ),
            MaxValueValidator(
                MAX_COOKING_TIME, "Максимальное время приготовления 600 минут"
            ),
        ),
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/",
        blank=True,
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name}. Автор: {self.author}"


class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в рецепте"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
        related_name="recipe_ingredients",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=(
            MinValueValidator(
                MIN_AMOUNT_WEIGHT_PRODUCT,
                "Суммарный вес продукта должен быть минимум 1 грамм",
            ),
            MaxValueValidator(
                MAX_AMOUNT_WEIGHT_PRODUCT,
                "Суммарный вес продукта должен быть максимум 3000 грамм",
            ),
        ),
    )

    class Meta:
        ordering = ["ingredient__name"]
        verbose_name = "Количество ингридиента"
        verbose_name_plural = "Количество ингридиентов"
        constraints = (
            models.UniqueConstraint(
                name="Нельзя добавить два одинаковых ингредиента",
                fields=[
                    "recipe",
                    "ingredient",
                ],
            ),
        )

    def __str__(self) -> str:
        return f"{self.ingredient}"


class Favorite(models.Model):
    """Модель избранное"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="in_favorite",
    )

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                name="Рецепт уже добавлен в избранное",
                fields=["recipe", "user"],
            ),
        ]

    def __str__(self):
        return f"{self.recipe} добавлен в избранное пользователем {self.user}"


class ShoppingCart(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="in_shopping_cart",
    )

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                name="Ингредиент в корзине должен быть уникальным",
                fields=["user", "recipe"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} добавил в список {self.recipe}"
