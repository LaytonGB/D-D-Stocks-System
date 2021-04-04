from django.shortcuts import render

from accounts.views import get_user

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

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
