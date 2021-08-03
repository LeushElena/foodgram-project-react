#from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers

from djoser.serializers import UserSerializer

from .models import (CustomUser, Ingredient, IngredientRecipe, 
                     Recipe, Subsribe, Tag)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 
                  'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, obj):
        return obj.subscribing.exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class AddIngredientAmountSerializator(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    #image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientAmountSerializator(
        source='ingredientrecipe_set', 
        many=True, read_only=True
    )
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'title', 'text', 'image', 'cooking_time', 
                  'is_favorited', 'is_in_shopping_cart')

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = self.initial_data.pop("ingredients")
        tags_data = self.initial_data.pop("tags")
        recipe = Recipe.objects.create(author=CustomUser.objects.get(
            id=validated_data.pop('author').id), image=image, 
            **validated_data
        )
        for tag_ in tags_data:
            recipe.tags.add(Tag.objects.get(id=tag_))
        for ingredient_model in ingredients:
            amount = ingredient_model.pop("amount")
            current_ingredient = Ingredient.objects.get(
                id=ingredient_model.pop("id")
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get("cooking_time", instance.cooking_time)
        instance.image = validated_data.get("image", instance.image)
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags_data = self.initial_data.pop("tags")
        for tag_ in tags_data:
            instance.tags.add(Tag.objects.get(id=tag_))
        ingredients = self.initial_data.pop("ingredients")
        for ingredient_model in ingredients:
            amount = ingredient_model.pop("amount")
            current_ingredient = Ingredient.objects.get(
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
    #image = Base64ImageField()
 
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'cooking_time', 'image')
        read_only_fields = ('id', 'title', 'cooking_time', 'image')


class SubsribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subsribe
        fields = ('email','id', 'username', 'first_name', 'last_name',
                  'is_subscribed','recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipe_set.all().order_by("-id")
        if limit:
            obj.author.recipe_set.all().order_by("-id")[:limit]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return len(obj.author.recipe_set.all())

    def get_is_subscribed(self, obj):
        return obj.author.subscribing.exists()
