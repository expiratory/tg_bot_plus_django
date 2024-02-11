from django.contrib import admin

from django.http import HttpResponse

from openpyxl import Workbook

from .models import Order, OrderItem


def export_orders_to_xlsx(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['Order ID', 'User', 'Created At', 'Post Data', 'Order Item ID', 'Good', 'Quantity'])

    for order in queryset:
        for order_item in order.orderitem_set.all():
            worksheet.append([order.id, order.user.user_tg_nickname, order.created_at.strftime('%Y-%m-%d %H:%M:%S'), order.post_data, order_item.id, order_item.good.name, order_item.quantity])

    workbook.save(response)
    return response


export_orders_to_xlsx.short_description = "Export selected orders to XLSX"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_tg_nickname', 'created_at', 'post_data',)
    search_fields = ('user__user_tg_nickname',)
    ordering = ('-created_at',)
    actions = [export_orders_to_xlsx]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_tg_nickname', 'get_good_name',)
    search_fields = ('order__user__user_tg_nickname', 'good__name',)
    ordering = ('id',)
