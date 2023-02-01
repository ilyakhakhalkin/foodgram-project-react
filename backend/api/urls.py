from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomAuthToken, IngredientViewSet, Logout, RecipeViewSet,
                    TagViewSet, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', Logout.as_view()),
    path('', include(router.urls)),
]
