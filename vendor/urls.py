from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('add-diamond/', add_diamond, name='add_diamond'),
    path('add-multiple-diamonds/', add_multiple_diamonds, name='add_multiple_diamonds'),
    path('import-diamonds-from_api/', import_diamonds_from_api, name='import_diamonds_from_api'),
    path('edit-diamond/<int:id>/', edit_diamond, name='edit_diamond'),
    path('load-diamonds/', load_diamonds, name='load_diamonds'),
    path('delete-diamond/<int:id>/', delete_diamond, name='delete_diamond'),
    path('orders/', view_orders, name='view_orders'),
    path('process-order-item/<int:item_id>/', process_order_item, name='process_order_item'),
]
