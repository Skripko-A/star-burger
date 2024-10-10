from django.db import models


class GeoPoint(models.Model):
    address = models.CharField(
        max_length=50, 
        unique=True
        )
    lng = models.DecimalField(
        max_digits=18,
        decimal_places=14,
        verbose_name='Долгота',
        null=True
        )
    lat = models.DecimalField(
        max_digits=18,
        decimal_places=14,
        verbose_name='Широта',
        null=True
        )
    created_at = models.DateField(
        auto_now_add=True
        )
    updated_at = models.DateField(
        auto_now=True,
        blank=True,
        null=True
        ) 
