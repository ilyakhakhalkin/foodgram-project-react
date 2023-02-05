from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomRecipesLimitPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'
