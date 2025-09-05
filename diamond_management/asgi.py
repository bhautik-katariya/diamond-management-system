"""
ASGI config for diamond_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import diamond_management.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diamond_management.settings')

# Initialize Django ASGI app first to ensure Django setup
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            diamond_management.routing.websocket_urlpatterns
        )
    ),
})

