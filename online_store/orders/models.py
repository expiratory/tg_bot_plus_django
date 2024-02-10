from django.db import models

from user.models import User
from goods.models import Good


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    post_data = models.TextField(default='')

    def __str__(self):
        return str(self.pk)

    @staticmethod
    def get_qs_as_dict():
        qs = Order.objects.select_related('user').prefetch_related('orderitem_set__good')

        orders_dict = {}

        for order in qs:
            order_dict = {}
            order_dict["Order ID"] = order.id
            order_dict["User"] = order.user.user_tg_nickname
            order_dict["Created At"] = order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            order_dict["Post Data"] = order.post_data
            for order_item in order.orderitem_set.all():
                order_item_dict = {}
                order_item_dict["Order Item ID"] = order_item.id
                order_item_dict["Good"] = order_item.good.name
                order_item_dict["Quantity"] = order_item.quantity
                order_dict[order_item.id] = order_item_dict
            orders_dict[order.id] = order_dict

        return orders_dict


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.pk)
