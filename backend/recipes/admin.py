from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "author",
    )
    inlines = (RecipeIngredientInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = (
        "recipe",
        "amount",
    )


class IngredientResourse(resources.ModelResource):
    class Meta:
        model = Ingredient
        fields = (
            "name",
            "measurement_unit",
        )
        exclude = ("id",)
        import_id_fields = (
            "name",
            "measurement_unit",
        )


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResourse]
    list_display = (
        "name",
        "measurement_unit",
    )
