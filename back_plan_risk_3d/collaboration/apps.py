"""Configuración de la aplicación collaboration."""
from django.apps import AppConfig


class CollaborationConfig(AppConfig):
    """Configuración de la app de colaboración en tiempo real."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collaboration'
    verbose_name = 'Colaboración en Tiempo Real'
