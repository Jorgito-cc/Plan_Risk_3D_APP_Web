"""Rutas WebSocket para la app de colaboración."""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/editor/(?P<room_token>[0-9a-f-]+)/$',
        consumers.EditorConsumer.as_asgi()
    ),
]
