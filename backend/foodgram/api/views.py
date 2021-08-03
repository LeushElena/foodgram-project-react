from .filters import IngredientSearchFilter, TagAndAuthorFilter
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (Cart, Favorite, Ingredient, IngredientRecipe, 
                     Recipe, Subsribe, Tag, CustomUser)
from .permissions import OwnerOrReadOnly
from .serializers import (CustomUserSerializer,IngredientSerializer, 
                          RecipeMinifiedSerializer, RecipeSerializer, 
                          SubsribeSerializer, TagSerializer)


class CustomViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if user != author:
            if not Subsribe.objects.filter(user=user, author=author).exists():
                subscribe = Subsribe.objects.create(user=user, author=author)
                serializer = SubsribeSerializer(
                    subscribe, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        Subsribe.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, id=None):
        user = request.user
        subsribers = user.subsriber.all()
        page = self.paginate_queryset(subsribers)
        serializer = SubsribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
        

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_class = TagAndAuthorFilter

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user = request.user
        recipes = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user=user, recipes=recipes).exists():
            Favorite.objects.create(user=user, recipes=recipes)
            serializer = RecipeMinifiedSerializer(recipes)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not recipe.in_cart.exists():
            Cart.objects.create(user=user, recipes=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Cart.objects.filter(user=user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        cart = user.cart_set.all()
        shopping_cart_data = {}
        for item_recipe in cart:
            ingredients_from_cart = IngredientRecipe.objects.filter(
                recipe=item_recipe.recipes
            )
            for composition in ingredients_from_cart:
                name = composition.ingredient.name
                amount = composition.amount
                measurement_unit = composition.ingredient.measurement_unit
                if name in shopping_cart_data:
                    shopping_cart_data[name]['amount'] += amount
                else:
                    shopping_cart_data[name] = {
                        "amount": amount, 
                        "measurement_unit": measurement_unit
                    }
        shopping_list = ([f'{item} - {shopping_cart_data[item]["amount"]} '
                         f'{shopping_cart_data[item]["measurement_unit"]} \n' 
                         for item in shopping_cart_data])
        response = HttpResponse(shopping_list, "Content-Type: text/plain")
        response["Content-Discription"] = "attachment; filename='shopping_list.txt'"
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    

class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ['^name']
