from django.shortcuts import render

# Create your views here.
def party_page(request):
    return render(request, 'party.html')
