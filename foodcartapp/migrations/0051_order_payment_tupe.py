# Generated by Django 5.1 on 2024-09-07 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_rename_delivered_at_order_delivered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_tupe',
            field=models.CharField(choices=[('O', 'Онлайн'), ('T', 'Картой курьеру'), ('C', 'Наличными курьеру')], db_index=True, default='C', max_length=2, verbose_name='Способ оплаты'),
            preserve_default=False,
        ),
    ]