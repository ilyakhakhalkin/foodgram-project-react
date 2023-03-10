# Generated by Django 3.2.16 on 2023-02-01 14:47

import recipes.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230201_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.validators.validate_cooking_time], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, validators=[recipes.validators.validate_amount], verbose_name='Количество'),
        ),
    ]
