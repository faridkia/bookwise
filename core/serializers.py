from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=60)

class ReviewSerializer(serializers.Serializer):
    book = serializers.CharField()
    rating = serializers.IntegerField()
    # user = serializers.CharField()

class ReviewGenreSerializer(serializers.Serializer):
    book = serializers.CharField()
    genre = serializers.CharField()

class AddReviewSerializer(serializers.Serializer):
    book = serializers.IntegerField()
    rating = serializers.IntegerField(max_value=5, min_value=1)

class DeleteReviewSerializer(serializers.Serializer):
    book = serializers.IntegerField()
