from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    RecipeTag,
    Ingredient,
    RecipeIngredient,
    RecipeUserFavorites,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'colored_name')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeTagTabular(admin.TabularInline):
    model = RecipeTag


class RecipeIngredientTabular(admin.TabularInline):
    model = RecipeIngredient


@admin.register(RecipeIngredient)
class RecipeIngredient(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'name',
                    'author',
                    'text',
                    'cooking_time',
                    'get_tags',
                    'get_ingredients',
                    'get_favorited_count',
                    )
    search_fields = ('name',
                     'author__username',
                     'author__first_name',
                     'author__last_name',
                     'recipetag__tag__name',
                     )

    inlines = [RecipeTagTabular, RecipeIngredientTabular]

    def get_tags(self, obj):
        return ",\n".join([tag.name for tag in obj.tags.all()])

    def get_ingredients(self, obj):
        return ",\n".join([ing.name for ing in obj.ingredients.all()])

    def get_favorited_count(self, obj):
        return obj.favorited_count

    get_tags.short_description = 'Теги'
    get_ingredients.short_description = 'Ингредиенты'
    get_favorited_count.short_description = 'В избранном'


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'tag',)


@admin.register(RecipeUserFavorites)
class RecipeUserFavorites(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
