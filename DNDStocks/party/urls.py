from django.urls import path
from . import views

urlpatterns = [
    path('', views.party_page, name='party_page'),
    path('travel/', views.travel_page, name='travel_page'),
    path('travel/undo/', views.undo_travel, name='undo_travel'),
]
