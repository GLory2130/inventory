from django.contrib import admin
from .models import CustomUser, Product, ProductConsumption

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(ProductConsumption)