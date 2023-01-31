from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from django.db.models import F
import base64

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeUserFavorites,
    RecipeIngredient,
)
from users.models import (
    User,
    Subscription,
    ShoppingCart,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_subs')
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super(UserSerializer, self).create(validated_data)

    def get_subs(self, obj):
        request = self.context.get('request', None)
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(
                    follower=request.user,
                    following=obj.id
                ).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_favorites')
    is_in_shopping_cart = serializers.SerializerMethodField('get_cart')
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = Recipe

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('author')
        queryset = queryset.prefetch_related('tags', 'ingredients')

        return queryset

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )

    def get_favorites(self, obj):
        request = self.context.get('request', None)
        if request and not request.user.is_anonymous:
            return RecipeUserFavorites.objects.filter(
                    user=request.user,
                    recipe=obj.id
                ).exists()
        return False

    def get_cart(self, obj):
        request = self.context.get('request', None)
        if request and not request.user.is_anonymous:
            return ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=obj.id
                ).exists()
        return False

    def validate(self, data):
        tag_id_list = self.initial_data.get('tags')
        if tag_id_list is None:
            raise ValidationError({'tags': 'Не указаны теги'})

        tags = []
        for tag in tag_id_list:
            if not isinstance(tag, int):
                raise ValidationError({'tags': f'{tag} - неверный формат'})
            tag_obj = Tag.objects.filter(pk=tag)
            if not tag_obj.exists():
                raise ValidationError({'tags': f'Тег {tag} не найден'})
            tags.append(tag_obj)

        tags = Tag.objects.filter(pk__in=tag_id_list)
        data['tags'] = tags

        ingredient_list = self.initial_data.get('ingredients')
        found_ingredients = []
        for ingredient in ingredient_list:
            if not isinstance(ingredient['id'], int):
                raise ValidationError(
                    {'ingredients': f'{ingredient["id"]} - неверный формат id'}
                )
            # if not isinstance(ingredient['amount'], int):
            #     raise ValidationError(
            #         {'ingredients':
            #             f'{ingredient["amount"]} - неверный формат amount'}
            #     )
            ingredient_obj = Ingredient.objects.filter(pk=ingredient['id'])
            if not ingredient_obj.exists():
                raise ValidationError(
                    {'ingredients': f'id = {ingredient["id"]} не найден'}
                )
            found_ingredients.append(
                {'ingredient': ingredient_obj.first(),
                 'amount': ingredient['amount']}
            )

        data['ingredients'] = found_ingredients
        return super().validate(data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)

        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )

        return super().update(instance, validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Неправильный пароль')
            )
        return value

    def validate(self, data):
        password_validation.validate_password(data['new_password'],
                                              self.context['request'].user
                                              )
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class SubscriptionSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeShortInfo(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
