# Generated by Django 5.1 on 2024-09-11 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('M', 'Менеджер'), ('P', 'Сборщик'), ('C', 'Курьер'), ('A', 'Архив')], db_index=True, default='M', max_length=2, null=True, verbose_name='Статус'),
        ),
    ]
