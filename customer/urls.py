from django.urls import path
from .views import *

# app_name = 'customer'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('diamond/<int:sr_no>/', diamond_detail, name='diamond_detail'),
]