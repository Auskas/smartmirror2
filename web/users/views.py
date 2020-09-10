from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm
import os
import urllib, json
from urllib.request import urlopen, Request
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('SM.setup')

def register(request):
    if User.objects.count() >= conf_settings.MAX_NUMBER_OF_USERS:
        messages.error(request, f'Нельзя добавить ещё одного пользователя!')
        return redirect('login')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            if User.objects.count() >= conf_settings.MAX_NUMBER_OF_USERS:
                print('CANNOT!')
                messages.error(request, f'Нельзя добавить ещё одного пользователя!')
                #return render(request, 'users/register.html', {'form': form})
            else:
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Аккаунт создан для {username}!')
                return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'u_form': u_form,
    }
    return render(request, 'users/profile.html', context)