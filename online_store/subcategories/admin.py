from django.contrib import admin

from .models import Subcategory


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_category_name')
    search_fields = ('name', 'category__name',)
    ordering = ('id',)
