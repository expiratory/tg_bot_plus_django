from django.db import models


class User(models.Model):
    user_tg_nickname = models.CharField(max_length=255)
    balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.user_tg_nickname)
