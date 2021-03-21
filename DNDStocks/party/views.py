from django.shortcuts import render

from .models import Party
from locations.models import Location
from locations.models import Resource

from random import seed, random

# Create your views here.
def party_page(request):
    return render(request, 'party.html')

def travel_page(request):
    party = Party.objects.get(id=1)
    current_location = party.location
    all_locations = {current_location, *list(Location.objects.all())} # <--- KEEP AN EYE ON THIS

    # Trading calc
    seed(party.journey_count)
    local_resources = []
    all_resources = Resource.objects.all()
    for r in all_resources:
        if random() >= 0.05:
            adjustment = random()
            price = r.base_value + (adjustment * 2 * r.variance) - r.variance
            local_resources.append([
                r.id,
                r.name,
                price * 1.1,
                price * 0.9,
            ])

    context = {
        'title': 'Travel Page',
        'party': party,
        'current_location': current_location,
        'all_locations': all_locations,
        'local_resources': local_resources,
    }
    return render(request, 'travel.html', context)
