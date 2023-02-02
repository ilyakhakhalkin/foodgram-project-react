import base64

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            RecipeUserFavorites, Tag)
from users.models import ShoppingCart, Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
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
        user = getattr(self.context.get('request'), 'user', None)
        return Subscription.objects.filter(
            follower=getattr(user, 'id', None),
            following=getattr(obj, 'id', None)
        ).exists()


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
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        model = Recipe

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('author')
        return queryset.prefetch_related('tags', 'ingredients')

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )

    def get_favorites(self, obj):
        return is_in_database(self.context, RecipeUserFavorites, obj)

    def get_cart(self, obj):
        return is_in_database(self.context, ShoppingCart, obj)

    def get_tags_and_ingredients(self):
        tag_id_list = set(self.initial_data.get('tags', []))
        tags_queryset = Tag.objects.filter(pk__in=tag_id_list)

        ing_data = self.initial_data.get('ingredients', [])
        filtered_data = {el.get('id'): el.get('amount', 1) for el in ing_data}

        ingredients_queryset = Ingredient.objects.filter(
            pk__in=filtered_data.keys()
        )
        ingredients = []
        for ingredient in ingredients_queryset:
            ingredients.append({
                'ingredient': ingredient,
                'amount': filtered_data[ingredient.id]
            })

        return [tag for tag in tags_queryset], ingredients

    def validate(self, data):
        tags, ingredients = self.get_tags_and_ingredients()
        if len(tags) == 0:
            raise ValidationError('Теги не указаны или не найдены')
        if len(tags) < len(self.initial_data.get('tags')):
            raise ValidationError('Неверный формат тегов')
        if len(ingredients) == 0:
            raise ValidationError('Ингридиенты не указаны или не найдены')
        if len(ingredients) < len(self.initial_data.get('ingredients')):
            raise ValidationError('Неверный формат ингредиентов')

        data['tags'] = tags
        data['ingredients'] = ingredients
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
                ('Неправильный пароль')
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


def is_in_database(context, model, obj):
    user = getattr(context.get('request'), 'user', None)
    return model.objects.filter(
        user=getattr(user, 'id', None),
        recipe=getattr(obj, 'id', None)
    ).exists()
