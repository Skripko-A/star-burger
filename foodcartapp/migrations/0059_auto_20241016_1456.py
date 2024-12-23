# Generated by Django 5.1 on 2024-10-16 14:56

from django.db import migrations


def replace_none_string_fields(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    Order.objects.filter(comment=None).update(comment='')

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_rename_restraunt_order_restaurant'),
    ]

    operations = [
        migrations.RunPython(replace_none_string_fields)
    ]
