from django.urls import path
from . import views

urlpatterns = [
    path('', views.locations_page, name='locations_page'),
]
