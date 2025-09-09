"""
URL configuration for diamond_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),              # allauth routes
    path("oauth/google/customer/", google_customer_start, name="google_customer_start"),
    path("oauth/google/vendor/", google_vendor_start, name="google_vendor_start"),
    path("post_google_login/", post_google_login, name="post_google_login"),
    path('', dashboard, name='dashboard'),
    path('diamond-detail/<int:id>', diamond_detail, name='diamond_detail'),
    path('customer/', include(('customer.urls', 'customer'), namespace='customer')),
    path('vendor/', include(('vendor.urls', 'vendor'), namespace='vendor')),
    path('login/', login, name='login'),
    path('vendor-login/', vendor_login, name='vendor_login'),
    path('register/', register, name='register'),
    path('vendor-register/', vendor_register, name='vendor_register'),
    path('logout/', logout, name='logout'),
    path('profile/', edit_profile, name='edit_profile'),
    path('download-diamonds/', download_diamonds_excel, name='diamond_download_excel'),
    path('admin-logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='admin_logout'),
]
