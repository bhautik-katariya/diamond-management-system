from django.urls import re_path
from vendor import consumers

websocket_urlpatterns = [
    re_path(r"ws/vendor/orders/(?P<vendor_id>\d+)/$", consumers.OrderConsumer.as_asgi()),
]
