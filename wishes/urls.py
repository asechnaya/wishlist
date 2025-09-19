from django.urls import path, include
from . import views

urlpatterns = [
    # Main public feed
    path('', views.main_feed, name='main_feed'),

    # User's private wishlist page
    path('my-wishes/', views.wish_list, name='wish_list'),

    # Add a new wish page
    path('add/', views.add_wish, name='add_wish'),

    # Edit wish page
    path('<int:pk>/edit/', views.edit_wish, name='edit_wish'),

    # Delete wish confirmation page
    path('<int:pk>/delete/', views.delete_wish, name='delete_wish'),

    # User registration page
    path('register/', views.register, name='register'),

    # User profile page
    path('profile/', views.profile, name='profile'),

    # Public wishlist for a specific user
    path('wisher/<str:username>/', views.public_wish_list, name='public_wish_list'),

    # Public wish detail page for a specific user's wish
    # This URL now correctly includes both the username and the wish's primary key
    path('wisher/<str:username>/<int:pk>/', views.public_wish_detail, name='public_wish_detail'),
]
