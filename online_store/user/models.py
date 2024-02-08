from django.db import models


class User(models.Model):
    user_tg_nickname = models.CharField(max_length=255)

    def __str__(self):
        return str(self.pk)
