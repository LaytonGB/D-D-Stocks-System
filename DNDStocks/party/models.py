from django.contrib import messages
from django.db import models
from django.db.models import Sum
from django.db.models.aggregates import Max
from django.db.models.deletion import CASCADE, DO_NOTHING

class ArticleManager(models.Manager):
    def create_article(self, name):
        article = self.create(
            name = name,
        )
        return article
class Article(models.Model):
    name = models.CharField(unique=True, max_length=50)
    class Meta:
        abstract = True
    objects = ArticleManager()

# Party model
class PartyManager(models.Manager):
    def create_party(self, location, journey_count=1, gold=0):
        party = self.create(
            location = location,
            journey_count = journey_count,
            gold = gold,
        )
        return party
class Party(models.Model):
    members = models.ManyToManyField('Character', related_name='party',)
    location = models.ForeignKey('locations.Location', on_delete=DO_NOTHING)
    journey_count = models.IntegerField(default=1)
    gold = models.FloatField(default=0)
    inventory = models.ManyToManyField('locations.Resource', through='Inventory')
    travel_history = models.ManyToManyField('locations.Location', related_name='history', through='TravelHistory')
    class Meta:
        ordering = ['-id']
    objects = PartyManager()

    def weight(self):
        return ( f'{self.resource_set.aggregate(total_weight=Sum("quantity"))["total_weight"]} lbs' )
    def get_resource(self, r):
        """ Returns the inventory entry for the resource instance for this party, or creates
            the entry if one does not exist. """
        try:
            i = self.resource_set.get(resource_id=r.id)
        except:
            if r is None:
                return
            i = self.inventory.add(r)
        return i
    def trade(self, request, resource, buy_amt: float, local_resources: list): # TODO add error messages
        """ Perform a trade and add the trade to trade history. """
        # gather variables
        cost = buy_amt * next(r for r in local_resources if r[0] == resource.id)[2]
        inv: Inventory = self.get_resource(resource)
        # check limits
        if self.gold >= cost and inv.quantity >= -buy_amt:
            # adjust gold
            setattr(self, 'gold', self.gold - cost)
            self.save()
            # adjust resources
            setattr(inv, 'quantity', inv.quantity + buy_amt)
            inv.save()
            # add history
            self.trade_history_set.add_history(self, resource, cost, buy_amt)
        else:
            messages.error(request, 'Transaction failed: Gold or Resources were insufficient.')
        return request
    def revert_trade(self, request, count=1):
        """ Revert one or more trade deals. Returns the number of trade deals successfully reverted. """
        print(f'Reverting trade...')
        trade_history = self.trade_history_set.order_by('-id')
        for n in range(1, count + 1):
            print(f'Trade {n}:')
            last_trade: TradeHistory = trade_history.first()

            print(f'Trade Hist: {trade_history} | Last Trade: {last_trade} | Self Location: {self.location} | Last Trade Location: {last_trade.location}')
            if trade_history is not None and last_trade is not None:
                inv_res: Inventory = self.get_resource(last_trade.resource) # the specific inventory row
                setattr(self, 'gold', self.gold + last_trade.money_spent) # refund or charge party gold
                self.save()
                setattr(inv_res, 'quantity', inv_res + last_trade.quantity_gained) # refund or charge party inventory
                inv_res.save()
                if self.location is not last_trade.location:
                    messages.warning(request, 'Current location did not match up with the location of last trade.')
                last_trade.delete() # delete the trade history entry
            else:
                if n == 1:
                    messages.error(request, 'Last trade could not be undone.')
                else:
                    messages.info(request, 'No trades were remaining, but it was requested that more be undone.')
        return request
    def travel_to(self, request, new_location):
        setattr(self, 'location', new_location)
        setattr(self, 'journey_count', self.journey_count + 1)
        self.save()
        self.travel_history_set.add_history(self)
        if self.travel_history_set.first().location != new_location:
            messages.error(request, f'Something went wrong when adding travel history.')
        return request
    def revert_travel(self, request, count=1):
        if self.journey_count > 1:
            all_trades = list(self.trade_history_set.order_by('-id'))
            loc_trades = []
            for t in all_trades:
                if t.location is self.location:
                    loc_trades.append(t)
                else:
                    break
            print(f'Attempting to revert the last {len(loc_trades)}')
            self.revert_trade(request, len(loc_trades)) # undo all trades at this location

            history = self.travel_history_set.order_by('-id')
            last_location = list(history)[1].location
            print(f'Reverting location to: {last_location.name}')
            self.location = last_location # revert location
            self.journey_count = self.journey_count - 1 # revert journey count
            history.first().delete() # delete history entry
        return

class Inventory(models.Model):
    party = models.ForeignKey(Party, related_name='resource_set', on_delete=CASCADE)
    resource = models.ForeignKey('locations.Resource', on_delete=DO_NOTHING)
    quantity = models.FloatField(default=0)

class TravelHistoryManager(models.Manager):
    def add_history(self, party):
        print('adding travel history')
        old_visit_count: int
        try:
            old_visit_count = party.travel_history_set.filter(location_id=party.location_id).order_by('-id').first().visit_count
        except:
            old_visit_count = 0
        history = self.create(
            party = party,
            location = party.location,
            visit_count = old_visit_count + 1,
        )
        return history
class TravelHistory(models.Model):
    party = models.ForeignKey(Party, related_name='travel_history_set', on_delete=CASCADE)
    location = models.ForeignKey('locations.Location', related_name='travel_history_set', on_delete=DO_NOTHING)
    visit_count = models.IntegerField(default=1)
    class Meta:
        ordering = ['-id']
    objects = TravelHistoryManager()

class TradeHistoryManager(models.Manager):
    def add_history(self, party, resource, money_spent, quantity_gained):
        print('history creation reached')
        hist: TravelHistory = party.travel_history_set.first() or party.travel_history_set.add_history(party)
        if hist.location.id != party.location.id:
            hist = party.travel_history_set.add_history(party)
        return self.create(
            party = party,
            location_hist = hist,
            resource = resource,
            money_spent = money_spent,
            quantity_gained = quantity_gained,
        )
class TradeHistory(models.Model):
    party = models.ForeignKey(Party, related_name='trade_history_set', on_delete=DO_NOTHING)
    location_hist = models.ForeignKey("TravelHistory", related_name='trade_history_set', on_delete=models.CASCADE, null=True)
    resource = models.ForeignKey("locations.Resource", on_delete=DO_NOTHING)
    money_spent = models.FloatField(null=True)
    quantity_gained = models.IntegerField(null=True)
    objects = TradeHistoryManager()

# Player Character model
class Character(Article):
    foo = None
