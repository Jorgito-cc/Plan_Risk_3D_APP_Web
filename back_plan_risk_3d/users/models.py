"""Modelos para el módulo users."""
from django.db import models


class Usuario(models.Model):
    """Modelo de usuario con roles y suscripciones."""

    ROLES = (
        ('usuario_normal', 'Usuario Normal'),
        ('usuario_premium', 'Usuario Premium'),
        ('usuario_estrella', 'Usuario Estrella'),
        ('Administrador', 'Administrador'),
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='usuario_normal'
    )
    profesion = models.CharField(
        max_length=20,
        choices=(
            ('estudiante', 'Estudiante'),
            ('profesional', 'Profesional'),
            ('otro', 'Otro'),
        ),
        default='estudiante',
        null=True,
        blank=True
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_expiracion_plan = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(null=True, blank=True)
    telefono = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    acepta_politicas = models.BooleanField(default=False)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """Representación en string del modelo."""
        return f"{self.nombre} - {self.rol}"

    @property
    def is_authenticated(self):
        """Indica si el usuario está autenticado."""
        return True

    @property
    def is_active(self):
        """Indica si el usuario está activo."""
        return True

    def get_username(self):
        """Retorna el email como nombre de usuario."""
        return self.email

class PlanConfig(models.Model):
    """Modelo para configurar dinámicamente los precios de los planes."""
    rol = models.CharField(max_length=20, unique=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.rol}: Bs. {self.precio_mensual}"