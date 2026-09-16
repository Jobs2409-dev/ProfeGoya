# core\exception.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Llamar al manejador de excepciones predeterminado de DRF
    response = exception_handler(exc, context)

    if response is not None:
        # Personalizar la respuesta de error
        custom_response_data = {
            'error': True,
            'detail': response.data,
        }
        return Response(custom_response_data, status=response.status_code)

    return Response({'error': 'Ocurrió un error inesperado.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

