from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            RecipeUserFavorites, Tag)
from users.models import ShoppingCart, Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .paginators import (CustomPageNumberPagination,
                         CustomRecipesLimitPagination)
from .permissions import ReadOrAuthorOrAdmin
from .serializers import (IngredientSerializer, PasswordChangeSerializer,
                          RecipeSerializer, RecipeShortInfo,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (ReadOrAuthorOrAdmin,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return self.get_serializer_class().setup_eager_loading(queryset)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        serializer_class=RecipeShortInfo
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            return self.add_favorite(request.user, recipe)

        return self.delete_favorite(request.user, recipe)

    def add_favorite(self, user, recipe) -> Response:
        """
        Добавление рецепта в избранное.
        """
        fav_recipe = RecipeUserFavorites.objects.filter(
            user=user,
            recipe=recipe
        )
        if fav_recipe.exists():
            return Response(
                data={'errors': 'Рецепт уже есть в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeShortInfo(recipe)
        RecipeUserFavorites.objects.create(user=user, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, user, recipe):
        """
        Удаление рецепта из избранного.
        """
        fav_recipe = RecipeUserFavorites.objects.filter(
            user=user,
            recipe=recipe
        )
        if fav_recipe.exists():
            fav_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data={'errors': 'Этого рецепта нет в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        serializer_class=RecipeShortInfo,
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            return self.add_to_cart(request.user, recipe)

        return self.delete_from_cart(request.user, recipe)

    def add_to_cart(self, user, recipe):
        """
        Добавление рецепта в список покупок.
        """
        serializer = RecipeShortInfo(recipe)
        cart_recipe = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if cart_recipe.exists():
            return Response(
                data={'errors': 'Рецепт уже есть в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_cart(self, user, recipe):
        """
        Удаление рецепта из списка покупок.
        """
        cart_recipe = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if cart_recipe.exists():
            cart_recipe.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            data={'errors': 'Этого рецепта нет в корзине'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in=(request.user.shopping_cart.values('id'))
            ).values(
                name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            ).annotate(amount=Sum('amount'))
        )

        content = ''
        for ing in ingredients:
            content += (
                f'{ing["name"]}'
                f' - {ing["amount"]}'
                f' {ing["unit"]}\r\n'
            )

        response = HttpResponse(content,
                                content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = 'attachment; filename=cart.txt'
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        if pk == 'me':
            if not request.user.is_anonymous:
                return Response(self.serializer_class(request.user).data)
            raise AuthenticationFailed('Учетные данные не были предоставлены.')
        return super().retrieve(request, request, pk)

    @action(
        detail=False, methods=['post'],
        serializer_class=PasswordChangeSerializer,
    )
    def set_password(self, request):
        if request.user.is_anonymous:
            raise AuthenticationFailed('Учетные данные не были предоставлены.')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, pagination_class=CustomRecipesLimitPagination)
    def subscriptions(self, request):
        following = Subscription.objects.filter(follower=request.user)
        queryset = User.objects.filter(following__in=following)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_subscribtion_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_subscribtion_serializer(self, *args, **kwargs):
        kwargs.setdefault(
            'context',
            self.get_serializer_context()
        )
        return SubscriptionSerializer(*args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        if request.user.is_anonymous:
            return Response(
                data={'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        to_follow = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            return self.create_subscription(follower=request.user,
                                            following=to_follow)

        return self.delete_subscription(follower=request.user,
                                        following=to_follow)

    def create_subscription(self, follower, following):
        sub = Subscription.objects.filter(follower=follower,
                                          following=following)
        if sub.exists():
            return Response(
                data={'errors': 'Нельзя подписаться дважды'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(follower=follower,
                                    following=following)
        serializer = self.get_subscribtion_serializer(following)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_subscription(self, follower, following):
        sub = Subscription.objects.filter(follower=follower,
                                          following=following)
        if sub.exists():
            sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data={'errors': 'Вы не подписаны на этого автора'},
                        status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, email=request.data['email'])
        request.data['username'] = user.username
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key})


class Logout(views.APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
