from django.shortcuts import render

from accounts.views import get_user

# Create your views here.
def home_page(request):
    user = get_user(request)
    context = {
        'title': 'Home',
        'user': user,
        'pages': [
            ['party', '/party/'],
            ['locations', '/locations/'],
            ['travel', '/party/travel/'],
        ]
    }
    return render(request, 'home.html', context)
