from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        related_name='favorite_recipes',
        verbose_name='Избранное',
        through='recipes.RecipeUserFavorites',
    )

    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Список покупок',
        related_name='cart_owner',
        through='ShoppingCart',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_superuser


class Subscription(models.Model):
    follower = models.ForeignKey(User,
                                 verbose_name='Подписчик',
                                 on_delete=models.CASCADE,
                                 related_name='followers',
                                 )
    following = models.ForeignKey(User,
                                  verbose_name='Автор',
                                  on_delete=models.CASCADE,
                                  related_name='following'
                                  )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self) -> None:
        if self.follower == self.following:
            raise ValidationError('Нельзя подписаться на себя')

        if Subscription.objects.filter(follower=self.follower,
                                       following=self.following
                                       ).exists():
            raise ValidationError('Нельзя подписаться дважды')

        return super().clean()


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             )
    recipe = models.ForeignKey('recipes.Recipe',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def clean(self) -> None:
        if ShoppingCart.objects.filter(user=self.user,
                                       recipe=self.recipe).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')
