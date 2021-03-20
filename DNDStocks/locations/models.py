from django.db import models

# Create your models here.
class LocationManager(models.Manager):
    def create_location(name):
        location = self.create(
            name = name,
        )
