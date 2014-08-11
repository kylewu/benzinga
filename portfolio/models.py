from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=32)

    amount = models.FloatField(default=100000.0)
