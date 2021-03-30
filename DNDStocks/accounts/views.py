from django.shortcuts import render
from django.contrib.auth.models import User

def get_user(request) -> User or None:
    user = request.user
    if isinstance(user, User):
        return user

def account_page(request):
    return

def login_page(request):
    context = {
        'title': 'Login',
    }
    return render(request, 'accounts/login_page.html', context)
