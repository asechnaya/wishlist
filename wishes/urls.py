# wishes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # User's own private wish list (homepage for logged-in users)
    path('', views.wish_list, name='wish_list'),

    # Page to add a new wish
    path('add/', views.add_wish, name='add_wish'),

    # Page to view details of a user's own wish (requires login)
    path('<int:pk>/', views.wish_detail, name='wish_detail'),

    # User registration page
    path('register/', views.register, name='register'),

    # Public wish list page for a specific user (e.g., /wisher/username/)
    path('wisher/<str:username>/', views.public_wish_list, name='public_wish_list'),

    # Public wish detail page for a specific wish belonging to a specific user
    # (e.g., /wisher/username/123/)
    path('wisher/<str:username>/<int:pk>/', views.public_wish_detail, name='public_wish_detail'),

    # Page to edit a user's own wish (requires login)
    path('<int:pk>/edit/', views.edit_wish, name='edit_wish'),

    # Page to confirm deletion of a user's own wish (requires login)
    path('<int:pk>/delete/', views.delete_wish, name='delete_wish'),
]
