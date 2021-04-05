from pprint import pprint
from typing import Any, Tuple
from time import perf_counter

from django.db import connection
from django.shortcuts import redirect, render
from django.contrib import messages

from DNDStocks.views import dictfetchall

from .models import Party, Inventory, TradeHistory, TravelHistory
from locations.models import Location, LocationResource, Resource

from random import seed, random

# Create your views here.
def party_page(request):
    return render(request, 'party.html')

def travel_page(request):
    party: Party = Party.objects.get(id=1)
    current_location = party.location
    newest_journey = party.latest_journey()
    all_locations = Location.objects.exclude(id=current_location.id).order_by('name')
    all_resources = Resource.objects.all()

    # Add party resources to inventory table if needed
    for r in all_resources:
        try:
            party.inventory.get(resource_id=r.id)
        except:
            party.inventory.add(r)

    # Trading calc and party inventory
    local_resources, inventory, local_specialities = get_stocks(party)

    context = {
        'title': 'Travel Page',
        'party': party,
        'inventory': inventory,
        'current_location': current_location,
        'all_locations': all_locations,
        'local_resources': local_resources,
        'local_specialities': local_specialities,
    }

    return render(request, 'travel.html', context)

def get_stocks(party: Party) -> Tuple[list[Any], list[Any], list[int]]:
    """ Using the party journey count as the random seed,
        Return the local resources, party inventory, and local specialities in a tuple
        applying any necessary randomization.

        local_resources: resource id, resource name, buying price, selling price
        inventory: resource id, resource name, # resource in party inventory, resource base value
        local_specialities: resource id list for all special deals"""
    seed(party.journey_count)
    location_resources = LocationResource.objects.filter(location_id=party.location.id)
    all_resources: list[Resource] = Resource.objects.all()
    local_resources = []
    inventory = []
    local_specialities = []
    for r in all_resources:
        lr: LocationResource
        try:
            lr = location_resources.get(resource_id=r.id)
        except:
            lr = None
        r_set = party.get_resource(r) # get the entry in party personal resources for resource
        inventory.append({
            'id': r.id,
            'name': r.name,
            'quantity': r_set.quantity,
            'base_value': r.base_value
        })
        if lr is not None:
            local_specialities.append(r.id)
            tender_probability = lr.probability or 0.95
        else:
            tender_probability = 0.95

        if random() < tender_probability:
            price = get_price(r, lr)
            local_resources.append({
                'id': r.id,
                'name': r.name,
                'buy_price': price * 1.15,
                'sell_price': price * 0.9,
            })

    return local_resources, inventory, local_specialities

def get_price(r:Resource, lr:LocationResource) -> float:
    adjustment = random()
    try:
        return float((lr.base_value or r.base_value) * ( 1 + (lr.variance or r.variance) * (adjustment * 2 - 1) ))
    except:
        return float(r.base_value * ( 1 + r.variance * (adjustment * 2 - 1) ))

def new_travel(request):
    new_location_id = request.POST.get('change_location_select')
    if new_location_id is not None:
        party: Party = Party.objects.get(id=1)
        new_location = Location.objects.get(id=new_location_id)
        request = party.travel_to(request, new_location)

        # print('the travel function is calling to add history')
        # TravelHistory.objects.add_history(party, new_location)

        # print(f'BEFORE CHECK -> party.location: {party.location.name} | party.journey_count: {party.journey_count}')
        # setattr(party, 'location', new_location)
        # setattr(party, 'journey_count', party.journey_count + 1)
        # party.save()
        # print(f'AFTER CHECK -> party.location: {party.location.name} | party.journey_count: {party.journey_count}')

    return redirect('/party/travel/', request)

def undo_travel(request):
    """ Undo the last journey, returning the party to the previous location
        and reverting all of their trades between the last journey and now. """
    party = Party.objects.get(id=1)
    request = party.revert_travel(request)
    return redirect('/party/travel/', request)

def trade_deal(request):
    resource_id = request.POST.get('resource_select') and int(request.POST.get('resource_select'))
    resource = Resource.objects.get(id=resource_id)
    b_amt = (request.POST.get('resource_buy_amount') and int(request.POST.get('resource_buy_amount'))) or 0
    s_amt = (request.POST.get('resource_sell_amount') and int(request.POST.get('resource_sell_amount'))) or 0
    buy_amt: float

    if resource and (b_amt or s_amt):
        buy_amt = b_amt - s_amt
        if buy_amt == 0:
            return redirect('/party/travel/', request)
        party: Party = Party.objects.get(id=1)
        local_resources, inventory, local_specialities = get_stocks(party)

        request = party.trade(request, resource, buy_amt, local_resources)
    else:
        messages.error(request, 'Resource or buy and sell amounts were missing.')

    return redirect('/party/travel/', request)

def undo_trade(request):
    """ Revert the party gold and inventory by refunding or restoring the last traded quantities. """
    party: Party = Party.objects.get(id=1)
    request = party.revert_trade(request)
    return redirect('/party/travel/', request)

def history_page(request):
    party = Party.objects.first()
    history: dict[int, object] = {}
    with connection.cursor() as cursor:
        # get the travel history
        cursor.execute(f"""
            SELECT
                travel.id AS travel_id,
                loc.name AS location,
                res.name AS resource,
                trade.quantity_gained AS quantity,
                trade.gold_gained AS gold
            FROM locations_location AS loc
            LEFT join party_travelhistory AS travel ON loc.id=travel.location_id
            LEFT join party_tradehistory AS trade ON travel.id=trade.location_hist_id
            LEFT join locations_resource AS res ON trade.resource_id=res.id
            WHERE travel.party_id={party.id}
            ORDER BY travel.id DESC;
        """)
        history = dictfetchall(cursor)
    context = {
        'title': 'Party History',
        'history': history,
    }
    return render(request, 'history.html', context)
