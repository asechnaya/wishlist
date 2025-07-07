# wishes/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import WishViewSet, TagViewSet

router = DefaultRouter()
router.register(r'wishes', WishViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Custom URL for listing current user's wishes
    path('my-wishes/', WishViewSet.as_view({'get': 'list_my_wishes'}), name='api_my_wishes'),
    # Custom URL for public user wishes
    path('users/<str:username>/wishes/', WishViewSet.as_view({'get': 'public_user_wishes'}), name='api_public_user_wishes'),
    # Custom URL for public wish detail
    path('users/<str:username>/wishes/<int:pk>/', WishViewSet.as_view({'get': 'public_wish_detail'}), name='api_public_wish_detail'),
]
