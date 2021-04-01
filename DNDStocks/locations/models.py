from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING

from party.models import Article

from random import seed, random

# Location model
# Has a many to many table with Resource
class Location(Article):
    resources = models.ManyToManyField("Resource", related_name="custom_resources", through="LocationResource")

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
    probability = models.FloatField(null=True, default=None)
    objects = ResourceManager()

# Custom location resources model
class LocationResourceManager(models.Manager):
    def create_resource(self, location:Location, resource:Resource, is_speciality:bool=False, base_value:float=None, variance:float=None, probability:float=None):
        return self.create(
            location = location,
            resource = resource,
            is_speciality = is_speciality,
            base_value = base_value,
            variance = variance,
            probability = probability,
        )
class LocationResource(models.Model):
    location = models.ForeignKey("Location", on_delete=CASCADE)
    resource = models.ForeignKey("Resource", on_delete=CASCADE)
    is_speciality = models.BooleanField(default=False)
    base_value = models.FloatField(null=True, default=None)
    variance = models.FloatField(null=True, default=None)
    probability = models.FloatField(null=True, default=None)
    objects = LocationResourceManager()
