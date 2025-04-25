"""
Request logging middleware for smarteq project.
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses.
    """

    def process_request(self, request):
        """
        Process request and set start time.
        """
        request.start_time = time.time()
        
        # Don't log media or static requests
        if request.path.startswith('/media/') or request.path.startswith('/static/'):
            return None
            
        # Log request details
        request_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') else 'AnonymousUser',
            'remote_addr': self._get_client_ip(request),
        }
        
        if request.GET:
            request_data['query_params'] = dict(request.GET)
        
        # Only log request body for non-GET methods and if not a file upload
        if request.method not in ('GET', 'HEAD') and not request.content_type.startswith('multipart/form-data'):
            try:
                request_data['body'] = json.loads(request.body) if request.body else None
            except json.JSONDecodeError:
                request_data['body'] = 'Invalid JSON'
        
        logger.info(f"REQUEST: {json.dumps(request_data)}")
        return None

    def process_response(self, request, response):
        """
        Process response and log response time.
        """
        # Skip logging for media and static files
        if request.path.startswith('/media/') or request.path.startswith('/static/'):
            return response
            
        # Calculate request processing time
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': f"{duration:.2f}s",
            }
            
            # Log response headers if there's an issue
            if response.status_code >= 400:
                response_data['headers'] = dict(response.headers)
                
            logger.info(f"RESPONSE: {json.dumps(response_data)}")
            
        return response
        
    def _get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip