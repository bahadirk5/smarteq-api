import logging
import traceback
from functools import wraps

# Create inventory logger
logger = logging.getLogger('apps.inventory')

def log_exception(func):
    """
    Decorator that logs exceptions that occur in the decorated function
    and re-raises them.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get calling function details
            try:
                module_name = func.__module__
                class_name = args[0].__class__.__name__ if args else ""
                func_name = func.__name__
                caller_info = f"{module_name}.{class_name}.{func_name}"
            except:
                caller_info = func.__name__
            
            # Get traceback info
            tb = traceback.format_exc()
            
            # Log the error with detailed information
            logger.error(
                f"Exception in {caller_info}: {str(e)}\n"
                f"Args: {args[1:]}\n"
                f"Kwargs: {kwargs}\n"
                f"Traceback:\n{tb}"
            )
            raise
    return wrapper

class LoggerMixin:
    """
    Mixin to add logging capabilities to a class.
    """
    
    @property
    def logger(self):
        # Use class name for logger to help identify source of logs
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f'apps.inventory.{self.__class__.__name__}')
        return self._logger
    
    def log_debug(self, message):
        self.logger.debug(message)
    
    def log_info(self, message):
        self.logger.info(message)
    
    def log_warning(self, message):
        self.logger.warning(message)
    
    def log_error(self, message, exc_info=None):
        if exc_info:
            self.logger.error(message, exc_info=exc_info)
        else:
            self.logger.error(message)
        
    def log_exception(self, message):
        self.logger.exception(message)