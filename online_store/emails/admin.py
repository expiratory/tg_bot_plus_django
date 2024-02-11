from django.contrib import admin

from .models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'admin_email', 'created_at')
    search_fields = ('type', 'admin_email',)
    ordering = ('-created_at',)
