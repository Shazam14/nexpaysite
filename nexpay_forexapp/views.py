#import stripe
import stripe
from django.http import HttpResponse
import requests


from django.contrib.auth.models import User
from django.core.mail import send_mail #for mail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework import permissions, status, viewsets, generics
from nexpay_forexapp.serializers import PaymentSerializer, AnimeCharsSerializer, LoginSerializer, UserSerializer, ExchangeRateSerializer
from .models import PaymentHistory, AnimeChars, Payment, ExchangeRate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from django.conf import settings


from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token



#need to set this as environment variable

# views.py
stripe.api_key=settings.STRIPE_SECRET_KEY

API_URL="http/locahost:8000"


class RegistrationAPIView(CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        response_data = {
            'user_id': user.id,
            'username': user.username,
            'token': token.key,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginAPIView(CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'user_id': user.id,
                'username': user.username,
                'token': token.key,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                'detail': 'Invalid username or password',
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

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

# checking out



# @csrf_exempt
# def create_checkout_session(request):
#     if request.method == 'POST':
#         # Get the necessary data for creating a Checkout Session from the request
#         # For example, you can get the price and product information from the request's POST data
#         animechars_id=self.kwargs["pk"]
#         print(animechars_id)
#         price_id = request.POST.get('price_id')
#         success_url = request.POST.get('success_url')
#         cancel_url = request.POST.get('cancel_url')

#         # Create a Checkout Session
#         try:
# #             animeproduct=AnimeChars.objects.get(id=animechars_id)
# #             print(animeproduct)
#             session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                     {
#                         # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                         'price_data': {
#                             'currency':'AUD',
#                              'unit_amount':int(animeproduct.price) * 100,
#                              'product_data':{
#                                  'name':animeproduct.anime_name,
#                                  'images':[f"{API_URL}/{animeproduct.anime_image}"]

#                              }
#                         },
#                         'quantity': 1,
#                     },
#                 ],
#             mode='payment',
#             success_url=success_url,
#             cancel_url=cancel_url,
#         )

#             return Response({'sessionId': session.id})
#         except Exception as e:
#             return Response({'msg':'something went wrong while creating stripe session','error':str(e)}, status=500)
       
    
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




# import requests
# from decimal import Decimal
# from django.http import JsonResponse

# def process_payment(request):
#     if request.method == 'POST':
#         amount = Decimal(request.POST.get('amount'))
#         currency = request.POST.get('currency')
#         # Make API request to get latest exchange rate
#         status_code = response.status_code
#         result = response.text

#         response = requests.request("GET", url, headers=headers, data = payload)


#         response = requests.get('https://api.exchangeratesapi.io/latest')
#         exchange_rate = Decimal(response.json()['rates'][currency])
#         converted_amount = amount * exchange_rate
#         # Save payment details to database
#         payment = Payment(amount=amount, currency=currency, exchange_rate=exchange_rate,
#                           status='success', converted_amount=converted_amount)
#         payment.save()
#         return JsonResponse({'status': 'success', 'converted_amount': str(converted_amount)})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request'})



# # views for payment process
# def process_payment(request):
#     if request.method == 'POST':
#         # Get the payment amount and currency from the form
#         amount = request.POST['amount']
#         currency = request.POST['currency']
        
#         # Create a Stripe payment intent
#         intent = stripe.PaymentIntent.create(
#             amount=amount,
#             currency=currency
#         )
        
#         # Render the payment intent to the template for processing
#         return render(request, 'payment/process_payment.html', {'client_secret': intent['client_secret']})

# def payment_callback(request):
#     if request.method == 'POST':
#         # Get the payment status and transaction details from the payment gateway callback
#         payment_status = request.POST['status']
#         transaction_id = request.POST['transaction_id']
        
#         # Handle the payment status and update your database accordingly
#         if payment_status == 'succeeded':
#             # Payment successful, update the order status in your database
#             order = Order.objects.get(transaction_id=transaction_id)
#             order.status = 'completed'
#             order.save()
            
#         # Redirect to a success or failure page based on the payment status
#         if payment_status == 'succeeded':
#             return redirect('payment:success')
#         else:
#             return redirect('payment:failure')
