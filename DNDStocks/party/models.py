from django.db import models
from django.db.models.deletion import DO_NOTHING

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
    members = models.ManyToManyField(to='Character', related_name='party',)
    location = models.ForeignKey(to='locations.Location', on_delete=DO_NOTHING)
    journey_count = models.IntegerField(default=1)
    gold = models.FloatField(default=0)
    objects = PartyManager()

class Inventory(models.Model):
    party = models.ForeignKey(Party, on_delete=DO_NOTHING)

# Player Character model
class Character(Article):
    foo = None
