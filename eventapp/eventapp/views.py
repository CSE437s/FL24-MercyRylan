# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests
import environ


# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')

# Registration View
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new user
        user = User.objects.create_user(username=username, password=password, email=email)
        # Generate token for the new user
        token = Token.objects.create(user=user)
        
        return Response({'message': 'User registered successfully', 'token': token.key}, status=status.HTTP_201_CREATED)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate token if the user is authenticated
            token, created = Token.objects.get_or_create(user=user)
            return Response({'message': 'Login successful', 'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
    context = {        
        'google_maps_api_key': google_maps_api_key
    }
    return render(request, 'eventapp/home.html', context)