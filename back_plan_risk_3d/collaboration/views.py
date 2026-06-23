"""Vistas API para la app de colaboración."""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.auth import JWTAuthentication
from .models import SalaColaborativa
from .serializers import SalaColaborativaSerializer


class CrearSalaView(APIView):
    """Crear una nueva sala colaborativa para un proyecto 3D."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Crea una sala colaborativa y devuelve el token UUID.

        Body esperado: { "proyecto_id": <int> }
        """
        proyecto_id = request.data.get('proyecto_id')
        if not proyecto_id:
            return Response(
                {'error': 'Se requiere proyecto_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reutilizar sala activa existente o crear una nueva
        sala_existente = SalaColaborativa.objects.filter(
            proyecto_id=proyecto_id,
            activa=True
        ).first()

        if sala_existente:
            serializer = SalaColaborativaSerializer(sala_existente)
            return Response(serializer.data, status=status.HTTP_200_OK)

        sala = SalaColaborativa.objects.create(
            proyecto_id=proyecto_id,
            creador=request.user
        )
        serializer = SalaColaborativaSerializer(sala)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnviarInvitacionView(APIView):
    """Enviar un correo de invitación a la sala colaborativa."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Enviar enlace de colaboración por email SMTP.

        Body esperado:
        {
            "email_destino": "correo@ejemplo.com",
            "enlace": "http://localhost:4200/private/editor?room=<uuid>",
            "nombre_proyecto": "Mi Proyecto"
        }
        """
        email_destino = request.data.get('email_destino')
        enlace = request.data.get('enlace')
        nombre_proyecto = request.data.get('nombre_proyecto', 'Proyecto 3D')

        if not email_destino or not enlace:
            return Response(
                {'error': 'Se requiere email_destino y enlace'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = request.user
        nombre_invitador = getattr(usuario, 'nombre', 'Un usuario')

        subject = f'🏗️ {nombre_invitador} te invita a colaborar en PlanRisk3D'
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #003366, #0066cc); padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0;">PlanRisk3D</h1>
                <p style="margin: 5px 0 0; opacity: 0.9;">Colaboración en Tiempo Real</p>
            </div>
            <div style="padding: 25px; color: #333;">
                <h2 style="color: #003366;">¡Hola! 👋</h2>
                <p><strong>{nombre_invitador}</strong> te ha invitado a colaborar en el proyecto
                   <strong>"{nombre_proyecto}"</strong> dentro de PlanRisk3D.</p>

                <p>Podrás ver el modelo 3D en tiempo real y mover piezas junto a otros colaboradores.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{enlace}"
                       style="background-color: #003366; color: white; padding: 14px 30px;
                              text-decoration: none; border-radius: 8px; font-weight: bold;
                              font-size: 16px; display: inline-block;">
                        Unirme a la Colaboración 🚀
                    </a>
                </div>

                <p style="color: #666; font-size: 13px;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                    <a href="{enlace}" style="color: #0066cc; word-break: break-all;">{enlace}</a>
                </p>
            </div>
            <div style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                © 2026 PlanRisk3D - Innovación en la Construcción.<br>
                Este correo fue enviado automáticamente, no responder.
            </div>
        </div>
        """

        text_content = strip_tags(html_content)

        try:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email_destino]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            print(f"✅ Invitación colaborativa enviada a {email_destino}")
            return Response(
                {'message': f'Invitación enviada a {email_destino}'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"❌ Error al enviar invitación: {e}")
            return Response(
                {'error': f'Error al enviar correo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EnviarGLBView(APIView):
    """Enviar un archivo .glb por correo electrónico."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Recibe un archivo y un correo, y lo envía por SMTP.
        """
        email_destino = request.data.get('email_destino')
        archivo_glb = request.FILES.get('archivo_glb')
        nombre_proyecto = request.data.get('nombre_proyecto', 'Proyecto 3D')

        if not email_destino or not archivo_glb:
            return Response(
                {'error': 'Se requiere email_destino y archivo_glb'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = request.user
        nombre_remitente = getattr(usuario, 'nombre', 'Un usuario')

        subject = f'📦 {nombre_remitente} te ha enviado el modelo 3D: {nombre_proyecto}'
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #003366, #0066cc); padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0;">PlanRisk3D</h1>
                <p style="margin: 5px 0 0; opacity: 0.9;">Modelo 3D Exportado</p>
            </div>
            <div style="padding: 25px; color: #333;">
                <h2 style="color: #003366;">¡Hola! 👋</h2>
                <p><strong>{nombre_remitente}</strong> te ha compartido el modelo 3D del proyecto
                   <strong>"{nombre_proyecto}"</strong>.</p>
                <p>Encuentras el archivo <strong>.glb</strong> adjunto a este correo. Puedes abrirlo en cualquier visor 3D compatible (como el visor 3D de Windows, Blender, o visores web).</p>
            </div>
            <div style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                © 2026 PlanRisk3D - Innovación en la Construcción.<br>
                Este correo fue enviado automáticamente, no responder.
            </div>
        </div>
        """

        text_content = strip_tags(html_content)

        try:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email_destino]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Adjuntar el archivo GLB
            msg.attach(archivo_glb.name, archivo_glb.read(), 'model/gltf-binary')

            msg.send(fail_silently=False)
            print(f"✅ Modelo enviado correctamente a {email_destino}")
            return Response(
                {'message': f'Modelo enviado a {email_destino}'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"❌ Error al enviar modelo: {e}")
            return Response(
                {'error': f'Error al enviar modelo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ObtenerSalaView(APIView):
    """Obtener los detalles de una sala colaborativa por su token."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        try:
            sala = SalaColaborativa.objects.get(token=token, activa=True)
            proyecto = sala.proyecto
            return Response({
                'token': sala.token,
                'proyecto_id': proyecto.id,
                'glb_model': proyecto.glb_model.url if proyecto.glb_model else None,
            }, status=status.HTTP_200_OK)
        except SalaColaborativa.DoesNotExist:
            return Response({'error': 'Sala no encontrada o inactiva'}, status=status.HTTP_404_NOT_FOUND)


class CerrarSalaView(APIView):
    """Cerrar (desactivar) una sala colaborativa."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Desactivar una sala colaborativa.

        Body esperado: { "token": "<uuid>" }
        """
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Se requiere token de la sala'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sala = SalaColaborativa.objects.get(token=token)
            sala.activa = False
            sala.save()
            return Response(
                {'message': 'Sala cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        except SalaColaborativa.DoesNotExist:
            return Response(
                {'error': 'Sala no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

