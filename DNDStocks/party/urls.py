from django.urls import path
from . import views

urlpatterns = [
    path('', views.party_page, name='party_page'),
    path('travel/', views.travel_page, name='travel_page'),
    path('travel/to/', views.new_travel, name='new_travel'),
    path('travel/undo/', views.undo_travel, name='undo_travel'),
    path('trade/deal/', views.trade_deal, name='trade_deal'),
    path('trade/undo/', views.undo_trade, name='undo_trade'),
    path('trade/history/', views.trade_history, name='trade_history'),
]
