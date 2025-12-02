from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/detect/", consumers.YOLODetectionConsumer.as_asgi()),  # type: ignore
]