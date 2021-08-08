from django.contrib import admin

from .models import (Cart, CustomUser, Favorite, 
                     Ingredient, Recipe, Subsribe, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit",)
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "name", "show_count_add_to_favorite")
    list_filter = ("author", "name", "tags",)

    def show_count_add_to_favorite(self, obj):
        return obj.favorites.count()
   

@admin.register(Subsribe)
class SubsribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author",)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username",)
    list_filter = ("email", "username")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe",)
