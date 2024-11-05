# Generated by Django 5.1 on 2024-10-30 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_auto_20241016_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurants',
            field=models.JSONField(blank=True, default=list, verbose_name='Рестораны'),
        ),
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий к заказу'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания заказа'),
        ),
    ]