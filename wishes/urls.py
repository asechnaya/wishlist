from django.urls import path
from . import views  # This imports your views.py from the current directory


urlpatterns = [
    # Path for the list of wishes (homepage of your wishlist app)
    # This matches the root path of the 'wishes' app, e.g., http://127.0.0.1:8000/
    path('', views.wish_list, name='wish_list'),

    # Path for adding a new wish
    # This will be accessible at, e.g., http://127.0.0.1:8000/add/
    path('add/', views.add_wish, name='add_wish'),

    # Path for viewing a specific wish's details
    # The <int:pk> part captures an integer (primary key) from the URL.
    # For example, http://127.0.0.1:8000/1/ would show details for wish with ID 1.
    path('<int:pk>/', views.wish_detail, name='wish_detail'),

    # Path for user registration
    # This will be accessible at, e.g., http://127.0.0.1:8000/register/
    path('register/', views.register, name='register'),

    # NEW URL PATTERN for a user's public wishlist
    # It will look like /wisher/username/

    path('wisher/<str:username>/', views.public_wish_list, name='public_wish_list'),

    # NEW URL TEMPLATES for editing and deleting

    path('<int:pk>/edit/', views.edit_wish, name='edit_wish'),
    path('<int:pk>/delete/', views.delete_wish, name='delete_wish'),


]


