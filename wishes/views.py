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

logger = logging.getLogger('wishes')


# NEW FUNCTION: Main public feed page
def main_feed(request):
    logger.debug("Accessing main public feed.")

    # Start with all public and non-completed wishes
    all_public_wishes_query = Wish.objects.filter(private=False, completed=False)

    # Get all tags that are associated with public, non-completed wishes
    tags = Tag.objects.filter(wish__private=False, wish__completed=False).distinct()
    selected_tag = request.GET.get('tag')

    # Apply filtering BEFORE ordering and slicing
    if selected_tag:
        all_public_wishes_query = all_public_wishes_query.filter(tags__name=selected_tag)
        logger.debug(f"Main feed filtered by tag: '{selected_tag}'.")

    # Now apply ordering and slicing
    all_public_wishes = all_public_wishes_query.order_by('-created_at')[:20]  # Limit to 20 for a feed

    context = {
        'wishes': all_public_wishes,
        'tags': tags,
        'selected_tag': selected_tag,
        'is_main_feed': True  # A flag to differentiate this template from others
    }
    logger.info(f"Main feed displayed. Total public wishes: {all_public_wishes.count()}")
    return render(request, 'wishes/main_feed.html', context)


def register(request):
    logger.debug(f"Attempting to register user. Method: {request.method}")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            logger.info(f"User '{user.username}' registered and logged in successfully.")
            return redirect('wish_list')  # Redirect to user's private wish list
        else:
            logger.warning(f"Registration failed for user. Form errors: {form.errors.as_json()}")
    else:
        logger.debug("Displaying registration form.")
    return render(request, 'registration/register.html', {'form': form})


@login_required
def wish_list(request):
    logger.debug(f"User '{request.user.username}' accessing wish list. Filter tag: {request.GET.get('tag')}")
    all_user_wishes = Wish.objects.filter(user=request.user)
    tags = Tag.objects.filter(wish__user=request.user).distinct()
    selected_tag = request.GET.get('tag')

    if selected_tag:
        all_user_wishes = all_user_wishes.filter(tags__name=selected_tag)
        logger.debug(f"Wish list filtered by tag: '{selected_tag}' for user '{request.user.username}'.")

    active_wishes = all_user_wishes.filter(completed=False)
    completed_wishes = all_user_wishes.filter(completed=True)

    logger.info(
        f"Wish list displayed for user '{request.user.username}'. Active wishes: {active_wishes.count()}, Completed wishes: {completed_wishes.count()}")
    return render(request, 'wishes/wish_list.html', {
        'active_wishes': active_wishes,
        'completed_wishes': completed_wishes,
        'tags': tags,
        'selected_tag': selected_tag
    })


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
            logger.warning(
                f"Failed to add wish for user '{request.user.username}'. Form errors: {form.errors.as_json()}")
    else:
        logger.debug(f"Displaying add wish form for user '{request.user.username}'.")
    return render(request, 'wishes/add_wish.html', {'form': form})


@login_required
def wish_detail(request, pk):
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
        wishes = Wish.objects.filter(user=owner, private=False, completed=False)
        tags = Tag.objects.filter(wish__user=owner, wish__private=False, wish__completed=False).distinct()
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
        return redirect('main_feed')  # Redirect to main feed if public list not found
    return render(request, 'wishes/public_wish_list.html', context)


def public_wish_detail(request, username, pk):
    logger.debug(f"Accessing public wish detail for username: '{username}', wish PK: {pk}")
    try:
        owner = get_object_or_404(User, username=username)
        wish = get_object_or_404(Wish, pk=pk, user=owner, private=False, completed=False)
        logger.info(f"Public wish '{wish.title}' (ID: {pk}) displayed for owner '{username}'.")
    except Exception as e:
        logger.error(f"Error accessing public wish ID {pk} for user '{username}': {e}", exc_info=True)
        messages.error(request, "The wish you requested could not be found or is private/completed.")
        return redirect('main_feed')  # Redirect to main feed if public wish not found
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
            logger.warning(
                f"Failed to update wish ID {pk} for user '{request.user.username}'. Form errors: {form.errors.as_json()}")
    else:
        form = WishForm(instance=wish)
    return render(request, 'wishes/edit_wish.html', {'form': form, 'wish': wish})


@login_required
def delete_wish(request, pk):
    logger.debug(f"User '{request.user.username}' attempting to delete wish ID: {pk}. Method: {request.method}")
    try:
        wish = get_object_or_404(Wish, pk=pk, user=request.user)
    except Exception as e:
        logger.error(f"Error retrieving wish ID {pk} for deletion by user '{request.user.username}': {e}",
                     exc_info=True)
        messages.error(request, "The wish you tried to delete could not be found or you don't have permission.")
        return redirect('wish_list')

    if request.method == 'POST':
        wish.delete()
        messages.info(request, 'Wish deleted successfully.')
        logger.info(f"Wish '{wish.title}' (ID: {pk}) deleted by user '{request.user.username}'.")
        return redirect('wish_list')
    logger.debug(f"Displaying delete confirmation for wish ID {pk} to user '{request.user.username}'.")
    return render(request, 'wishes/delete_wish_confirm.html', {'wish': wish})
