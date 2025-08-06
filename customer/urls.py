from django.urls import path
from .views import *

app_name = 'customer'

urlpatterns = [
    path('add-to-cart/<int:diamond_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
]