from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, RegistroView, LoginView, LogoutView, update_usuario, DashboardKPIsView, PlanConfigView, AdminHistorialPlanosView
from .pagues import (
    create_checkout_session,
    stripe_webhook,
    confirm_payment,
    check_project_limit,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/usuario/update/<int:pk>/', update_usuario, name='usuario-update'),
    path('admin/kpis/', DashboardKPIsView.as_view(), name='admin-kpis'),
    path('admin/planes-config/', PlanConfigView.as_view(), name='admin-planes-config'),
    path('admin/historial-planos/', AdminHistorialPlanosView.as_view(), name='admin-historial-planos'),

    # Stripe Checkout
    path('stripe/create-checkout-session/', create_checkout_session, name='stripe-checkout'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('stripe/confirm-payment/', confirm_payment, name='stripe-confirm'),

    # Validación de límite de proyectos
    path('check-project-limit/', check_project_limit, name='check-project-limit'),

    path('', include(router.urls)),
]
