from django.contrib import admin
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.account_page, name='account_page'),
    path('login/', views.login_page, name='login_page'),
]
