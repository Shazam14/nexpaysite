from rest_framework import serializers
from .models import Payment, AnimeChars, PaymentHistory, UserProfile, ExchangeRate

from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'user',) # Add any additional fields here


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name',)
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validate the login data.
        """
        email = data.get('email')
        password = data.get('password')

        # Perform custom validation here, such as checking if email and password match in the database
        # ...

        # Example validation: email and password are required fields
        if not email:
            raise serializers.ValidationError('Email is required')
        if not password:
            raise serializers.ValidationError('Password is required')

        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('amount', 'currency', 'exchange_rate', 'status', 'timestamp')



class AnimeCharsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimeChars
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')



class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['base_currency', 'target_currency', 'exchange_rate', 'created_at']


