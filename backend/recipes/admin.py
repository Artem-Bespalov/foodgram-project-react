from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Favourite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "author",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
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
