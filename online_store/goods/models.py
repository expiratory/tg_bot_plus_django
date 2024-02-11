from django.db import models

from categories.models import Category
from subcategories.models import Subcategory


class Good(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField()
    price = models.IntegerField()
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_category_name(self):
        return self.category.name

    def get_subcategory_name(self):
        return self.subcategory.name
