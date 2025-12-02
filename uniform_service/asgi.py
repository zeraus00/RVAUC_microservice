"""
ASGI config for uniform_service project.
"""

import os
import django
from django.core.asgi import get_asgi_application

# 1. Set the settings module FIRST
# FIX: Use 'uniform_service.settings' as the module name is 'uniform_service'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uniform_service.settings")

# 2. Initialize Django. This must happen BEFORE importing detector.routing
# This step loads all settings and makes models accessible.
django.setup()

# 3. NOW it is safe to import channels and your routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import detector.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    
    "websocket": AuthMiddlewareStack(
        URLRouter(
            detector.routing.websocket_urlpatterns
        )
    ),
})