from django_filters.rest_framework import FilterSet, filters

from rest_framework.filters import SearchFilter

from .models import Recipe, CustomUser, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = "name"


class RecipeSearchFilter(SearchFilter):
    search_param = "author"


class TagAndAuthorFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name="tagrecipe__tags__slug")
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all()
    )
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart"
    )
   
    def get_is_favorited(self, queryset, name, value):
        user=self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(in_cart__user=user)
        return queryset
    
    class Meta:
        model = Recipe
        fields = ("tags", "author", 
                  "is_favorited", "is_in_shopping_cart")
