from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('add_diamond/', add_diamond, name='add_diamond'),
    path('add_multiple_diamonds/', add_multiple_diamonds, name='add_multiple_diamonds'),
    path('import_diamonds_from_api/', import_diamonds_from_api, name='import_diamonds_from_api'),
    path('edit_diamond/<int:id>/', edit_diamond, name='edit_diamond'),
    path('update_multiple_diamonds/', update_multiple_diamonds, name='update_multiple_diamonds'),
    path('load_diamonds/', load_diamonds, name='load_diamonds'),
    path('delete_diamond/<int:id>/', delete_diamond, name='delete_diamond'),
    path('orders/', view_orders, name='view_orders'),
]
