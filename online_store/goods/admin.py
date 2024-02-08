from django.contrib import admin

from .models import Good


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    pass
