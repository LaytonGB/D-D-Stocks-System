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
    history = models.ManyToManyField('locations.Location', related_name='history', through='History')
    objects = PartyManager()

class Inventory(models.Model):
    party = models.ForeignKey(Party, related_name='resource_set', on_delete=CASCADE)
    resource = models.ForeignKey('locations.Resource', on_delete=DO_NOTHING)
    quantity = models.FloatField(default=0)

class HistoryManager(models.Manager):
    def add_history(self, party, location, count):
        history = self.create(
            party = party,
            location = location,
            visit_count = count,
        )
        return history
class History(models.Model):
    party = models.ForeignKey(Party, related_name='history_set', on_delete=CASCADE)
    location = models.ForeignKey('locations.Location', related_name='party_history_set', on_delete=DO_NOTHING)
    visit_count = models.IntegerField(default=1)
    objects = HistoryManager()

# Player Character model
class Character(Article):
    foo = None
