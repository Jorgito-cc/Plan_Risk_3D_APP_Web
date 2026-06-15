
"""Vistas para el módulo users."""
import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count, Q
from django.utils import timezone
from users.models import Usuario, PlanConfig
from plans.models import Plan3DJob
from .auth import JWTAuthentication
from .serializers import RegistroSerializer, UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Hashear password antes de crear usuario."""
        password = serializer.validated_data.get("password")
        if password:
            serializer.validated_data["password"] = make_password(password)
        serializer.save()

    def perform_update(self, serializer):
        """Hashear password antes de actualizar usuario."""
        password = serializer.validated_data.get("password")
        if password:
            serializer.validated_data["password"] = make_password(password)
        serializer.save()


class RegistroView(generics.CreateAPIView):
    """Vista para registro de nuevos usuarios."""

    queryset = Usuario.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Crear nuevo usuario."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                UsuarioSerializer(usuario).data,
                status=status.HTTP_201_CREATED
            )
        print("❌ ERRORES DE SERIALIZER:", serializer.errors)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """Vista para inicio de sesión con JWT."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Autenticar usuario y generar tokens JWT."""
        email = request.data.get("email")
        password = request.data.get("password")

        # Asegurar existencia del Administrador por defecto
        if email == "support@planrisk3d.com":
            admin_exists = Usuario.objects.filter(email=email).exists()
            if not admin_exists and password == "12345678":
                Usuario.objects.create(
                    nombre="Administrador",
                    email=email,
                    password=make_password(password),
                    rol="Administrador"
                )

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, usuario.password):
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = generar_tokens(usuario)

        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "usuario": UsuarioSerializer(usuario).data
        })


class LogoutView(APIView):
    """Vista para cerrar sesión."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cerrar sesión del usuario."""
        return Response(
            {"message": "Sesión cerrada, borra tu token localmente"},
            status=205
        )


def generar_tokens(usuario):
    """
    Generar tokens JWT para un usuario.

    Args:
        usuario: Instancia de Usuario

    Returns:
        Dict con tokens refresh y access
    """
    refresh = RefreshToken()
    refresh['usuario_id'] = usuario.id
    refresh['rol'] = usuario.rol
    access = refresh.access_token
    access.set_exp(lifetime=timedelta(hours=24))
    return {
        "refresh": str(refresh),
        "access": str(access)
    }


@api_view(['PUT'])
def update_usuario(request, pk):
    """
    Actualizar usuario existente.

    Args:
        request: Request con datos a actualizar
        pk: ID del usuario

    Returns:
        Response con usuario actualizado o error
    """
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UsuarioSerializer(
        usuario,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlanConfigView(APIView):
    """Vista para gestionar precios dinámicos de los planes."""
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        configs = PlanConfig.objects.all()
        data = {c.rol: c.precio_mensual for c in configs}
        
        # Valores por defecto si la tabla está vacía
        if 'usuario_estrella' not in data:
            data['usuario_estrella'] = 180.00
        if 'usuario_premium' not in data:
            data['usuario_premium'] = 220.00
            
        return Response(data)

    def post(self, request):
        precios = request.data
        for rol, precio in precios.items():
            PlanConfig.objects.update_or_create(
                rol=rol,
                defaults={'precio_mensual': precio}
            )
        return Response({"message": "Precios actualizados exitosamente"})

class DashboardKPIsView(APIView):
    """Vista para obtener KPIs del Dashboard Administrativo."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        hace_30_dias = now - timedelta(days=30)
        hace_15_dias_futuro = now + timedelta(days=15)

        # 1. KPIs de Rendimiento y Uso
        total_planos = Plan3DJob.objects.count()
        planos_mes = Plan3DJob.objects.filter(created_at__gte=hace_30_dias).count()
        
        usuarios_activos_qs = Plan3DJob.objects.filter(created_at__gte=hace_30_dias).values('usuario').distinct()
        usuarios_activos = usuarios_activos_qs.count()
        total_usuarios = Usuario.objects.count()
        
        porcentaje_usuarios_activos = round((usuarios_activos / total_usuarios) * 100, 2) if total_usuarios > 0 else 0
        promedio_planos_usuario = round((total_planos / total_usuarios), 2) if total_usuarios > 0 else 0

        # 2. KPIs de Suscripciones y Finanzas
        usuarios_premium = Usuario.objects.filter(rol='usuario_premium').count()
        usuarios_estrella = Usuario.objects.filter(rol='usuario_estrella').count()
        
        tasa_conversion = round(((usuarios_premium + usuarios_estrella) / total_usuarios) * 100, 2) if total_usuarios > 0 else 0
        
        # Precios dinámicos desde PlanConfig
        precio_premium = PlanConfig.objects.filter(rol='usuario_premium').first()
        val_premium = float(precio_premium.precio_mensual) if precio_premium else 220.00
        
        precio_estrella = PlanConfig.objects.filter(rol='usuario_estrella').first()
        val_estrella = float(precio_estrella.precio_mensual) if precio_estrella else 180.00

        mrr = (usuarios_premium * val_premium) + (usuarios_estrella * val_estrella)
        
        # Usuarios por expirar en los próximos 15 días
        usuarios_expirar = Usuario.objects.filter(
            fecha_expiracion_plan__gte=now.date(),
            fecha_expiracion_plan__lte=hace_15_dias_futuro.date()
        ).count()

        # 3. KPIs Demográficos
        estudiantes = Usuario.objects.filter(profesion='estudiante').count()
        profesionales = Usuario.objects.filter(profesion='profesional').count()
        otros_profesion = Usuario.objects.filter(profesion='otro').count()

        # 4. KPIs de Engagement
        usuarios_aceptaron_politicas = Usuario.objects.filter(acepta_politicas=True).count()
        tasa_aceptacion_politicas = round((usuarios_aceptaron_politicas / total_usuarios) * 100, 2) if total_usuarios > 0 else 0

        # --- DETALLES PARA EL DRILL-DOWN ---
        # 1. Detalles de Suscripciones
        suscripciones_qs = Usuario.objects.filter(rol__in=['usuario_premium', 'usuario_estrella']).values(
            'id', 'nombre', 'apellido', 'email', 'rol', 'fecha_expiracion_plan'
        )
        detalles_suscripciones = list(suscripciones_qs)
        
        # 2. Detalles de Planos Recientes (últimos 10)
        planos_recientes_qs = Plan3DJob.objects.select_related('usuario').order_by('-created_at')[:10]
        detalles_planos = [
            {
                "id": p.id,
                "usuario_nombre": f"{p.usuario.nombre} {p.usuario.apellido}" if p.usuario else "Desconocido",
                "usuario_email": p.usuario.email if p.usuario else "",
                "created_at": p.created_at.strftime('%d/%m/%Y %H:%M') if p.created_at else "Sin fecha",
                "status": "completed" if p.glb_model else "processing"
            }
            for p in planos_recientes_qs
        ]
        
        # 3. Usuarios Normales (Gratis)
        usuarios_normales = Usuario.objects.filter(rol='usuario_normal').count()

        return Response({
            "rendimiento": {
                "total_planos": total_planos,
                "planos_ultimo_mes": planos_mes,
                "usuarios_activos": usuarios_activos,
                "porcentaje_usuarios_activos": porcentaje_usuarios_activos,
                "promedio_planos_usuario": promedio_planos_usuario
            },
            "finanzas": {
                "tasa_conversion": tasa_conversion,
                "mrr": mrr,
                "usuarios_por_expirar": usuarios_expirar,
                "total_premium": usuarios_premium,
                "total_estrella": usuarios_estrella
            },
            "demografia": {
                "estudiantes": estudiantes,
                "profesionales": profesionales,
                "otros": otros_profesion
            },
            "engagement": {
                "tasa_aceptacion_politicas": tasa_aceptacion_politicas
            },
            "detalles": {
                "usuarios_normales": usuarios_normales,
                "suscripciones": detalles_suscripciones,
                "planos_recientes": detalles_planos,
                "precios_actuales": {
                    "usuario_premium": val_premium,
                    "usuario_estrella": val_estrella
                }
            }
        })

class AdminHistorialPlanosView(APIView):
    """Vista para obtener el historial completo de planos para el administrador."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        planos_qs = Plan3DJob.objects.select_related('usuario').order_by('-created_at')
        
        detalles_planos = []
        for p in planos_qs:
            estado = "processing"
            if p.glb_model:
                estado = "completed"
            elif getattr(p, 'blockchain_tx', None):
                estado = "completed"
                
            detalles_planos.append({
                "id": p.id,
                "usuario_nombre": p.usuario.nombre if p.usuario else "Desconocido",
                "usuario_apellido": p.usuario.apellido if p.usuario else "",
                "usuario_email": p.usuario.email if p.usuario else "Sin correo",
                "fecha": p.created_at.strftime('%d/%m/%Y %H:%M') if p.created_at else "Sin fecha",
                "estado": estado,
                "glb_url": p.glb_model.url if p.glb_model and getattr(p.glb_model, 'name', None) else None
            })
            
        return Response(detalles_planos)
