from typing import Any, Tuple
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
    party = Party.objects.get(id=1)
    current_location = party.location
    all_locations = {current_location, *list(Location.objects.all())} # <--- KEEP AN EYE ON THIS
    all_resources = Resource.objects.all()

    # Add party travel location if needed
    history = party.travel_history_set.order_by('-id')
    if history is None or current_location != history.first():
        try:
            TravelHistory.objects.add_history(party, current_location, history.filter(location=current_location).visit_count + 1)
        except:
            TravelHistory.objects.add_history(party, current_location, 1)

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
        inventory.append([r.id, r.name, r_set.quantity, r.base_value])
        if lr is not None:
            local_specialities.append(r.id)
            tender_probability = lr.probability or 0.95
        else:
            tender_probability = 0.95

        if random() < tender_probability:
            price = get_price(r, lr)
            local_resources.append([
                r.id,
                r.name,
                price * 1.15,
                price * 0.9,
            ])

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
        party = Party.objects.get(id=1)
        new_location = Location.objects.get(id=new_location_id)
        try:
            visit_count = party.travel_history_set.filter(location_id=new_location_id).order_by('-id').first().visit_count
        except:
            visit_count = 1

        TravelHistory.objects.add_history(party, new_location, visit_count)

        setattr(party, 'location', new_location)
        setattr(party, 'journey_count', party.journey_count + 1)
        party.save()

    return redirect('/party/travel/')

def undo_travel(request):
    """ Undo the last journey, returning the party to the previous location
        and reverting all of their trades between the last journey and now. """
    party = Party.objects.get(id=1)
    request = party.revert_journey(request)

    return redirect('/party/travel/', request)

def trade_deal(request):
    resource_id = request.POST.get('resource_select') and int(request.POST.get('resource_select'))
    resource = Resource.objects.get(id=resource_id)
    buy_amt = (request.POST.get('resource_buy_amount') and int(request.POST.get('resource_buy_amount'))) or 0
    sell_amt = (request.POST.get('resource_sell_amount') and int(request.POST.get('resource_sell_amount'))) or 0
    trade_amt: float

    if resource_id and (buy_amt or sell_amt):
        trade_amt = buy_amt - sell_amt
        if trade_amt == 0:
            return redirect('/party/travel/', request)
        party: Party = Party.objects.get(id=1)
        local_resources, inventory, local_specialities = get_stocks(party)

        party.trade(resource, trade_amt, local_resources)

    return redirect('/party/travel/', request)

def undo_trade(request):
    """ Revert the party gold and inventory by refunding or restoring the last traded quantities. """
    party: Party = Party.objects.get(id=1)
    request = party.revert_trade(request)
    return redirect('/party/travel/', request)

def history_page(request):
    party = Party.objects.first()
    history = None
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT
                trade.id,
                l.name AS 'location',
                r.name AS 'resource',
                trade.quantity_gained AS 'quantity',
                trade.money_spent AS 'gold'
            FROM party_tradehistory AS trade, locations_location AS l, locations_resource AS r
            LEFT JOIN party_travelhistory AS travel ON trade.location_hist_id=travel.id
            WHERE travel.party_id={party.id} AND l.id=travel.location_id AND r.id=trade.resource_id
            ORDER BY trade.id desc""")
        history = dictfetchall(cursor)
        print(history)
    context = {
        'title': 'Party History',
        'history': history,
    }
    return render(request, 'history.html', context)
