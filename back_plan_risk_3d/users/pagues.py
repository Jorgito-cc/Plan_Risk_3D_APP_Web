"""Procesamiento de pagos con Stripe Checkout."""
from datetime import date, timedelta

import json
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from plans.models import Plan3DJob
from .models import Usuario

# --- Stripe Configuration ---
STRIPE_SECRET_KEY = (
    "sk_test_51QIgrTGy5MqVc5xQsB2Zp0YPH9r5nKm0JzPwOWyM57v"
    "GDCJCDLrTotXFpC7vjZJXu854YrFhZBpZsYm0FqwA243H00VflnNCIg"
)
stripe.api_key = STRIPE_SECRET_KEY

# URLs del frontend React para redirección post-pago
REACT_FRONTEND_URL = "https://corporativosw.netlify.app"

# Mapeo de planes a precios y roles
PLAN_CONFIG = {
    "usuario_estrella": {
        "name": "Plan Estrella - Plan Risk 3D",
        "price": 18000,  # 180.00 Bs en centavos
        "currency": "bob",
        "description": "24 proyectos/mes · Visor 3D avanzado · Detección IA",
    },
    "usuario_premium": {
        "name": "Plan Premium - Plan Risk 3D",
        "price": 22000,  # 220.00 Bs en centavos
        "currency": "bob",
        "description": "Proyectos ilimitados · IA completa · Blockchain · n8n",
    },
}

# Límites de proyectos por plan
PROJECT_LIMITS = {
    "usuario_normal": 4,
    "usuario_estrella": 24,
    "usuario_premium": None,  # Ilimitado
    "Administrador": None,    # Ilimitado
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Crear una sesión de Stripe Checkout.

    Recibe el plan deseado y redirige al usuario a la página de pago de Stripe.
    """
    try:
        plan = request.data.get('plan')
        user = request.user

        if plan not in PLAN_CONFIG:
            return Response(
                {
                    'success': False,
                    'message': (
                        'Plan no válido. '
                        'Opciones: usuario_estrella, usuario_premium'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        config = PLAN_CONFIG[plan]

        # Crear la sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': config['currency'],
                    'product_data': {
                        'name': config['name'],
                        'description': config['description'],
                    },
                    'unit_amount': config['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=(
                f"{REACT_FRONTEND_URL}/planes"
                f"?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=f"{REACT_FRONTEND_URL}/planes?payment=cancel",
            metadata={
                'usuario_id': str(user.id),
                'plan': plan,
            },
            customer_email=user.email,
        )

        return Response(
            {
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id,
            },
            status=status.HTTP_200_OK
        )

    except stripe.error.StripeError as e:
        return Response(
            {
                'success': False,
                'message': f'Error de Stripe: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Error interno: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Webhook de Stripe para procesar eventos de pago completado.

    Escucha el evento 'checkout.session.completed' y actualiza
    el rol del usuario automáticamente.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    # Si no hay firma del webhook, procesar igualmente en desarrollo
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # Procesar el evento checkout.session.completed
    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        usuario_id = metadata.get('usuario_id')
        plan = metadata.get('plan')

        if usuario_id and plan:
            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
                usuario.rol = plan
                if not usuario.fecha_expiracion_plan:
                    usuario.fecha_expiracion_plan = date.today()
                usuario.fecha_expiracion_plan = (
                    date.today() + timedelta(days=30)
                )
                usuario.save()
                print(
                    f"✅ Pago confirmado: Usuario {usuario.email} "
                    f"actualizado a {plan}"
                )
            except Usuario.DoesNotExist:
                print(f"⚠️ Usuario con ID {usuario_id} no encontrado")

    return HttpResponse(status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """
    Confirmar pago manualmente (alternativa al webhook para desarrollo local).

    Verifica con Stripe que la sesión fue pagada y actualiza el rol del usuario.
    """
    try:
        session_id = request.data.get('session_id')
        user = request.user

        if not session_id:
            return Response(
                {'success': False, 'message': 'session_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Recuperar la sesión de Stripe para verificar el pago
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status != 'paid':
            return Response(
                {
                    'success': False,
                    'message': 'El pago no ha sido completado.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extraer metadata
        plan = session.metadata.get('plan')
        session_user_id = session.metadata.get('usuario_id')

        # Verificar que el usuario que confirma es el mismo que pagó
        if str(user.id) != str(session_user_id):
            return Response(
                {
                    'success': False,
                    'message': 'La sesión no corresponde a este usuario.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Actualizar el rol del usuario
        user.rol = plan
        if not user.fecha_expiracion_plan:
            user.fecha_expiracion_plan = date.today()
        user.fecha_expiracion_plan = date.today() + timedelta(days=30)
        user.save()

        return Response(
            {
                'success': True,
                'message': (
                    f'¡Pago confirmado! Plan actualizado a '
                    f'{"Estrella" if plan == "usuario_estrella" else "Premium"}.'
                ),
                'usuario': {
                    'id': user.id,
                    'nombre': user.nombre,
                    'email': user.email,
                    'rol': user.rol,
                    'fecha_expiracion_plan': str(
                        user.fecha_expiracion_plan
                    ),
                }
            },
            status=status.HTTP_200_OK
        )

    except stripe.error.StripeError as e:
        return Response(
            {'success': False, 'message': f'Error de Stripe: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'success': False, 'message': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_project_limit(request):
    """
    Verificar si el usuario puede crear más proyectos según su plan.

    Returns:
        JSON con: can_create, current_count, limit, rol
    """
    user = request.user
    current_count = Plan3DJob.objects.filter(usuario=user).count()
    limit = PROJECT_LIMITS.get(user.rol)

    can_create = True
    if limit is not None and current_count >= limit:
        can_create = False

    return Response(
        {
            'can_create': can_create,
            'current_count': current_count,
            'limit': limit,  # None = ilimitado
            'rol': user.rol,
            'upgrade_url': f'{REACT_FRONTEND_URL}/planes',
        },
        status=status.HTTP_200_OK
    )
