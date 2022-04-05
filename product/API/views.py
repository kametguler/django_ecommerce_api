from re import T
from typing import Generic, List
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import datastructures
from django.utils.functional import empty
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from product.API.permissions import IsAdminUserOrReadOnly, CartOwnerOrNotAccess, CheckoutFor
from .serializers import OrderItemSerializer, OrderSerializer, ItemSerializer, CartFunctionality, ShippingSerializer
from product.models import *
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import permissions, request, serializers, status
from django.core.mail import send_mail

class ItemViewSet(ModelViewSet):
    lookup_field = 'slug'
    serializer_class = ItemSerializer
    queryset = Item.objects.filter(stock__gt=0)
    permission_classes = [IsAdminUserOrReadOnly]


class AddToCartView(GenericViewSet, UpdateModelMixin):
    serializer_class = CartFunctionality
    queryset = OrderItem.objects.all()
    permission_classes = [CartOwnerOrNotAccess]

    def update(self, request, *args, **kwargs):
        pk = kwargs['id']
        item = get_object_or_404(Item, pk=pk)
        order_item, created = self.queryset.get_or_create(
            item=item,
            customer=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]

            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity += 1
                order_item.save()
            else:
                order.items.add(order_item)
        else:
            order = Order.objects.create(customer=request.user)
            order.items.add(order_item)
        return Response({'message': 'Ürün başarıyla sepete eklendi.'}, status=status.HTTP_200_OK)


class RemoveFromCartView(GenericViewSet, UpdateModelMixin):
    serializer_class = CartFunctionality
    queryset = OrderItem.objects.all()
    permission_classes = [CartOwnerOrNotAccess]

    def update(self, request, *args, **kwargs):
        pk = kwargs['id']
        item = get_object_or_404(Item, pk=pk)

        order_item, created = self.queryset.get_or_create(
            item=item,
            customer=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]

            if order.items.filter(item__pk=item.pk).exists():
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    message = 'Ürün adeti başarıyla azaltıldı.'
                else:
                    order_item.delete()
                    message = 'Ürün başarıyla sepetten kaldırıldı'
        return Response({'message': message}, status=status.HTTP_200_OK)


class OrderSummaryView(GenericViewSet, ListModelMixin):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [CartOwnerOrNotAccess]

    def list(self, request, *args, **kwargs):
        order = self.queryset.filter(customer=request.user, ordered=False)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class CartItemView(GenericViewSet, ListModelMixin):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = [permissions.IsAuthenticated, CartOwnerOrNotAccess]

    def list(self, request, *args, **kwargs):
        user = request.user
        qs = self.queryset.filter(customer=user, ordered=False)
        serializer = OrderItemSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ShippingView(ModelViewSet):
    queryset = Shipping_Addresses.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [CartOwnerOrNotAccess]


class doOrderView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer  
    permission_classes = [CartOwnerOrNotAccess]  
    
    def update(self, request, *args, **kwargs):
        customer = request.user
        instance = self.get_object()
        data = request.data
        user_instance = User.objects.get(username=customer)
        if instance.ordered == True:
            
            return Response({'message':'Its already ordered'})

        else:
            
            if data.get('name') is not None:
                user_instance.first_name=data.get('name') 
                user_instance.last_name=data.get('surname')
                user_instance.save()
            
            adress = Shipping_Addresses(
                    customer = customer,
                    phone = data.get('phone'),
                    address = data.get('address'),
                    note = data.get('note')
                )
            adress.save()
            adres = Shipping_Addresses.objects.last()
            items = OrderItem.objects.filter(customer=customer)
            itemler = []
            for item in items:
                item.ordered = True
                itemler.append(item)
                item.save()
                product = Item.objects.filter(id=item.item_id)
                    
                for pro in product:
                        
                    pro.stock -= item.quantity
                    pro.save()
                    
            instance.paid_price = data.get('paid_price')
            instance.ordered = True
            instance.checkout_address = adres
            instance.save()
            serializer = self.get_serializer(instance)
                
            send_mail('Kamet Moda - Siparişiniz Hakkında',
            'Siparişiniz Başarılı bir şekilde oluşturulmuştur.',
            'Kamet Moda',
            [customer.email],
            fail_silently=False,
            )
    
            return Response(serializer.data)        
                
                
            
           
        
        
