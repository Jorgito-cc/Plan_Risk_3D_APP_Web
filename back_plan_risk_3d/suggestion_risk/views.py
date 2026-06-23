from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services_gemini import analizar_modelo_glb, call_gemini, call_groq


@api_view(['POST'])
def analizar_glb(request):
    """
    Analizar archivos .glb con Gemini AI.

    Recibe un archivo .glb y retorna análisis de daños estructurales
    y sugerencias de materiales.

    Returns:
        Response con análisis o mensaje de error
    """
    if 'archivo' not in request.FILES:
        error_msg = (
            'No se ha enviado ningún archivo. '
            'Por favor envía un archivo con la clave "archivo"'
        )
        return Response(
            {'error': error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )

    archivo_glb = request.FILES['archivo']

    # Validar que sea un archivo .glb
    if not archivo_glb.name.endswith('.glb'):
        return Response(
            {'error': 'El archivo debe ser de tipo .glb'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Llamar al servicio de Gemini
    resultado = analizar_modelo_glb(archivo_glb)

    if resultado.get('success'):
        return Response(resultado, status=status.HTTP_200_OK)
    else:
        return Response(
            resultado,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def preguntar_chatbot(request):
    query = request.data.get("query")
    if not query:
        return Response({"error": "Falta la pregunta"}, status=status.HTTP_400_BAD_REQUEST)
    
    contexto = f"""
    Eres el Asistente Virtual Oficial de "Plan Risk 3D". Tu trabajo es ayudar a los visitantes y clientes respondiendo preguntas sobre la plataforma de manera amable, profesional y concisa en español.
    
    INFORMACIÓN DE LA PLATAFORMA:
    - ¿Qué es Plan Risk 3D?: Es una plataforma avanzada que convierte automáticamente planos 2D (PDF, DXF, DWG o imágenes) en modelos 3D interactivos (GLB) mediante Visión Artificial (Mask R-CNN).
    - Detección de Riesgos: Analiza problemas estructurales y sugiere materiales de construcción usando Inteligencia Artificial.
    - Blockchain: Certifica la autenticidad de los planos registrando sus firmas criptográficas en la red Polygon (Amoy) para evitar falsificaciones.
    - Aplicación Móvil: Cuenta con una app en Flutter para visualizar los modelos 3D y proyectarlos en Realidad Aumentada (AR).
    
    PLANES DE SUSCRIPCIÓN Y PRECIOS:
    1. Plan Free (Normal): Gratis. Límite de hasta 4 proyectos/planos creados.
    2. Plan Estrella: Bs. 180 al mes. Permite crear hasta 24 proyectos.
    3. Plan Premium: Bs. 22,080 al mes. Proyectos ilimitados y soporte prioritario.
    
    Responde a la siguiente consulta utilizando únicamente esta información. Si te preguntan algo fuera de tema, guíalos amablemente de vuelta a Plan Risk 3D. No uses formato markdown de bloque de código en tu respuesta, responde con texto simple o markdown normal.
    
    Pregunta del usuario: {query}
    Respuesta:
    """
    
    resultado = call_groq(contexto)
    
    if resultado.get("success"):
        return Response({"respuesta": resultado["data"]}, status=status.HTTP_200_OK)
    else:
        return Response({"error": resultado.get("error", "Error al procesar la respuesta")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
