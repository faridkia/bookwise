import psycopg2
from rest_framework.response import Response
from rest_framework import  status
from django.contrib.auth.models import User
from django.conf import settings
import jwt
from rest_framework.exceptions import AuthenticationFailed

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')

def check_user(request):
    token = request.headers.get('Authorization')
    if not token:
        return Response({"error": "Authorization token is missing"}, status=status.HTTP_401_UNAUTHORIZED)
    token = token.split(' ')[1]
    payload = decode_jwt(token)
    username = payload.get('user_id')
    if not username:
        return Response({"error": "Username not found in token"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=username)
        return user
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
