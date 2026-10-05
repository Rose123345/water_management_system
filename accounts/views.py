from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme


def login(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created. A system administrator must assign your role before you can access the workspace.',
            )
            return redirect('accounts:login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})