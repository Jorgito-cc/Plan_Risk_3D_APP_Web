
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
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()

            # Enviar correos de bienvenida, terminos y privacidad
            if usuario.email:
                subject = '¡Bienvenido a PlanRisk3D! 🚀'
                
                # HTML content con datos de la empresa, planes y funciones
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
                    <div style="background-color: #003366; padding: 20px; text-align: center; color: white;">
                        <h1>PlanRisk3D</h1>
                        <p>Plataforma de Generación de Modelos 3D y Gestión de Riesgos</p>
                    </div>
                    <div style="padding: 20px; color: #333;">
                        <h2>¡Hola {usuario.nombre}! Bienvenido a la familia</h2>
                        <p>Nos alegra mucho tenerte con nosotros. <strong>PlanRisk3D</strong> es una herramienta innovadora impulsada por Inteligencia Artificial que transforma planos 2D en modelos 3D interactivos, permitiendo una mejor visualización arquitectónica y evaluación de riesgos.</p>
                        
                        <h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 5px;">¿Qué puedes hacer en PlanRisk3D?</h3>
                        <ul>
                            <li>🏗️ <strong>Conversión Automática:</strong> Sube planos en 2D y obtén vistas en 3D en minutos.</li>
                            <li>🤖 <strong>Asistencia de IA:</strong> Analiza tus modelos con nuestro asistente virtual inteligente.</li>
                            <li>🔒 <strong>Seguridad Blockchain:</strong> Registra tus planos en la red de Ethereum (Sepolia) para inmutabilidad.</li>
                            <li>📱 <strong>Realidad Aumentada (AR):</strong> Visualiza tus modelos en el mundo real desde tu dispositivo móvil.</li>
                        </ul>

                        <h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 5px;">Nuestros Planes</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                            <tr style="background-color: #f4f4f4;">
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Gratuito</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">Acceso a herramientas básicas de visualización.</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Estrella</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">Modelos 3D avanzados + Registro en Blockchain + Texturas.</td>
                            </tr>
                            <tr style="background-color: #f4f4f4;">
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Premium</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">Acceso total ilimitado + Asistente IA Avanzado + AR Móvil.</td>
                            </tr>
                        </table>

                        <p style="margin-top: 30px; text-align: center;">
                            <a href="https://planrisk3d.com" style="background-color: #003366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Explorar PlanRisk3D</a>
                        </p>
                    </div>
                    <div style="background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; color: #777;">
                        © 2026 PlanRisk3D - Innovación en la Construcción.<br>
                        Si tienes preguntas, contáctanos a support@planrisk3d.com
                    </div>
                </div>
                """
                text_content = strip_tags(html_content)

                try:
                    # 1. ENVIAR CORREO DE BIENVENIDA
                    msg = EmailMultiAlternatives(
                        subject, 
                        text_content, 
                        settings.DEFAULT_FROM_EMAIL, 
                        [usuario.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                    print(f"[Email] Correo de bienvenida enviado a {usuario.email}")

                    # 2. ENVIAR CORREO DE TÉRMINOS Y CONDICIONES
                    subject_tc = 'Términos y Condiciones - PlanRisk3D 📜'
                    html_tc = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #111; border-radius: 10px; overflow: hidden; background-color: #0B132B; color: #E0E0E0;">
                        <div style="text-align: center; padding: 20px;">
                            <h1 style="color: #FFD700; margin-bottom: 5px;">Términos y Condiciones</h1>
                            <p style="color: #A0A0A0; font-size: 12px; margin-top: 0;">Última actualización: Junio 2026</p>
                            <hr style="border: 1px solid #FFD700; width: 50px; margin: 10px auto;">
                        </div>
                        <div style="padding: 20px; font-size: 14px; line-height: 1.6;">
                            <h3 style="color: #FFFFFF;">1. Aceptación de los Términos</h3>
                            <p>Al registrarse y utilizar los servicios de la plataforma <strong>Plan Risk 3D</strong>, usted acepta cumplir y estar sujeto a los siguientes términos y condiciones de servicio. Si no está de acuerdo con alguna parte de estos términos, no debe acceder al software.</p>

                            <h3 style="color: #FFFFFF;">2. Descripción del Servicio (Licencia SaaS)</h3>
                            <p>Plan Risk 3D es una plataforma de software en la nube bajo la modalidad SaaS (Software as a Service) que proporciona herramientas de modelado tridimensional de planos arquitectónicos y simulación de riesgos estructurales asistidos por Inteligencia Artificial (Mask R-CNN y Gemini). El usuario adquiere una licencia de acceso temporal según el plan seleccionado (Básico, Estrella o Premium) y no posee ningún derecho de propiedad sobre el código fuente, marcas o patentes del software.</p>

                            <div style="border: 1px solid #FFD700; border-radius: 8px; padding: 15px; margin: 20px 0; background-color: rgba(255, 215, 0, 0.05);">
                                <h3 style="color: #FFD700; margin-top: 0;">3. Limitación de Responsabilidad Técnica (Ingeniería Civil)</h3>
                                <p style="margin-bottom: 0;"><strong>IMPORTANTE:</strong> Todos los cálculos, predicciones de riesgos, modelos 3D y reportes generados por la Inteligencia Artificial de Plan Risk 3D son herramientas de asistencia técnica computacional preliminar y <strong>NO reemplazan el criterio profesional</strong> de un Ingeniero Civil o Ingeniero Estructural colegiado. La empresa no asume responsabilidad civil ni legal por daños directos o indirectos, fallas de construcción, colapsos estructurales o multas derivadas de la ejecución de obras basadas únicamente en los análisis proporcionados por esta plataforma.</p>
                            </div>

                            <h3 style="color: #FFFFFF;">4. Uso Aceptable de la Cuenta</h3>
                            <p>Usted se compromete a no utilizar el sistema para subir archivos corruptos, planos que violen derechos de autor de terceros o ejecutar scripts maliciosos. Queda prohibida la ingeniería inversa del motor de IA o el scraping automatizado de la base de datos de materiales y presupuestos de obra.</p>

                            <h3 style="color: #FFFFFF;">5. Modificaciones del Servicio y Tarifas</h3>
                            <p>La empresa se reserva el derecho de modificar o suspender temporal o permanentemente el servicio con o sin previo aviso. Los precios de los planes (180 Bs. y 220 Bs.) pueden estar sujetos a cambios, los cuales se notificarán con al menos 30 días de anticipación.</p>
                        </div>
                    </div>
                    """
                    text_tc = strip_tags(html_tc)
                    msg_tc = EmailMultiAlternatives(subject_tc, text_tc, settings.DEFAULT_FROM_EMAIL, [usuario.email])
                    msg_tc.attach_alternative(html_tc, "text/html")
                    msg_tc.send(fail_silently=False)
                    print(f"[Email] Correo de Terminos enviado a {usuario.email}")

                    # 3. ENVIAR CORREO DE POLÍTICA DE PRIVACIDAD
                    subject_pp = 'Política de Privacidad - PlanRisk3D 🔒'
                    html_pp = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #111; border-radius: 10px; overflow: hidden; background-color: #0B132B; color: #E0E0E0;">
                        <div style="text-align: center; padding: 20px;">
                            <h1 style="color: #FFD700; margin-bottom: 5px;">Política de Privacidad</h1>
                            <p style="color: #A0A0A0; font-size: 12px; margin-top: 0;">Última actualización: Junio 2026</p>
                            <hr style="border: 1px solid #FFD700; width: 50px; margin: 10px auto;">
                        </div>
                        <div style="padding: 20px; font-size: 14px; line-height: 1.6;">
                            <h3 style="color: #FFFFFF;">1. Información que Recopilamos</h3>
                            <p>Recopilamos la información estrictamente necesaria para brindar nuestros servicios SaaS de simulación estructural y control de obras:</p>
                            <ul>
                                <li><strong>Datos de Registro:</strong> Nombre completo, apellido, dirección de correo electrónico, contraseña (encriptada), teléfono y profesión.</li>
                                <li><strong>Datos Técnicos:</strong> Archivos de planos arquitectónicos (PDF, PNG, JPG, CAD) que cargue en la plataforma y los modelos 3D resultantes.</li>
                                <li><strong>Registros de Transacciones:</strong> Registros del plan de suscripción seleccionado e historial de pagos.</li>
                            </ul>

                            <h3 style="color: #FFFFFF;">2. Uso de la Información</h3>
                            <p>Sus datos y planos se utilizan únicamente para procesar los modelos 3D estructurales mediante nuestra red neuronal Mask R-CNN, realizar análisis de daños vía Gemini AI y generar cómputos métricos de materiales. Nos comprometemos a no vender, alquilar ni compartir su información o archivos técnicos con terceros para fines comerciales o publicitarios.</p>

                            <div style="border: 1px solid #FFD700; border-radius: 8px; padding: 15px; margin: 20px 0; background-color: rgba(255, 215, 0, 0.05);">
                                <h3 style="color: #FFD700; margin-top: 0;">3. Seguridad y Auditoría en Blockchain</h3>
                                <p style="margin-bottom: 0;">Para garantizar la inmutabilidad y transparencia de las auditorías de riesgo estructural generadas en la plataforma, registramos los hashes criptográficos (huellas digitales) de los reportes en una cadena de bloques (Blockchain). Esto asegura que sus análisis de seguridad no puedan ser alterados retroactivamente. Adicionalmente, toda la comunicación se cifra mediante protocolos SSL/TLS y las contraseñas se almacenan con algoritmos de hasheo seguros (bcrypt/argon2) en el backend de Django.</p>
                            </div>

                            <h3 style="color: #FFFFFF;">4. Sus Derechos de Acceso y Eliminación</h3>
                            <p>Usted conserva el control total de sus datos. En cualquier momento, puede acceder a su perfil para modificar sus datos personales, descargar sus planos procesados o solicitar la eliminación total de su cuenta y archivos de nuestros servidores llamando al canal de soporte técnico.</p>
                        </div>
                    </div>
                    """
                    text_pp = strip_tags(html_pp)
                    msg_pp = EmailMultiAlternatives(subject_pp, text_pp, settings.DEFAULT_FROM_EMAIL, [usuario.email])
                    msg_pp.attach_alternative(html_pp, "text/html")
                    msg_pp.send(fail_silently=False)
                    print(f"[Email] Correo de Privacidad enviado a {usuario.email}")

                except Exception as e:
                    print("[Error] Error al enviar correos:", e)

            return Response(
                UsuarioSerializer(usuario).data,
                status=status.HTTP_201_CREATED
            )
        print("[Error] ERRORES DE SERIALIZER:", serializer.errors)
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
