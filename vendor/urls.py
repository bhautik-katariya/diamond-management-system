from django.urls import path
from .views import *

# app_name = 'vendor'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('add_diamond/', add_diamond, name='add_diamond'),
    path('edit_diamond/<int:sr_no>/', edit_diamond, name='edit_diamond'), 
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('load_diamonds/', load_diamonds, name='load_diamonds'),
    path('delete_diamond/<int:sr_no>/', delete_diamond, name='delete_diamond'),
]
