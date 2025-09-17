# wishes/urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    # Main public feed (homepage)
    path('', views.main_feed, name='main_feed'),

    # Private wishlist for the logged-in user
    path('my-wishes/', views.wish_list, name='wish_list'),

    # Actions for creating, editing, and deleting wishes
    path('add/', views.add_wish, name='add_wish'),
    path('<int:pk>/edit/', views.edit_wish, name='edit_wish'),
    path('<int:pk>/delete/', views.delete_wish, name='delete_wish'),

    # User authentication paths
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Public wishlist for a specific user
    path('wisher/<str:username>/', views.public_wish_list, name='public_wish_list'),

    # Public wish detail page for a specific user and wish
    path('wisher/<str:username>/<int:pk>/', views.public_wish_detail, name='public_wish_detail'),
]
