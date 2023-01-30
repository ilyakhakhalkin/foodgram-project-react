from django.db import models
from django.utils.html import format_html

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('Адрес', max_length=30)
    color = models.CharField('Цвет', max_length=7, default='#ffffff')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def colored_name(self):
        return format_html(
            '''<span style="background-color: {}">
                <span style="background: inherit;
                            background-clip: text;
                            -webkit-background-clip: text;
                            color: transparent;
                            filter: invert(1) grayscale(1);
                            -webkit-filter: invert(1) grayscale(1);">{}</span>
            </span>''',
            self.color, self.color,
        )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=70,)
    measurement_unit = models.CharField('Единица измерения', max_length=10,)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Пользователь',
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               )
    name = models.CharField('Название', max_length=200,)
    text = models.TextField('Описание',)
    image = models.ImageField('Изоюражение',
                              upload_to='recipe_images',
                              blank=True,
                              )
    cooking_time = models.IntegerField('Время приготовления (в минутах)')

    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Теги',
        through='RecipeTag',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pk',)

    def __str__(self) -> str:
        return self.name

    @property
    def favorited_count(self):
        return RecipeUserFavorites.objects.filter(recipe=self).count()


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               )
    tag = models.ForeignKey(Tag,
                            verbose_name='Тег',
                            on_delete=models.CASCADE,
                            )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='unique_recipe-tag')
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   )
    amount = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe-ingredient')
        ]


class RecipeUserFavorites(models.Model):
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               )
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='unique_recipe-user-favorites')
        ]
