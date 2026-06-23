"""Serializadores para la app de colaboración."""
from rest_framework import serializers
from .models import SalaColaborativa


class SalaColaborativaSerializer(serializers.ModelSerializer):
    """Serializador para crear y listar salas colaborativas."""

    class Meta:
        model = SalaColaborativa
        fields = ['id', 'token', 'proyecto', 'creador', 'activa', 'created_at']
        read_only_fields = ['id', 'token', 'creador', 'created_at']
