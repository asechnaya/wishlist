import re
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django import forms as forms
from django.contrib.auth import get_user_model
from .models import Wish, Tag, User
from .forms import WishForm, ProfileForm

# Initialize logger for the wishes app
logger = logging.getLogger('wishes')

# Get the custom User model
User = get_user_model()


# New form for user registration with custom validation
class CustomUserCreationForm(UserCreationForm):
    """
    A custom UserCreationForm to validate the username field.
    Allows only Latin letters, numbers, dashes, and underscores.
    """

    def clean_username(self):
        username = self.cleaned_data['username']
        # Use regex to validate username: allows a-z, A-Z, 0-9, dash, and underscore.
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError("Username must contain only Latin letters, numbers, dashes, or underscores.")
        return username


def main_feed(request):
    """
    Renders the main public feed of wishes.
    Only shows public, non-completed wishes that have an image.
    """
    logger.debug("Accessing main feed.")
    selected_tag = request.GET.get('tag')

    # Exclude private and completed wishes, and those without an image.
    # The `|` operator is used for an OR condition within a Q object.
    all_public_wishes_query = Wish.objects.filter(
        private=False, completed=False
    ).exclude(
        Q(image__isnull=True) | Q(image='')
    )

    tags = Tag.objects.filter(
        wish__in=all_public_wishes_query
    ).distinct()

    if selected_tag:
        all_public_wishes_query = all_public_wishes_query.filter(tags__name=selected_tag)
        logger.debug(f"Main feed filtered by tag: '{selected_tag}'.")

    all_public_wishes = all_public_wishes_query.order_by('-created_at')[:20]

    context = {
        'wishes': all_public_wishes,
        'tags': tags,
        'selected_tag': selected_tag,
    }
    return render(request, 'wishes/main_feed.html', context)


@login_required
def wish_list(request):
    """
    Renders the logged-in user's private wishlist.
    Separates wishes into active and completed sections.
    """
    logger.debug("Accessing private wishlist.")
    selected_tag = request.GET.get('tag')
    all_user_wishes = Wish.objects.filter(user=request.user)

    if selected_tag:
        all_user_wishes = all_user_wishes.filter(tags__name=selected_tag)

    tags = Tag.objects.filter(wish__user=request.user).distinct()

    active_wishes = all_user_wishes.filter(completed=False)
    completed_wishes = all_user_wishes.filter(completed=True)

    context = {
        'active_wishes': active_wishes,
        'completed_wishes': completed_wishes,
        'tags': tags,
        'selected_tag': selected_tag,
    }
    return render(request, 'wishes/wish_list.html', context)


@login_required
def add_wish(request):
    """
    Handles adding a new wish.
    """
    if request.method == 'POST':
        form = WishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            form._save_tags(wish)  # Call the custom tag-saving method
            logger.info(f"New wish '{wish.title}' added by {request.user.username}.")
            return redirect('wish_list')
    else:
        form = WishForm()

    return render(request, 'wishes/add_wish.html', {'form': form})


@login_required
def edit_wish(request, pk):
    """
    Handles editing an existing wish.
    """
    wish = get_object_or_404(Wish, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WishForm(request.POST, request.FILES, instance=wish)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            form._save_tags(wish)  # Call the custom tag-saving method
            logger.info(f"Wish '{wish.title}' (ID: {pk}) updated by {request.user.username}.")
            return redirect('wish_detail', pk=pk)
    else:
        form = WishForm(instance=wish)

    return render(request, 'wishes/edit_wish.html', {'form': form, 'wish': wish})


@login_required
def delete_wish(request, pk):
    """
    Handles deleting a wish.
    """
    wish = get_object_or_404(Wish, pk=pk, user=request.user)
    if request.method == 'POST':
        wish_title = wish.title
        wish.delete()
        logger.info(f"Wish '{wish_title}' (ID: {pk}) deleted by {request.user.username}.")
        return redirect('wish_list')

    return render(request, 'wishes/delete_wish_confirm.html', {'wish': wish})


def register(request):
    """
    Handles new user registration with a custom form for username validation.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}.")
            return redirect('wish_list')
    else:
        # For a GET request, initialize a new, empty form.
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """
    Allows a user to view and edit their profile information.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Django messages framework provides user feedback.
            messages.success(request, 'Your profile was updated successfully!')
            logger.info(f"Profile for {request.user.username} updated.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'wishes/profile.html', {'form': form})


def public_wish_list(request, username):
    """
    Renders a public wishlist page for a specific user.
    """
    logger.info(f"Accessing public wishlist for user: {username}.")
    owner = get_object_or_404(User, username=username)
    selected_tag = request.GET.get('tag')

    all_wishes_query = Wish.objects.filter(
        user=owner, private=False, completed=False
    ).exclude(
        Q(image__isnull=True) | Q(image='')
    )

    tags = Tag.objects.filter(
        wish__in=all_wishes_query
    ).distinct()

    if selected_tag:
        all_wishes_query = all_wishes_query.filter(tags__name=selected_tag)
        logger.debug(f"Public wishlist filtered by tag: '{selected_tag}'.")

    context = {
        'wishes': all_wishes_query,
        'owner': owner,
        'is_owner': request.user == owner,
        'tags': tags,
        'selected_tag': selected_tag,
    }
    logger.info(f"Found {all_wishes_query.count()} public wishes for user {username}.")
    return render(request, 'wishes/public_wish_list.html', context)


def public_wish_detail(request, username, pk):
    """
    Renders the detail page for a single public wish.
    """
    logger.debug(f"Accessing public wish detail for user '{username}', wish ID: {pk}.")
    owner = get_object_or_404(User, username=username)

    try:
        # Check if the logged-in user is the owner, or if the wish is public
        if request.user.is_authenticated and request.user == owner:
            wish = get_object_or_404(Wish, pk=pk, user=owner)
        else:
            wish = get_object_or_404(Wish, pk=pk, user=owner, private=False, completed=False)

        logger.info(f"Wish detail for '{wish.title}' accessed.")
    except Exception as e:
        logger.error(f"Failed to retrieve public wish detail for ID {pk}: {e}")
        return redirect('main_feed')

    context = {
        'wish': wish,
        'owner': owner,
        'is_owner': request.user == owner,
    }
    return render(request, 'wishes/public_wish_detail.html', context)
