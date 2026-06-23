from django.urls import path
from .views import analizar_glb, preguntar_chatbot

urlpatterns = [
    path('analizar/', analizar_glb, name='analizar-glb'),
    path('chat/', preguntar_chatbot, name='preguntar-chatbot'),
]
