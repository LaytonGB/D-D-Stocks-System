from django.db import models

# Create your models here.
class LocationManager(models.Manager):
    def create_location(name):
        location = self.create(
            name = name,
        )
        return location
class Location(models.Model):
    name = models.CharField(unique=True, max_length=50)
    def __str__(self):
        return f'{self.name.capitalize()}'
    objects = LocationManager()
