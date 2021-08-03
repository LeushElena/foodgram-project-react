from django_filters.rest_framework import FilterSet, filters

from rest_framework.filters import SearchFilter

from .models import Recipe, CustomUser, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeSearchFilter(SearchFilter):
    search_param = 'author'


class TagAndAuthorFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name="slug",
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all()
    )
    is_favorited = filters.BooleanFilter(method="get_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart"
    )
    
    def get_favorited(self, request, queryset, value):
        user=self.request.user
        print(user)
        if value:
            return Recipe.objects.filter(favorites__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(in_cart__user=user)
        return Recipe.objects.all()
    
    class Meta:
        model = Recipe
        fields = ['tags', 'author', 
                  'is_favorited', 'is_in_shopping_cart']
