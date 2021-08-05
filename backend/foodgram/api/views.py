from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, TagAndAuthorFilter
from .models import (Cart, Favorite, Ingredient, IngredientRecipe, 
                     Recipe, Subsribe, Tag, CustomUser)
from .permissions import OwnerOrReadOnly
from .serializers import (CreateCartSerializer, CreateFavoriteSerializer, 
                          CreateSubsribeSerializer, CustomUserSerializer, 
                          IngredientSerializer, RecipeSerializer, 
                          SubsribeSerializer, TagSerializer)


class CustomViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        data = {
            "user": request.user.id,
            "author": id,
        }
        serializer = CreateSubsribeSerializer(data=data) 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        Subsribe.objects.filter(
            user=user, author=get_object_or_404(CustomUser, id=id)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, permission_classes=(IsAuthenticated,),)
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
        data = {
            "user": request.user.id,
            "recipe": pk
        }
        serializer = CreateFavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        Favorite.objects.filter(
            user=user, recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk
        }
        serializer = CreateCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        Cart.objects.filter(
            user=user, recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        cart = user.cart_set.all()
        shopping_cart_data = {}
        for item_recipe in cart:
            ingredients_from_cart = IngredientRecipe.objects.filter(
                recipe=item_recipe.recipe
            )
            for composition in ingredients_from_cart:
                name = composition.ingredient.name
                amount = composition.amount
                measurement_unit = composition.ingredient.measurement_unit
                if name in shopping_cart_data:
                    shopping_cart_data[name]["amount"] += amount
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
    search_fields = ["^name"]
