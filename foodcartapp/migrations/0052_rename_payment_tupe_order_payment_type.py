# Generated by Django 5.1 on 2024-09-07 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_order_payment_tupe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='payment_tupe',
            new_name='payment_type',
        ),
    ]
