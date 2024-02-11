from django.contrib import admin

from .models import Good


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'get_category_name', 'get_subcategory_name')
    search_fields = ('name', 'category__name', 'subcategory__name',)
    ordering = ('id',)
