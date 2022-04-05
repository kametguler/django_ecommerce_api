from django.db.models import base
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, AddToCartView, RemoveFromCartView, OrderSummaryView, CartItemView, ShippingView, doOrderView
router = DefaultRouter()
router.register('products', ItemViewSet, basename='products')
router.register('order-summary', OrderSummaryView, basename='order-summary')
router.register('cart', CartItemView, basename='cart')
router.register('addresses', ShippingView, basename='addresses')
router.register('do-order', doOrderView, basename='do-order')


urlpatterns = [
    path('', include(router.urls)),
    path('add-to-cart/<id>/',
         AddToCartView.as_view({'put': 'update'}), name='add-to-cart'),
    path('remove-from-cart/<id>/',
         RemoveFromCartView.as_view({'put': 'update'}), name='remove-from-cart'),
]
