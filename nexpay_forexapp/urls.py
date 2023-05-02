from django.urls import path
from . views import AnimeCharsPreview, stripe_webhook_view, CreateCheckOutSession, RegistrationAPIView, UserAPIView, CustomAuthToken, LoginAPIView, ListUsers
from django.views.decorators.csrf import csrf_exempt
#from rest_framework.authtoken.views import obtain_auth_token





urlpatterns = [
    #authentication proocess
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    #path('users/', ListUsers.as_view(), name='users_list'),
    
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('stripe-webhook/', stripe_webhook_view, name='stripe-webhook'),
    path('animeproduct/<int:pk>/', AnimeCharsPreview.as_view(), name="animeproduct"),
    path('api/checkout-session/', CreateCheckOutSession.as_view(), name='checkout-session')

    # path("process_payment", views.process_payment, name="process_payment"),
    # path("payment_callback", views.payment_callback, name="payment_callback"),
]
