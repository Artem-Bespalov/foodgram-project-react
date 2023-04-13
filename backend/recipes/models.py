from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


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
        ordering = ["id"]
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
        default=1,
        validators=(
            MinValueValidator(1, "Минимальное время приготовления 1 минута"),
        ),
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="media/recipes/",
        blank=True,
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name}. Автор: {self.author.username}"


class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в рецепте"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        default=1,
        verbose_name="Рецепт",
        validators=[MinValueValidator(1, "Должен быть хотябы 1 ингредиент")],
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
    )

    class Meta:
        ordering = ["-id"]
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
        return f"{self.ingredients}"


class Favourite(models.Model):
    """Модель избранное"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favourite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="in_favourite",
    )

    class Meta:
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


class ShoppingList(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_user",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
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
