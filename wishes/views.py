from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages  # create notifications
from .models import Wish, Tag
from .forms import WishForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')  # Notification
            return redirect('wish_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def wish_list(request):
    user_wishes = Wish.objects.filter(user=request.user)
    tags = Tag.objects.all()
    selected_tag = request.GET.get('tag')

    if selected_tag:
        user_wishes = user_wishes.filter(tags__name=selected_tag)

    return render(request, 'wishes/wish_list.html', {'wishes': user_wishes, 'tags': tags, 'selected_tag': selected_tag})


@login_required
def add_wish(request):
    if request.method == 'POST':
        form = WishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            form._save_tags(wish)  # Use inner method for tag saving
            messages.success(request, 'Wish added successfully!') # Уведомление
            return redirect('wish_list')
    else:
        form = WishForm()
    return render(request, 'wishes/add_wish.html', {'form': form})


@login_required
def wish_detail(request, pk):
    wish = get_object_or_404(Wish, pk=pk, user=request.user)
    return render(request, 'wishes/wish_detail.html', {'wish': wish})


def public_wish_list(request, username):
    owner = get_object_or_404(User, username=username)
    wishes = Wish.objects.filter(user=owner)
    tags = Tag.objects.all()
    selected_tag = request.GET.get('tag')

    if selected_tag:
        wishes = wishes.filter(tags__name=selected_tag)

    context = {
        'wishes': wishes,
        'owner': owner,
        'tags': tags,
        'selected_tag': selected_tag,
        'is_owner': request.user.is_authenticated and request.user == owner
    }
    return render(request, 'wishes/public_wish_list.html', context)


@login_required
def edit_wish(request, pk):
    # Получаем желание, убеждаясь, что оно принадлежит текущему пользователю
    wish = get_object_or_404(Wish, pk=pk, user=request.user)

    if request.method == 'POST':
        # Передаем instance=wish, чтобы форма была заполнена данными существующего желания
        form = WishForm(request.POST, request.FILES, instance=wish)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user # Убеждаемся, что пользователь остается прежним
            wish.save()
            form._save_tags(wish)  # Сохраняем теги
            messages.success(request, 'Wish updated successfully!') # Уведомление
            return redirect('wish_detail', pk=wish.pk) # Перенаправляем на страницу деталей желания
    else:
        # Заполняем форму данными существующего желания
        form = WishForm(instance=wish)
    return render(request, 'wishes/edit_wish.html', {'form': form, 'wish': wish})


# НОВАЯ ФУНКЦИЯ: Удаление желания
@login_required
def delete_wish(request, pk):
    # Получаем желание, убеждаясь, что оно принадлежит текущему пользователю
    wish = get_object_or_404(Wish, pk=pk, user=request.user)

    if request.method == 'POST':
        wish.delete()
        messages.info(request, 'Wish deleted successfully.') # Уведомление
        return redirect('wish_list') # Перенаправляем на список желаний
    # Если это GET-запрос, показываем страницу подтверждения
    return render(request, 'wishes/delete_wish_confirm.html', {'wish': wish})
