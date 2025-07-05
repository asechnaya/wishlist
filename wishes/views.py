# wishes/views.py

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Wish, Tag
from .forms import WishForm

# Get an instance of the logger for the 'wishes' app
logger = logging.getLogger('wishes')

def register(request):
    logger.debug(f"Attempting to register user. Method: {request.method}")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            logger.info(f"User '{user.username}' registered and logged in successfully.")
            return redirect('wish_list')
        else:
            logger.warning(f"Registration failed for user. Form errors: {form.errors.as_json()}")
    else:
        logger.debug("Displaying registration form.")
    return render(request, 'registration/register.html', {'form': form})

@login_required
def wish_list(request):
    logger.debug(f"User '{request.user.username}' accessing wish list. Filter tag: {request.GET.get('tag')}")
    user_wishes = Wish.objects.filter(user=request.user)
    tags = Tag.objects.filter(wish__user=request.user).distinct()
    selected_tag = request.GET.get('tag')

    if selected_tag:
        user_wishes = user_wishes.filter(tags__name=selected_tag)
        logger.debug(f"Wish list filtered by tag: '{selected_tag}' for user '{request.user.username}'.")

    logger.info(f"Wish list displayed for user '{request.user.username}'. Total wishes: {user_wishes.count()}")
    return render(request, 'wishes/wish_list.html', {'wishes': user_wishes, 'tags': tags, 'selected_tag': selected_tag})

@login_required
def add_wish(request):
    logger.debug(f"User '{request.user.username}' attempting to add wish. Method: {request.method}")
    if request.method == 'POST':
        form = WishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            form._save_tags(wish)
            messages.success(request, 'Wish added successfully!')
            logger.info(f"Wish '{wish.title}' added by user '{request.user.username}'.")
            return redirect('wish_list')
        else:
            logger.warning(f"Failed to add wish for user '{request.user.username}'. Form errors: {form.errors.as_json()}")
    else:
        logger.debug(f"Displaying add wish form for user '{request.user.username}'.")
    return render(request, 'wishes/add_wish.html', {'form': form})

@login_required
def wish_detail(request, pk):
    # This view is for the owner to view their own wish details, potentially for editing/deleting.
    logger.debug(f"User '{request.user.username}' accessing wish detail for PK: {pk}")
    try:
        wish = get_object_or_404(Wish, pk=pk, user=request.user)
        logger.info(f"Wish '{wish.title}' (ID: {pk}) details displayed for user '{request.user.username}'.")
    except Exception as e:
        logger.error(f"Error accessing wish ID {pk} for user '{request.user.username}': {e}", exc_info=True)
        messages.error(request, "The wish you requested could not be found or you don't have permission to view it.")
        return redirect('wish_list')
    return render(request, 'wishes/wish_detail.html', {'wish': wish})

def public_wish_list(request, username):
    logger.debug(f"Accessing public wish list for username: '{username}'. Filter tag: {request.GET.get('tag')}")
    try:
        owner = get_object_or_404(User, username=username)
        wishes = Wish.objects.filter(user=owner)
        tags = Tag.objects.filter(wish__user=owner).distinct()
        selected_tag = request.GET.get('tag')

        if selected_tag:
            wishes = wishes.filter(tags__name=selected_tag)
            logger.debug(f"Public wish list for '{username}' filtered by tag: '{selected_tag}'.")

        context = {
            'wishes': wishes,
            'owner': owner,
            'tags': tags,
            'selected_tag': selected_tag,
            'is_owner': request.user.is_authenticated and request.user == owner
        }
        logger.info(f"Public wish list displayed for '{username}'. Total wishes: {wishes.count()}")
    except Exception as e:
        logger.error(f"Error accessing public wish list for username '{username}': {e}", exc_info=True)
        messages.error(request, f"Could not find a wishlist for user '{username}'.")
        return redirect('wish_list')
    return render(request, 'wishes/public_wish_list.html', context)

# NEW FUNCTION: Public Wish Detail View
def public_wish_detail(request, username, pk):
    logger.debug(f"Accessing public wish detail for username: '{username}', wish PK: {pk}")
    try:
        # First, get the owner of the wishlist
        owner = get_object_or_404(User, username=username)
        # Then, get the specific wish, ensuring it belongs to that owner
        wish = get_object_or_404(Wish, pk=pk, user=owner)
        logger.info(f"Public wish '{wish.title}' (ID: {pk}) displayed for owner '{username}'.")
    except Exception as e:
        logger.error(f"Error accessing public wish ID {pk} for user '{username}': {e}", exc_info=True)
        messages.error(request, "The wish you requested could not be found.")
        # Redirect to the owner's public wishlist if the specific wish isn't found
        return redirect('public_wish_list', username=username)
    return render(request, 'wishes/public_wish_detail.html', {'wish': wish, 'owner': owner})


@login_required
def edit_wish(request, pk):
    logger.debug(f"User '{request.user.username}' attempting to edit wish ID: {pk}. Method: {request.method}")
    try:
        wish = get_object_or_404(Wish, pk=pk, user=request.user)
    except Exception as e:
        logger.error(f"Error retrieving wish ID {pk} for editing by user '{request.user.username}': {e}", exc_info=True)
        messages.error(request, "The wish you tried to edit could not be found or you don't have permission.")
        return redirect('wish_list')

    if request.method == 'POST':
        form = WishForm(request.POST, request.FILES, instance=wish)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            form._save_tags(wish)
            messages.success(request, 'Wish updated successfully!')
            logger.info(f"Wish '{wish.title}' (ID: {pk}) updated by user '{request.user.username}'.")
            return redirect('wish_detail', pk=wish.pk)
        else:
            logger.warning(f"Failed to update wish ID {pk} for user '{request.user.username}'. Form errors: {form.errors.as_json()}")
    else:
        form = WishForm(instance=wish)
    return render(request, 'wishes/edit_wish.html', {'form': form, 'wish': wish})

@login_required
def delete_wish(request, pk):
    logger.debug(f"User '{request.user.username}' attempting to delete wish ID: {pk}. Method: {request.method}")
    try:
        wish = get_object_or_404(Wish, pk=pk, user=request.user)
    except Exception as e:
        logger.error(f"Error retrieving wish ID {pk} for deletion by user '{request.user.username}': {e}", exc_info=True)
        messages.error(request, "The wish you tried to delete could not be found or you don't have permission.")
        return redirect('wish_list')

    if request.method == 'POST':
        wish.delete()
        messages.info(request, 'Wish deleted successfully.')
        logger.info(f"Wish '{wish.title}' (ID: {pk}) deleted by user '{request.user.username}'.")
        return redirect('wish_list')
    logger.debug(f"Displaying delete confirmation for wish ID {pk} to user '{request.user.username}'.")
    return render(request, 'wishes/delete_wish_confirm.html', {'wish': wish})
