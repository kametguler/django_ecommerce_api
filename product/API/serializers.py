from re import escape
from django.db.models import fields
from django.db.models.fields.related import ManyToManyField
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import ManyRelatedField, StringRelatedField
from product.models import *


class ItemSerializer(serializers.ModelSerializer):
    add_to_cart_link = serializers.ReadOnlyField(source='get_add_to_cart_url')
    remove_from_cart_link = serializers.ReadOnlyField(
        source='get_remove_from_cart_url')

    class Meta:
        model = Item
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = ReadOnlyField(source='get_total_item_price')
    total_discount_price = ReadOnlyField(source='get_discount_item_price')
    saved_price = ReadOnlyField(source='get_amount_saved')
    final_price = ReadOnlyField(source='get_final_price')

    def __init__(self, instance=None, data=None, **kwargs):
        if instance:
            setattr(self.Meta, 'depth', 1)
        else:
            setattr(self.Meta, 'depth', 0)
        super(OrderItemSerializer, self).__init__(instance, data, **kwargs)

    class Meta:
        model = OrderItem
        fields = ['ordered', 'item', 'quantity', 'total_price', 'total_discount_price', 'saved_price',
                  'final_price']


class CartFunctionality(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField(source='get_total_price')

    def __init__(self, instance=None, data=None, **kwargs):
        if instance:
            setattr(self.Meta, 'depth', 1)
        else:
            setattr(self.Meta, 'depth', 0)
        super(OrderSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Order
        fields = ['id','ordered', 'items', 'ordered',
                  'total_price', 'checkout_address','paid_price']


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping_Addresses
        fields = ['phone', 'address', 'note']