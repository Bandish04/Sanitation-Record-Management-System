from django.db import models


class Plant(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"