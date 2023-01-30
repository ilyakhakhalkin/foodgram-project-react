from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet
from .views import TagViewSet
from .views import IngredientViewSet
from .views import RecipeViewSet
from .views import CustomAuthToken
from .views import Logout


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', Logout.as_view()),
    path('', include(router.urls)),
]
