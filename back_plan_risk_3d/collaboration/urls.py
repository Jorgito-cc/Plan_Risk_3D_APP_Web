from django.urls import path
from .views import CrearSalaView, EnviarInvitacionView, CerrarSalaView, ObtenerSalaView, EnviarGLBView

urlpatterns = [
    path('crear-sala/', CrearSalaView.as_view(), name='crear_sala'),
    path('enviar-invitacion/', EnviarInvitacionView.as_view(), name='enviar_invitacion'),
    path('enviar-glb/', EnviarGLBView.as_view(), name='enviar_glb'),
    path('sala/<uuid:token>/', ObtenerSalaView.as_view(), name='obtener_sala'),
    path('cerrar-sala/', CerrarSalaView.as_view(), name='cerrar_sala'),
]
