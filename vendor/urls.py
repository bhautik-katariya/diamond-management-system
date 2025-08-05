from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('add_diamond/', add_diamond, name='add_diamond'),
    path('edit_diamond/<int:sr_no>/', edit_diamond, name='edit_diamond'),
    path('load_diamonds/', load_diamonds, name='load_diamonds'),
    path('delete_diamond/<int:sr_no>/', delete_diamond, name='delete_diamond'),
]
