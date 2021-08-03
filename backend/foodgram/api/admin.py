from django.contrib import admin
from django.shortcuts import get_object_or_404

from .models import Cart, CustomUser, Favorite, Ingredient, Recipe, Subsribe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit",)
    list_filter = ("name",)
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "title", "show_count_add_to_favorite")
    list_filter = ("author", "title", "tags",)

    def show_count_add_to_favorite(self, obj):
        return (
            get_object_or_404(Recipe, pk=obj.id).favorites.count()
        )
    

@admin.register(Subsribe)
class SubsribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author",)
    pass


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username",)
    list_filter = ("email", "username")
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipes",)
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipes",)
    pass
