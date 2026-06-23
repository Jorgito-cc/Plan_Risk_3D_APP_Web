"""Admin para la app de colaboración."""
from django.contrib import admin
from .models import SalaColaborativa, HistorialMovimiento

admin.site.register(SalaColaborativa)
admin.site.register(HistorialMovimiento)
