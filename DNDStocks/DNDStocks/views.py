from django.shortcuts import render

# Create your views here.
def home_page(request):
    context = {
        'title': 'Home',
        'pages': [
            ['party', '/party/'],
            ['locations', '/locations/'],
            ['travel', '/party/travel/'],
        ]
    }
    return render(request, 'home.html', context)
