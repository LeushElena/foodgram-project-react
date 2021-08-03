
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager
from .validators import amount_validator, cooking_time_validator


class CustomUser(AbstractUser):
    email = models.EmailField('E-mail', max_length=254, unique=True)
    username = models.CharField('Никнейм', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    name = models.CharField(max_length=100)  
    measurement_unit = models.CharField(max_length=40)


class Tag(models.Model):
    name = models.CharField(max_length=30, 
                            verbose_name="Название тега")
    color = models.CharField(max_length=30, verbose_name="Цвет")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.slug}"


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="media/recipes/",
                              blank=True, null=True)
    text = models.CharField(max_length=3000)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[cooking_time_validator]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    
    class Meta:
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.title}"


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name="Количество", 
                                              validators=[amount_validator])

    def __str__(self):
        return f"{self.recipe}, {self.ingredient.id}, {self.amount}"


class Subsribe(models.Model): 
    user = models.ForeignKey(CustomUser,  
                             on_delete=models.CASCADE,  
                             related_name="subsriber")
    author = models.ForeignKey(CustomUser,  
                               on_delete=models.CASCADE,  
                               related_name="subscribing")
    
    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], 
                                    name='unique_subsribe')]
    
    def __str__(self):
        return f"{self.user} - {self.author}"


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipe, 
                                on_delete=models.CASCADE, 
                                related_name="favorites")
    
    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipes'], 
                                    name='unique_favorite')]
    
    def __str__(self):
        return f"{self.user} - {self.recipes}"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipe, 
                                on_delete=models.CASCADE, 
                                related_name="in_cart")
    
    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipes'], 
                                    name='unique_cart')]
    
    def __str__(self):
        return f"{self.user} - {self.recipes}"
