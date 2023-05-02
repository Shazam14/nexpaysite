from django.contrib import admin
from .models import AnimeChars, Payment, ExchangeRate, UserAccount
from rest_framework.authtoken.admin import TokenAdmin


# Register your models here.
admin.site.register(UserAccount)
admin.site.register(AnimeChars)
admin.site.register(Payment)
#admin.site.register(User)

# admin.site.register(PaymentHistory)
# admin.site.register(UserProfile)
admin.site.register(ExchangeRate)

#TokenAdmin.raw_id_fields = ['user']


