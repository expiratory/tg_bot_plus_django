from django.db import models

from user.models import User
from goods.models import Good


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Good, through='CartGood')

    def __str__(self):
        return str(self.pk)


class CartGood(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.pk)
