from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any additional fields for user profile here
    # e.g. profile picture, address, etc.

    def __str__(self):
        return self.user.username
    

class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)    

class AnimeChars(models.Model):
    anime_name = models.CharField(max_length=100)
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    anime_image = models.ImageField(upload_to="thumbnail")
    anime_url = models.URLField()

    def __str__(self):
        return self.anime_name

class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    status = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Payment: {self.amount} {self.currency}'


class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    anime_product = models.ForeignKey(AnimeChars, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField()


    def __str__(self):
        return self.anime_product.anime_name