from django_filters import rest_framework

from recipes.models import Recipe
from users.models import User


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name='username'
    )
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    is_in_shopping_cart = rest_framework.BooleanFilter(method='filter_by_cart')
    is_favorited = rest_framework.BooleanFilter(method='filter_by_favorites')

    class Meta:
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited',)
        model = Recipe

    def filter_by_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_owner=self.request.user)
        return queryset

    def filter_by_favorites(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes=self.request.user)

        return queryset
