
from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.name
