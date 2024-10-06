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
import json
from asgiref.sync import sync_to_async


# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')
google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
ticketmaster_api_key = env('TICKETMASTER_API_KEY')


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

def launch_page(request):
    return render(request, 'eventapp/index.html')

def map_view(request):
    latitude = request.GET.get('latitude') or '37.7749'
    longitude = request.GET.get('longitude') or '-122.4194'
    radius = request.GET.get('radius', '30')  # Default radius is 30 miles
    
    if not latitude or not longitude:
        return JsonResponse({'error': 'Latitude and Longitude are required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    ticketmaster_url = f'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)
    if response.status_code == status.HTTP_200_OK:
        events = response.json().get('_embedded', {}).get('events', [])
        events_simplified = [{
            'name': event['name'],
            'start': event['dates']['start']['localDate'],
            'description': event['info'] if 'info' in event else 'No description available.',
            'latitude': event['_embedded']['venues'][0]['location']['latitude'],
            'longitude': event['_embedded']['venues'][0]['location']['longitude']
        } for event in events]

    context = {        
        'google_maps_api_key': google_maps_api_key,
        'events': events_simplified     
    }
    return render(request, 'eventapp/home.html', context)


def fetch_events_from_ticketmaster(latitude, longitude, radius):
    ticketmaster_url = f'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)
    if response.status_code == status.HTTP_200_OK:
        events = response.json().get('_embedded', {}).get('events', [])
        return [{
            'name': event['name'],
            'start': event['dates']['start']['localDate'],
            'description': event['info'] if 'info' in event else 'No description available.',
            'latitude': event['_embedded']['venues'][0]['location']['latitude'],
            'longitude': event['_embedded']['venues'][0]['location']['longitude']
        } for event in events]
    return []

def fetch_events(request):
    latitude = request.GET.get('latitude') or '37.7749'
    longitude = request.GET.get('longitude') or '-122.4194'
    radius = request.GET.get('radius', '30')  # Default radius is 30 miles
    
    if not latitude or not longitude:
        return JsonResponse({'error': 'Latitude and Longitude are required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    ticketmaster_url = f'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)
    if response.status_code == status.HTTP_200_OK:
        events = response.json().get('_embedded', {}).get('events', [])

    return render(request, 'eventapp/events.html', {'events': events})