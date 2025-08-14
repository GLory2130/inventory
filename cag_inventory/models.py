from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomUser(AbstractUser):
    approved = models.BooleanField(default=False)

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    currentStock = models.IntegerField()
    minStock = models.IntegerField()
    maxStock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    lastUpdated = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class ProductConsumption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    consumed_at = models.DateTimeField(default=timezone.now)
    # consumed_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
