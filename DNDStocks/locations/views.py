from django.shortcuts import render

# Create your views here.
def locations_page(request):
    return render(request, 'locations.html')
