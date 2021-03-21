from django.db import models
from party.models import Article

from random import seed, random

# Location model
# Has a many to many table with resources
class Location(Article):
    foo = None

# Resource model
class ResourceManager(models.Manager):
    def create_resource(self, name, base_value, variance):
        resource = self.create(
            name = name,
            base_value = base_value,
            variance = variance,
        )
        return resource
class Resource(models.Model):
    name = models.CharField(unique=True, max_length=50)
    base_value = models.FloatField()
    variance = models.FloatField()
    objects = ResourceManager()
