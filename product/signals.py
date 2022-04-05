import random
import string
from django.contrib.auth.models import User
from .models import Order
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    randInt = random.randint(0, 9999999999)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(10))
    result_str += str(randInt)
    if created:
        Order.objects.create(customer=instance, transaction_id=result_str)
