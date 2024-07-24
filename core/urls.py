from django.urls import path
from . import views
app_name = 'core'

urlpatterns = [
    path('api/login/', views.LoginApiView.as_view(), name='login'),
    path('api/book/list', views.BookListView.as_view(), name='books'),
    path('api/book/<str:genre>', views.BookGenreListView.as_view(), name='book_genre'),
    path('api/add', views.AddReviewApiView.as_view(), name='add_review'),
    path('api/update', views.UpdateReviewApiView.as_view(), name='update_review'),
    path('api/delete', views.DeleteReviewApiView.as_view(), name='delete_review'),
    path('api/suggest', views.SuggestBookApiView.as_view(), name='suggest_books'),
    path('hello', views.hello, name='hello')
]