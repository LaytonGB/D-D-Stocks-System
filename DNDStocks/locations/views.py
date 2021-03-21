from django.shortcuts import render

def locations_page(request):
    return render(request, 'locations.html')
