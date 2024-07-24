from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from . serializers import LoginSerializer, ReviewSerializer, ReviewGenreSerializer, AddReviewSerializer, DeleteReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .utils import check_user, decode_jwt
import psycopg2
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction, connection,  IntegrityError
def hello(request):
    return HttpResponse('hello buddy')

class LoginApiView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            u = User.objects.create_user(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error":'is not valid.'})

class BookListView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        user = check_user(request)
        if user:
            id = user.username[-1]
            connection = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
            )
            cursor = connection.cursor()
            query = f'SELECT b.title, r.rating FROM reviews r, books b WHERE r.book_id = b.id and r.user_id={id}'
            cursor.execute(query)
            reviews = cursor.fetchall()
            review_list = []
            for r in reviews:
                review_list.append({
                    'book':r[0],
                    'rating':r[1],
                    # 'user':r[2]
                })
            serializer = ReviewSerializer(review_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'You are not logged in before'}, status=status.HTTP_404_NOT_FOUND)

class BookGenreListView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, genre):
        user = check_user(request)
        if user:
            id = user.username[-1]
            connection = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
            )
            cursor = connection.cursor()
            query = f"SELECT b.title, b.genre FROM reviews r, books b WHERE r.book_id = b.id and b.genre = '{genre}'"
            cursor.execute(query)
            reviews = cursor.fetchall()
            review_list = []
            for r in reviews:
                review_list.append({
                    'book':r[0],
                    'genre':r[1],
                    # 'user':r[2]
                })
            serializer = ReviewGenreSerializer(review_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'You are not logged in before'}, status=status.HTTP_404_NOT_FOUND)


class AddReviewApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = check_user(request)
        if user:
            id = user.username[-1]
            serializer = AddReviewSerializer(data=request.data)
            if serializer.is_valid():
                book = serializer.validated_data['book']
                rating = serializer.validated_data['rating']
                with connection.cursor() as cursor:
                    try:
                        query = f"INSERT INTO reviews(user_id, book_id, rating) VALUES ({id}, {book}, {rating})"
                        cursor.execute(query)
                        transaction.commit()
                        return Response({"message": "Review added successfully"},
                                        status=status.HTTP_201_CREATED)
                    except IntegrityError as e:
                        if 'unique_user_book_review' in str(e):
                            error_message = "You have already reviewed this book."
                            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        transaction.rollback()
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'You are not logged in before'}, status=status.HTTP_404_NOT_FOUND)

class UpdateReviewApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = check_user(request)
        if user:
            id = user.username[-1]
            serializer = AddReviewSerializer(data=request.data)
            if serializer.is_valid():
                book = serializer.validated_data['book']
                rating = serializer.validated_data['rating']
                with connection.cursor() as cursor:
                    try:
                        query = f"UPDATE reviews SET rating = {rating} WHERE user_id = {id} and book_id = {book}"
                        cursor.execute(query)
                        transaction.commit()
                        return Response({"message": "Review updated successfully"},
                                        status=status.HTTP_201_CREATED)
                    except Exception as e:
                        transaction.rollback()
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'You are not logged in before'}, status=status.HTTP_404_NOT_FOUND)
class DeleteReviewApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = check_user(request)
        if user:
            id = user.username[-1]
            serializer = DeleteReviewSerializer(data=request.data)
            if serializer.is_valid():
                book = serializer.validated_data['book']
                with connection.cursor() as cursor:
                    try:
                        query = f"DELETE FROM reviews WHERE user_id = {id} and book_id = {book}"
                        cursor.execute(query)
                        transaction.commit()
                        return Response({"message": "Review deleted successfully"},
                                        status=status.HTTP_201_CREATED)
                    except Exception as e:
                        transaction.rollback()
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'You are not logged in before'}, status=status.HTTP_404_NOT_FOUND)

#suggest book by genre
class SuggestBookApiView(APIView):
    def get(self, request):
        user = check_user(request)
        if user:
            id = user.username[-1]
            sql_genre = f"""
                        SELECT genre
                        FROM (
                            SELECT b.genre AS genre, AVG(r.rating) AS avg_rating
                            FROM reviews r
                            JOIN books b ON r.book_id = b.id
                            WHERE r.user_id = {id}
                            GROUP BY b.genre
                            ORDER BY avg_rating DESC
                            LIMIT 1
                        ) AS subquery
                    """
            try:
                with connection.cursor() as cursor:
                    # Find the most-rated genre
                    cursor.execute(sql_genre)
                    genre_result = cursor.fetchone()

                    if not genre_result:
                        return Response({"message": "there is not enough data about you."}, status=status.HTTP_404_NOT_FOUND)

                    genre_name = genre_result[0]
                    sql_books = f"""
                                            SELECT b.id, b.title, b.author, b.genre
                                            FROM books b
                                            WHERE b.genre = '{genre_name}'
                                        """
                    cursor.execute(sql_books, [genre_name])
                    books = cursor.fetchall()

                    books_list = []
                    for book in books:
                        books_list.append({
                            "id": book[0],
                            "title": book[1],
                            "author": book[2],
                            "genre_id": book[3],
                        })

                    return Response({"recommended_books": books_list}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)