# Generated by Django 3.2.16 on 2023-02-04 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230201_1447'),
        ('users', '0005_subscription_нельзя подписаться дважды'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(related_name='cart_owner', through='users.ShoppingCart', to='recipes.Recipe', verbose_name='Список покупок'),
        ),
    ]
