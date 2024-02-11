from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question',)
    search_fields = ('question',)
    ordering = ('id',)
