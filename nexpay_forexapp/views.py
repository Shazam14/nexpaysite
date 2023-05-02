#import stripe
import stripe
from django.http import HttpResponse
import requests
import logging

from django.contrib.auth.models import User
from django.core.mail import send_mail #for mail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect


from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer


from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework import permissions, status, viewsets, generics, authentication
from nexpay_forexapp.serializers import PaymentSerializer, AnimeCharsSerializer, LoginSerializer, UserSerializer, ExchangeRateSerializer
from .models import AnimeChars, Payment, ExchangeRate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from django.conf import settings


from django.contrib.auth import authenticate, login

from knox.views import LoginView as KnoxLoginView


from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response



#need to set this as environment variable

# views.py
stripe.api_key=settings.STRIPE_SECRET_KEY

API_URL="http/locahost:8000"

class UserAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegistrationAPIView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        response_data = {
            'user_id': user.id,
            'username': user.username,
            'token': token.key,
            'email': user.email,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LoginSerializer

    def post(self, request, format=None):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request=request, email=email, password=password)
        if user is not None:
            login(request, user)
            return super(LoginAPIView, self).post(request, format=None)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class AnimeCharsPreview(RetrieveAPIView):
    serializer_class=AnimeCharsSerializer
    permission_classes=[permissions.AllowAny]
    queryset=AnimeChars.objects.all()



# from rest_framework.decorators import api_view
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()

class PaymentAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


    def index(request):
        return HttpResponse("Hello, world. You're at the foreign exchange payment.")


#exchange rate --different approach
class ExchangeRateViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def get_exchange_rate(self, request):
        base_currency = self.request.query_params.get('base_currency', None)
        target_currency = self.request.query_params.get('target_currency', None)
        if not base_currency or not target_currency:
            return Response({'error': 'Both base_currency and target_currency are required.'}, status=400)
        try:
            # Call the external API to get the exchange rate
            response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}')
            if response.status_code != 200:
                return Response({'error': 'Failed to fetch exchange rate from external API.'}, status=500)
            data = response.json()
            exchange_rate = data['rates'].get(target_currency, None)
            if not exchange_rate:
                return Response({'error': 'Exchange rate not found for the given currencies.'}, status=404)
            # Store the exchange rate in the database
            exchange_rate_obj = ExchangeRate(base_currency=base_currency, target_currency=target_currency, exchange_rate=exchange_rate)
            exchange_rate_obj.save()
            # Serialize and return the exchange rate
            serializer = ExchangeRateSerializer(exchange_rate_obj)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
class CreateCheckOutSession(APIView):
    def post(self, request, *args, **kwargs):
        animechars_id=self.kwargs["pk"]
        print(animechars_id)
        try:
            animeproduct=AnimeChars.objects.get(id=animechars_id)
            print(animeproduct)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency':'AUD',
                             'unit_amount':int(animeproduct.price) * 100,
                             'product_data':{
                                 'name':animeproduct.anime_name,
                                 'images':[f"{API_URL}/{animeproduct.anime_image}"]

                             }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id":animeproduct.id
                },
                mode='payment',
                success_url=settings.SITE_URL + '?success=true',
                cancel_url=settings.SITE_URL + '?canceled=true',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return Response({'msg':'something went wrong while creating stripe session','error':str(e)}, status=500)
        



@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_SECRET_WEBHOOK
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        print(session)
        customer_email=session['customer_details']['email']
        prod_id=session['metadata']['product_id']
        product=Product.objects.get(id=prod_id)
        #sending confimation mail
        send_mail(
            subject="payment sucessful",
            message=f"thank for your purchase your order is ready.  download url {animeprod.book_url}",
            recipient_list=[customer_email],
            from_email="shazflicks@gmail.com"
        )

        #creating payment history
        # user=User.objects.get(email=customer_email) or None

        PaymentHistory.objects.create(product=product, payment_status=True)
    # Passed signature verification
    return HttpResponse(status=200)



