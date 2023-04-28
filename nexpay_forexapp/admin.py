from django.contrib import admin
from .models import AnimeChars, Payment, PaymentHistory, UserProfile, ExchangeRate


# Register your models here.

admin.site.register(AnimeChars)
admin.site.register(Payment)
admin.site.register(PaymentHistory)
admin.site.register(UserProfile)
admin.site.register(ExchangeRate)

