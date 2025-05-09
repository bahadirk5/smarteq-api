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


class CustomResponse:
    """
    Daha ayrıntılı API yanıtları için yardımcı sınıf.
    Bu sınıf, farklı durumlara göre özelleştirilmiş yanıtlar oluşturmayı sağlar.
    """
    @staticmethod
    def success(data=None, message=None, status_code=status.HTTP_200_OK):
        """
        Başarılı işlemler için yanıt döndürür.
        Args:
            data: İstemciye gönderilecek veriler
            message: İşlem hakkında bilgi mesajı
            status_code: HTTP durum kodu (varsayılan: 200 OK)
        """
        return Response(
            {
                'success': True,
                'message': message,
                'data': data
            },
            status=status_code
        )
    
    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """
        Kaynak oluşturma işlemleri için yanıt döndürür.
        """
        return CustomResponse.success(data=data, message=message, status_code=status.HTTP_201_CREATED)
    
    @staticmethod
    def bad_request(message="Bad request", errors=None):
        """
        Geçersiz istek durumlarında yanıt döndürür.
        """
        return Response(
            {
                'success': False,
                'message': message,
                'errors': errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def not_found(message="Resource not found"):
        """
        Kaynak bulunamadığında yanıt döndürür.
        """
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(message="Unauthorized access"):
        """
        Yetkilendirme hatalarında yanıt döndürür.
        """
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message="Access forbidden"):
        """
        Erişim yasaklandığında yanıt döndürür.
        """
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def server_error(message="Internal server error"):
        """
        Sunucu hatalarında yanıt döndürür.
        """
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
