from django.contrib import admin
from .models import Item, Order, OrderItem, Shipping_Addresses
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipping_Addresses)
