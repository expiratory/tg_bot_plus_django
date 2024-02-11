from django.contrib import admin

from .models import Cart, CartGood


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_tg_nickname',)
    search_fields = ('user__user_tg_nickname', )
    ordering = ('id',)


@admin.register(CartGood)
class CartGoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_tg_nickname', 'get_good_name', 'get_quantity')
    search_fields = ('cart__user__user_tg_nickname',)
    ordering = ('id',)
