from django.shortcuts import redirect, render

from .models import Party, Inventory, History
from locations.models import Location, Resource

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
    history = party.history_set
    if history is None or current_location.id != history.all().order_by('-id').first().location_id:
        try:
            History.objects.add_history(party, current_location, history.filter(party_id=party.id).filter(location_id=current_location.id).visit_count + 1)
        except:
            History.objects.add_history(party, current_location, 1)

    # Add party resources to inventory table if needed
    for r in all_resources:
        try:
            party.inventory.get(resource_id=r.id)
        except:
            party.inventory.add(r)

    # Trading calc and party inventory
    local_resources, inventory = get_stocks(party)

    context = {
        'title': 'Travel Page',
        'party': party,
        'inventory': inventory,
        'current_location': current_location,
        'all_locations': all_locations,
        'local_resources': local_resources,
    }

    return render(request, 'travel.html', context)

def get_stocks(party):
    seed(party.journey_count)
    all_resources = Resource.objects.all()
    local_resources = []
    inventory = []
    for r in all_resources:
        r_set = party.resource_set.filter(resource_id=r.id).first()
        inventory.append([r.id, r.name, r_set.quantity, r.base_value])
        if random() >= 0.05:
            adjustment = random()
            price = r.base_value * ( 1 + r.variance * (adjustment * 2 - 1) )
            local_resources.append([
                r.id,
                r.name,
                price * 1.1,
                price * 0.9,
            ])
    return local_resources, inventory

def new_travel(request):
    new_location_id = request.POST.get('change_location_select')
    if new_location_id is not None:
        party = Party.objects.get(id=1)
        new_location = Location.objects.get(id=new_location_id)
        try:
            visit_count = party.history_set.filter(location_id=new_location_id).order_by('-id').first().visit_count
        except:
            visit_count = 1

        History.objects.add_history(party, new_location, visit_count)

        setattr(party, 'location', new_location)
        setattr(party, 'journey_count', party.journey_count + 1)
        party.save()

    return redirect('/party/travel/')

def undo_travel(request):
    party = Party.objects.get(id=1)

    if party.journey_count > 1:
        history = History.objects.filter(party_id=party.id).order_by('-id')
        last_location_id = list(history)[1].location_id
        last_location = Location.objects.get(id=last_location_id)

        setattr(party, 'location', last_location)
        setattr(party, 'journey_count', party.journey_count - 1)
        party.save()

        history.first().delete()

    return redirect('/party/travel/', request)

def trade_deal(request):
    resource = request.POST.get('resource_select') and int(request.POST.get('resource_select'))
    buy_amt = request.POST.get('resource_buy_amount') and int(request.POST.get('resource_buy_amount'))
    sell_amt = request.POST.get('resource_sell_amount') and int(request.POST.get('resource_sell_amount'))
    print(f'resource_id:{resource} | buy_amt:{buy_amt} | sell_amt:{sell_amt}')

    if resource and (buy_amt or sell_amt):
        if buy_amt and sell_amt:
            x = buy_amt - sell_amt
            if x == 0:
                return redirect('/party/travel/', request)
            elif x > 0:
                buy_amt = x
                sell_amt = None
            else:
                sell_amt = x
                buy_amt = None

        party = Party.objects.get(id=1)
        local_resources, inventory = get_stocks(party)

        if buy_amt:
            print('buying')
            # if party has gold, perform trade
            cost = buy_amt * next(r for r in local_resources if r[0] == resource)[2]
            if party.gold >= cost:
                try: # get inventory entry
                    inv = party.resource_set.get(resource_id=resource)
                except: # create inventory entry if it didn't exist
                    res = Resource.objects.get(id=resource)
                    party.inventory.add(resource)
                    inv = party.resource_set.get(resource_id=resource)

                setattr(party, 'gold', party.gold - cost)
                party.save()
                setattr(inv, 'quantity', inv.quantity + buy_amt) # adjust
                inv.save()
                print('bought')

        elif sell_amt:
            # if party has resources, perform trade
            profit = sell_amt * next(r for r in local_resources if r[0] == resource)[3]
            try:
                inv = party.resource_set.get(resource_id=resource)
                if inv and inv.quantity >= sell_amt:
                    setattr(inv, 'quantity', inv.quantity - sell_amt)
                    inv.save()
                    setattr(party, 'gold', party.gold + profit)
                    party.save()

            except:
                pass

    return redirect('/party/travel/', request)
