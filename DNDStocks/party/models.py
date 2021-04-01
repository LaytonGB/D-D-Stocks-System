from django.db import models
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
    objects = PartyManager()

class Inventory(models.Model):
    party = models.ForeignKey(Party, related_name='resource_set', on_delete=CASCADE)
    resource = models.ForeignKey('locations.Resource', on_delete=DO_NOTHING)
    quantity = models.FloatField(default=0)

class TravelHistoryManager(models.Manager):
    def add_history(self, party, location, count):
        history = self.create(
            party = party,
            location = location,
            visit_count = count,
        )
        return history
class TravelHistory(models.Model):
    party = models.ForeignKey(Party, related_name='travel_history_set', on_delete=CASCADE)
    location = models.ForeignKey('locations.Location', related_name='travel_history_set', on_delete=DO_NOTHING)
    visit_count = models.IntegerField(default=1)
    objects = TravelHistoryManager()

class TradeHistoryManager(models.Manager):
    def add_history(self, party, location, resource, money_spent, quantity):
        return self.create(
            party = party,
            location = location,
            resource = resource,
            money_spent = money_spent,
            quantity = quantity,
        )
class TradeHistory(models.Model):
    party = models.ForeignKey('party.Party', related_name='trade_history_set', on_delete=DO_NOTHING)
    location = models.ForeignKey('locations.Location', related_name='trade_history_set', on_delete=DO_NOTHING)
    resource = models.ForeignKey("locations.Resource", on_delete=DO_NOTHING)
    money_spent = models.FloatField(null=True)
    quantity = models.IntegerField(null=True)
    objects = TradeHistoryManager()

# Player Character model
class Character(Article):
    foo = None
