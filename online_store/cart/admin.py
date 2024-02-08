from django.contrib import admin

from .models import Cart, CartGood

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(CartGood)
class CartGoodAdmin(admin.ModelAdmin):
    pass
