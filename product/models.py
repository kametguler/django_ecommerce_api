from re import T
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.contrib.auth.models import User

CATEGORY = (
    ('S', 'Shirt'),
    ('SP', 'Sport Wear'),
    ('OW', 'Out Wear')
)

LABEL = (
    ('N', 'New'), 
    ('BS', 'Best Seller')
)


class Item(models.Model):
    item_name = models.CharField(max_length=100, verbose_name='Ürün Adı')
    price = models.FloatField(verbose_name='Fiyatı')
    slug = models.SlugField(unique=True)
    discount_price = models.FloatField(
        blank=True, null=True, verbose_name='İndirimli Fiyatı')
    category = models.CharField(
        choices=CATEGORY, max_length=2, verbose_name='Kategorisi')
    label = models.CharField(
        choices=LABEL, max_length=2, verbose_name='Etiketi')
    description = models.TextField(verbose_name='Ürün Açıklaması')
    stock = models.IntegerField()

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse('items', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            "id": self.id
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            "id": self.id
        })


class OrderItem(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE, verbose_name='Müşteri')
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name='Ürün')
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Sipariş Ürünü'
        verbose_name_plural = 'Sipariş Ürünleri'

    def __str__(self):
        return f"{self.quantity} adet {self.item.item_name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_discount_item_price(self):
        if self.item.discount_price:
            if self.item.price > self.item.discount_price:
                return self.quantity * self.item.discount_price
            else:
                return self.get_total_item_price()
        else:
            return 0

    def get_amount_saved(self):
        if self.get_discount_item_price() != 'İndirimli Fiyat Normal Fiyattan Fazla!':
            return self.get_total_item_price() - self.get_discount_item_price()
        else:
            return 0

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    checkout_address = models.ForeignKey(
        'Shipping_Addresses', on_delete=models.SET_NULL, blank=True, null=True)
    paid_price = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sepet'
        verbose_name_plural = 'Sepet'
        ordering = ['-ordered_date']

    def __str__(self):
        return self.customer.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class Shipping_Addresses(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE, verbose_name='Müşteri')
    phone = models.CharField(max_length=20, verbose_name='Telefon Numarası')
    address = models.TextField(verbose_name='Açık Adres')
    note = models.TextField(verbose_name='Sipariş Notu', blank=True, null=True)
    country = CountryField(multiple=False, default='TR', verbose_name='Ülke')

    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresler'

    def __str__(self):
        return self.customer.username



