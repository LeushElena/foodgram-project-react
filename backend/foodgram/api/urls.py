from django.urls import include, path

from rest_framework import routers

from .views import CustomViewSet,IngredientViewSet, RecipeViewSet, TagViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register("users", CustomViewSet)
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
]
