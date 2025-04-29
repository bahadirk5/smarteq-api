from rest_framework.response import Response
from rest_framework import status

class ApiResponse(Response):
    """
    Standart API yanıt formatını sağlayan özel Response sınıfı.
    Tüm API yanıtlarını bu format ile standardize eder:
    {
        "data": object | null,
        "error": string | null,
        "status": number
    }
    """
    def __init__(self, data=None, error=None, status_code=status.HTTP_200_OK, **kwargs):
        content = {
            'data': data,
            'error': error,
            'status': status_code
        }
        super().__init__(data=content, status=status_code, **kwargs)


def success_response(data=None, status_code=status.HTTP_200_OK, **kwargs):
    """Başarılı API yanıtı oluşturmak için yardımcı fonksiyon"""
    return ApiResponse(data=data, error=None, status_code=status_code, **kwargs)


def error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
    """Hata yanıtı oluşturmak için yardımcı fonksiyon"""
    return ApiResponse(data=None, error=error_message, status_code=status_code, **kwargs)
