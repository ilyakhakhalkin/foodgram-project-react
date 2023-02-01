from django.core.exceptions import ObjectDoesNotExist
from django.db.models.constants import LOOKUP_SEP
from django_filters import rest_framework
from django_filters.conf import settings as django_filters_settings
from django_filters.filters import Filter

from recipes.models import Recipe


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )


class ListFilter(Filter):
    def __init__(self, query_param: str, *args, **kwargs):
        """
        Override default variables.
        Args:
            query_param (str): Query param in URL
        """
        super().__init__(*args, **kwargs)
        self.query_param = query_param
        self.distinct = True

    def filter(self, qs, value):
        """
        Override filter method in Filter class.
        """
        try:
            request = self.parent.request
            values = request.query_params.getlist(self.query_param)
            values = list(filter(None, values))
        except AttributeError:
            values = []

        if values and self.lookup_expr == 'in':
            return super().filter(qs, values)

        for value in set(values):
            predicate = self.get_filter_predicate(value)
            qs = self.get_method(qs)(**predicate)

        return qs.distinct() if self.distinct else qs

    def get_filter_predicate(self, value):
        """
        This function helps to get predicate for filtering
        """
        name = self.field_name

        if (
            name
            and self.lookup_expr != django_filters_settings.DEFAULT_LOOKUP_EXPR
        ):
            name = LOOKUP_SEP.join([name, self.lookup_expr])

        return {name: value}


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(
        field_name='author__id',
        lookup_expr='iexact'
    )

    tags = ListFilter(
        query_param='tags',
        field_name='tags__slug',
        lookup_expr='in',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(method='filter_by_cart')
    is_favorited = rest_framework.BooleanFilter(method='filter_by_favorites')

    class Meta:
        fields = ('id', 'tags',)
        model = Recipe

    def filter_by_cart(self, queryset, name, value):
        if value == 0 or value is None or self.request.user.is_anonymous:
            return queryset
        try:
            recipes = self.request.user.shopping_cart.all()
            return queryset.filter(pk__in=(rec.pk for rec in recipes))
        except ObjectDoesNotExist:
            return queryset

    def filter_by_favorites(self, queryset, name, value):
        if value == 0 or value is None or self.request.user.is_anonymous:
            return queryset
        try:
            recipes = self.request.user.favorites.all()
            return queryset.filter(pk__in=(rec.pk for rec in recipes))
        except ObjectDoesNotExist:
            return queryset
