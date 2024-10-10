from django.contrib import admin
from .models import GeoPoint


@admin.register(GeoPoint)
class GeoPointAdmin(admin.ModelAdmin):
    list_display = (
        'address', 
        'updated_at'
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )