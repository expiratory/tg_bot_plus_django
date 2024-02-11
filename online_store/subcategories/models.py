from django.db import models

from categories.models import Category


class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_category_name(self):
        return self.category.name
