from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField("E-mail", max_length=254, unique=True)
    username = models.CharField("Никнейм", max_length=150)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name"
    ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=100) 
    measurement_unit = models.CharField(verbose_name="Количество", 
                                        max_length=40)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(models.Model):
    name = models.CharField(max_length=30, 
                            verbose_name="Название")
    color = models.CharField(max_length=30, verbose_name="Цветовой HEX-код")
    slug = models.SlugField(verbose_name="Ссылка", unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.slug}"


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                               verbose_name="Автор публикации")
    name = models.CharField(max_length=100, verbose_name="Название")
    image = models.ImageField(upload_to="media/recipes/",
                              blank=True, null=True,
                              verbose_name="Картинка")
    text = models.CharField(max_length=3000, 
                            verbose_name="Текстовое описание")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=[validators.MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe",
        verbose_name="Ингредиенты"
    )
    tags = models.ManyToManyField(Tag, through="TagRecipe", 
                                  verbose_name="Теги")
    
    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
    
    def __str__(self):
        return f"{self.name}"


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, 
                               verbose_name='Рецепт')
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE, 
                             verbose_name="Теги")

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецепта"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, 
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", 
        validators=[validators.MinValueValidator(1)])

    class Meta:
        verbose_name = "Ингридиент и его количество в рецепте"
        verbose_name_plural = "Ингридиенты и их количество в рецептах"

    def __str__(self):
        return f"{self.recipe}, {self.ingredient.id}, {self.amount}"


class Subsribe(models.Model): 
    user = models.ForeignKey(CustomUser,  
                             on_delete=models.CASCADE,  
                             related_name="subsriber",
                             verbose_name="Пользователь")
    author = models.ForeignKey(CustomUser,  
                               on_delete=models.CASCADE,  
                               related_name="subscribing",
                               verbose_name="Автор публикации")
    
    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=["user", "author"], 
                                    name="unique_subsribe")]
    
    def __str__(self):
        return f"{self.user} - {self.author}"


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                             verbose_name="Пользователь")
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE, 
                               related_name="favorites", 
                               verbose_name='Рецепт')
    
    class Meta:
        ordering = ["-id"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], 
                                    name="unique_favorite")]
    
    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                             verbose_name="Пользователь")
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE, 
                               related_name="in_cart", 
                               verbose_name='Рецепт')
    
    class Meta:
        ordering = ["-id"]
        verbose_name = "Корзина"
        verbose_name_plural = "В корзине"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], 
                                    name="unique_cart")]
    
    def __str__(self):
        return f"{self.user} - {self.recipe}"
