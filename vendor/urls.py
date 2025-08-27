from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('add-diamond/', add_diamond, name='add_diamond'),
    path('add-multiple-diamonds/', add_multiple_diamonds, name='add_multiple_diamonds'),
    path('import-diamonds-from_api/', import_diamonds_from_api, name='import_diamonds_from_api'),
    path('edit-diamond/<int:id>/', edit_diamond, name='edit_diamond'),
    # path('update-multiple-diamonds/', update_multiple_diamonds, name='update_multiple_diamonds'),
    path('load-diamonds/', load_diamonds, name='load_diamonds'),
    path('delete-diamond/<int:id>/', delete_diamond, name='delete_diamond'),
    path('orders/', view_orders, name='view_orders'),
    path("pending-orders-count/", pending_orders_count, name="pending_orders_count"),
    path("orders/<int:order_id>/process/", process_order, name="process_order"),
]
