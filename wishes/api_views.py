# wishes/api_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Wish, Tag
from .serializers import WishSerializer, TagSerializer
from django.contrib.auth.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class WishViewSet(viewsets.ModelViewSet):
    queryset = Wish.objects.all().order_by('-created_at')  # Default queryset
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        # For authenticated users, show all their wishes (private, completed included)
        # For anonymous users, filter by private=False and completed=False
        if self.request.user.is_authenticated:
            # If it's the user's own list, show all their wishes
            if self.action == 'list_my_wishes':
                return Wish.objects.filter(user=self.request.user).order_by('-created_at')
            # For other actions (like retrieving a single wish), if the user is authenticated,
            # they can see their own wishes regardless of private/completed status.
            # However, for public feed, we still filter.
            if self.action == 'list' and not self.request.user.is_superuser:  # Main feed for non-superusers
                return Wish.objects.filter(private=False, completed=False).order_by('-created_at')
            return Wish.objects.all().order_by('-created_at')  # Superusers see all

        # For anonymous users, only show public and non-completed wishes
        return Wish.objects.filter(private=False, completed=False).order_by('-created_at')

    def perform_create(self, serializer):
        # Assign the current user as the owner of the wish
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def list_my_wishes(self, request):
        """
        List all wishes for the authenticated user.
        """
        wishes = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(wishes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_user_wishes(self, request, username=None):
        """
        List public and non-completed wishes for a specific user.
        """
        owner = get_object_or_404(User, username=username)
        wishes = Wish.objects.filter(user=owner, private=False, completed=False).order_by('-created_at')
        serializer = self.get_serializer(wishes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def public_wish_detail(self, request, pk=None, username=None):
        """
        Retrieve a single public and non-completed wish for a specific user.
        """
        owner = get_object_or_404(User, username=username)
        wish = get_object_or_404(Wish, pk=pk, user=owner, private=False, completed=False)
        serializer = self.get_serializer(wish)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]  # Tags are globally readable
