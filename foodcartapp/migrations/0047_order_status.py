# Generated by Django 5.1 on 2024-09-07 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_alter_orderproduct_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('M', 'Менеджер'), ('P', 'Сборщик'), ('C', 'Курьер'), ('A', 'Архив')], db_index=True, default='M', max_length=2, verbose_name='Статус'),
        ),
    ]
