from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField

from django.shortcuts import get_object_or_404

from djoser.serializers import UserSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from .models import (Cart, CustomUser, Favorite, Ingredient, IngredientRecipe, 
                     Recipe, Subsribe, Tag)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", 
                  "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        return obj.subscribing.exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class AddIngredientAmountSerializator(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    
    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount",)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientAmountSerializator(
        source="ingredientrecipe_set", 
        many=True, read_only=True
    )
    tags = TagSerializer(read_only=True, many=True)
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1)))
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "name", "text", "cooking_time", "image",  
                  "is_favorited", "is_in_shopping_cart")

    def validate(self, data):
        ingredients = self.initial_data.pop("ingredients")
        for ingredient_model in ingredients:
            amount = ingredient_model.get("amount")
            if int(amount) < 1:
                raise ValidationError("Количество не может быть меньше 1!")
        data["ingredients"] = ingredients
        return data
    
    def create(self, validated_data):
        image = validated_data.pop("image")
        ingredients = validated_data.pop("ingredients")
        tags_data = self.initial_data.pop("tags")
        recipe = Recipe.objects.create(
            author=get_object_or_404(
                CustomUser, id=validated_data.pop("author").id),
                image=image, **validated_data
        )
        for tag_ in tags_data:
            recipe.tags.add(get_object_or_404(Tag, id=tag_))
        for ingredient_model in ingredients:
            amount = ingredient_model.pop("amount")
            current_ingredient = get_object_or_404(Ingredient, 
                id=ingredient_model.pop("id")
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = (
            validated_data.get("cooking_time", instance.cooking_time)
        )
        instance.image = validated_data.get("image", instance.image)
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags_data = self.initial_data.pop("tags")
        for tag_ in tags_data:
            instance.tags.add(get_object_or_404(Tag, id=tag_))
        ingredients = validated_data.pop("ingredients")
        for ingredient_model in ingredients:
            amount = ingredient_model.pop("amount")
            current_ingredient = get_object_or_404(Ingredient,
                id=ingredient_model.pop("id")
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=instance, amount=amount
            )
        instance.save()
        return instance
    
    def get_is_favorited(self, obj):
        return obj.favorites.exists()
    
    def get_is_in_shopping_cart(self, obj):
        return obj.in_cart.exists()


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
 
    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")
        read_only_fields = ("id", "name", "cooking_time", "image")


class CreateFavoriteSerializer(serializers.ModelSerializer):
    queryset = Recipe.objects.all()

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message=("Вы уже добавили этот рецепт в избранное!")
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={"request": request}).data


class SubsribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subsribe
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed","recipes", "recipes_count",)
        
    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = obj.author.recipe_set.all().order_by("-id")
        if limit:
            obj.author.recipe_set.all().order_by("-id")[:int(limit)]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipe_set.count()

    def get_is_subscribed(self, obj):
        return obj.author.subscribing.exists()


class ShowSubsribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed","recipes", "recipes_count",)
        
    def get_recipes(self, obj):
        limit = self.context.get("recipes_limit")
        queryset = obj.recipe_set.all().order_by("-id")
        if limit:
            obj.recipe_set.all().order_by("-id")[:limit]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe_set.count()

    def get_is_subscribed(self, obj):
        return obj.subscribing.exists()


class CreateSubsribeSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()
    
    class Meta:
        model = Subsribe
        fields = ("user", "author")
        validators = [
            UniqueTogetherValidator(
                queryset=Subsribe.objects.all(),
                fields=("user", "author"),
                message=("Вы уже подписаны на этого автора!")
            )
        ]
    
    def validate(self, data):
        user = data.get("user")
        author = data.get("author")
        if user == author:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return ShowSubsribeSerializer(
            instance.author,
            context={"request": request}).data


class CreateCartSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()
    
    class Meta:
        model = Cart
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=("user", "recipe"),
                message=("Вы уже добавили этот рецепт в корзину!")
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={"request": request}).data
