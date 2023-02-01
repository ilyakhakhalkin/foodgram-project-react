# Generated by Django 3.2.16 on 2023-01-31 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230131_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ing_amount', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]