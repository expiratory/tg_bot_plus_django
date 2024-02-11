from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_tg_nickname', 'balance',)
    search_fields = ('user_tg_nickname',)
    ordering = ('id',)
