from django.db import models

from orders.models import Order


class Email(models.Model):
    type = models.CharField(max_length=100, default='')
    title = models.TextField(default='')
    content = models.TextField(default='')
    admin_email = models.CharField(max_length=100, default='')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type
