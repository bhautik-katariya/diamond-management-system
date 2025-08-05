from django.urls import path
from .views import *

app_name = 'customer'

urlpatterns = [
    path('add-to-cart/<int:diamond_id>/', add_to_cart, name='add_to_cart'),
]