# Generated by Django 3.2.5 on 2021-08-03 16:01

import api.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20210803_1015'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='subsribe',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[api.validators.amount_validator], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[api.validators.cooking_time_validator], verbose_name='Время приготовления'),
        ),
    ]