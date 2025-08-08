from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import *

# Register your models here.

admin.site.site_title = "Admin"
admin.site.site_header = "Diamond System"
admin.site.index_title = "Diamond System Administration"
admin.site.site_url = '/'

admin.site.register(Vendor)
admin.site.register(Diamond)
admin.site.register(Order)
admin.site.register(OrderItem)

