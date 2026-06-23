"""Modelos para el módulo de colaboración en tiempo real."""
import uuid
from django.db import models


class SalaColaborativa(models.Model):
    """
    Sala de colaboración vinculada a un proyecto 3D (Plan3DJob).

    Cada sala tiene un token UUID único que se comparte por enlace.
    Múltiples usuarios pueden unirse a la sala vía WebSocket para
    sincronizar movimientos de piezas en tiempo real.
    """

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    proyecto = models.ForeignKey(
        'plans.Plan3DJob',
        on_delete=models.CASCADE,
        related_name='salas_colaborativas'
    )
    creador = models.ForeignKey(
        'users.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salas_creadas'
    )
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sala Colaborativa'
        verbose_name_plural = 'Salas Colaborativas'
        ordering = ['-created_at']

    def __str__(self):
        return f'Sala {self.token} - Proyecto #{self.proyecto_id}'


class HistorialMovimiento(models.Model):
    """
    Historial de movimientos de piezas 3D dentro de una sala.

    Se guarda al soltar la pieza (onDragEnd) para no saturar la BD.
    """

    sala = models.ForeignKey(
        SalaColaborativa,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    usuario = models.ForeignKey(
        'users.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pieza_id = models.CharField(max_length=200)
    posicion_x = models.FloatField()
    posicion_y = models.FloatField()
    posicion_z = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de Movimiento'
        verbose_name_plural = 'Historiales de Movimiento'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.pieza_id} → ({self.posicion_x}, {self.posicion_y}, {self.posicion_z})'
