"""Comprehensive error handling utilities for the Document Q&A System."""

import functools
import traceback
from typing import Any, Callable, Dict, Optional, Tuple, Union, List
from enum import Enum

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ErrorType(Enum):
    """Enumeration of error types in the system."""
    FILE_UPLOAD = "file_upload"
    FILE_PROCESSING = "file_processing"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    WORKFLOW_ERROR = "workflow_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    STORAGE_ERROR = "storage_error"
    QA_ERROR = "qa_error"
    SYSTEM_ERROR = "system_error"
    # Enhanced Q&A specific errors
    ENHANCED_ANALYSIS_ERROR = "enhanced_analysis_error"
    CONVERSATIONAL_AI_ERROR = "conversational_ai_error"
    EXCEL_GENERATION_ERROR = "excel_generation_error"
    TEMPLATE_ERROR = "template_error"
    CONTEXT_MANAGEMENT_ERROR = "context_management_error"


class DocumentQAError(Exception):
    """Base exception class for Document Q&A System errors."""
    
    def __init__(self, message: str, error_type: ErrorType, 
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error": True,
            "message": self.message,
            "error_type": self.error_type.value,
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None
        }


class FileUploadError(DocumentQAError):
    """Error during file upload operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.FILE_UPLOAD, details, original_error)


class FileProcessingError(DocumentQAError):
    """Error during file processing operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.FILE_PROCESSING, details, original_error)


class APIError(DocumentQAError):
    """Error during API calls."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.API_ERROR, details, original_error)


class DatabaseError(DocumentQAError):
    """Error during database operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.DATABASE_ERROR, details, original_error)


class WorkflowError(DocumentQAError):
    """Error during workflow processing."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.WORKFLOW_ERROR, details, original_error)


class ValidationError(DocumentQAError):
    """Error during data validation."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.VALIDATION_ERROR, details, original_error)


class TimeoutError(DocumentQAError):
    """Error due to operation timeout."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.TIMEOUT_ERROR, details, original_error)


class StorageError(DocumentQAError):
    """Error during storage operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.STORAGE_ERROR, details, original_error)


class QAError(DocumentQAError):
    """Error during Q&A operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.QA_ERROR, details, original_error)


class EnhancedAnalysisError(DocumentQAError):
    """Error during enhanced analysis operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.ENHANCED_ANALYSIS_ERROR, details, original_error)


class ConversationalAIError(DocumentQAError):
    """Error during conversational AI operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.CONVERSATIONAL_AI_ERROR, details, original_error)


class ExcelGenerationError(DocumentQAError):
    """Error during Excel report generation."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.EXCEL_GENERATION_ERROR, details, original_error)


class TemplateError(DocumentQAError):
    """Error during template operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.TEMPLATE_ERROR, details, original_error)


class ContextManagementError(DocumentQAError):
    """Error during conversation context management."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.CONTEXT_MANAGEMENT_ERROR, details, original_error)


def handle_errors(error_type: ErrorType = ErrorType.SYSTEM_ERROR, 
                 return_error_dict: bool = False,
                 log_error: bool = True):
    """Decorator for handling errors in functions."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DocumentQAError:
                # Re-raise our custom errors
                raise
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                error = DocumentQAError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    error_type=error_type,
                    details={"function": func.__name__, "args": str(args)},
                    original_error=e
                )
                
                if return_error_dict:
                    return error.to_dict()
                else:
                    raise error
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, **kwargs) -> Tuple[Any, Optional[Exception]]:
    """Safely execute a function and return result and error."""
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        return None, e


def format_error_for_ui(error: Union[Exception, DocumentQAError, str]) -> Dict[str, Any]:
    """Format error for display in UI."""
    if isinstance(error, DocumentQAError):
        return {
            "error": True,
            "message": error.message,
            "type": error.error_type.value,
            "user_message": _get_user_friendly_message(error),
            "details": error.details
        }
    elif isinstance(error, Exception):
        return {
            "error": True,
            "message": str(error),
            "type": "system_error",
            "user_message": "An unexpected error occurred. Please try again.",
            "details": {"exception_type": type(error).__name__}
        }
    else:
        return {
            "error": True,
            "message": str(error),
            "type": "unknown_error",
            "user_message": str(error),
            "details": {}
        }


def _get_user_friendly_message(error: DocumentQAError) -> str:
    """Get user-friendly error message based on error type."""
    error_messages = {
        ErrorType.FILE_UPLOAD: "There was a problem uploading your file. Please check the file format and size.",
        ErrorType.FILE_PROCESSING: "We couldn't process your document. Please try uploading it again.",
        ErrorType.API_ERROR: "There was a problem connecting to our AI service. Please try again in a moment.",
        ErrorType.DATABASE_ERROR: "There was a problem saving your data. Please try again.",
        ErrorType.WORKFLOW_ERROR: "There was a problem processing your document. Please try again.",
        ErrorType.VALIDATION_ERROR: "The provided data is invalid. Please check your input.",
        ErrorType.TIMEOUT_ERROR: "The operation took too long to complete. Please try again.",
        ErrorType.STORAGE_ERROR: "There was a problem storing your document. Please try again.",
        ErrorType.QA_ERROR: "There was a problem answering your question. Please try rephrasing it.",
        ErrorType.SYSTEM_ERROR: "An unexpected error occurred. Please try again.",
        # Enhanced Q&A specific messages
        ErrorType.ENHANCED_ANALYSIS_ERROR: "There was a problem with the enhanced analysis. Basic analysis is still available.",
        ErrorType.CONVERSATIONAL_AI_ERROR: "There was a problem with the conversational AI. Please try a simpler question.",
        ErrorType.EXCEL_GENERATION_ERROR: "There was a problem generating the Excel report. You can try downloading as CSV instead.",
        ErrorType.TEMPLATE_ERROR: "There was a problem with the analysis template. Using default analysis instead.",
        ErrorType.CONTEXT_MANAGEMENT_ERROR: "There was a problem managing conversation context. Your conversation will continue with basic functionality."
    }
    
    return error_messages.get(error.error_type, error.message)


class ErrorRecovery:
    """Utilities for error recovery and retry logic."""
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, 
                          backoff_factor: float = 1.0) -> Tuple[Any, Optional[Exception]]:
        """Retry a function with exponential backoff."""
        import time
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = func()
                return result, None
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed: {str(e)}")
        
        return None, last_error
    
    @staticmethod
    def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
        """Circuit breaker pattern for preventing cascading failures."""
        def decorator(func: Callable) -> Callable:
            func._failure_count = 0
            func._last_failure_time = 0
            func._is_open = False
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import time
                
                current_time = time.time()
                
                # Check if circuit is open and recovery time has passed
                if func._is_open:
                    if current_time - func._last_failure_time > recovery_timeout:
                        func._is_open = False
                        func._failure_count = 0
                        logger.info(f"Circuit breaker for {func.__name__} is now closed")
                    else:
                        raise DocumentQAError(
                            f"Circuit breaker is open for {func.__name__}",
                            ErrorType.SYSTEM_ERROR,
                            {"retry_after": recovery_timeout - (current_time - func._last_failure_time)}
                        )
                
                try:
                    result = func(*args, **kwargs)
                    # Reset failure count on success
                    func._failure_count = 0
                    return result
                except Exception as e:
                    func._failure_count += 1
                    func._last_failure_time = current_time
                    
                    if func._failure_count >= failure_threshold:
                        func._is_open = True
                        logger.error(f"Circuit breaker opened for {func.__name__} after {failure_threshold} failures")
                    
                    raise e
            
            return wrapper
        return decorator


class GracefulDegradation:
    """Utilities for graceful degradation when enhanced features fail."""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable, 
                     error_types: Optional[List[ErrorType]] = None) -> Callable:
        """Decorator that provides fallback functionality when primary function fails."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return primary_func(*args, **kwargs)
                except DocumentQAError as e:
                    if error_types is None or e.error_type in error_types:
                        logger.warning(f"Primary function failed, using fallback: {str(e)}")
                        return fallback_func(*args, **kwargs)
                    else:
                        raise
                except Exception as e:
                    logger.warning(f"Primary function failed with unexpected error, using fallback: {str(e)}")
                    return fallback_func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def enhanced_with_basic_fallback(enhanced_func: Callable, basic_func: Callable):
        """Specific fallback for enhanced features to basic functionality."""
        return GracefulDegradation.with_fallback(
            enhanced_func, 
            basic_func,
            [ErrorType.ENHANCED_ANALYSIS_ERROR, ErrorType.CONVERSATIONAL_AI_ERROR, 
             ErrorType.TEMPLATE_ERROR, ErrorType.API_ERROR]
        )
    
    @staticmethod
    def safe_enhanced_operation(operation: Callable, fallback_result: Any = None, 
                              log_errors: bool = True) -> Tuple[Any, bool]:
        """
        Safely execute enhanced operation with fallback result.
        
        Returns:
            Tuple of (result, success_flag)
        """
        try:
            result = operation()
            return result, True
        except (EnhancedAnalysisError, ConversationalAIError, TemplateError, 
                ExcelGenerationError, ContextManagementError) as e:
            if log_errors:
                logger.warning(f"Enhanced operation failed gracefully: {str(e)}")
            return fallback_result, False
        except Exception as e:
            if log_errors:
                logger.error(f"Enhanced operation failed unexpectedly: {str(e)}")
            return fallback_result, False


class AlternativeFormats:
    """Utilities for providing alternative data formats when primary format fails."""
    
    @staticmethod
    def excel_to_csv_fallback(data: List[Dict[str, Any]], filename: str) -> str:
        """Convert data to CSV format when Excel generation fails."""
        import csv
        import io
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def excel_to_json_fallback(data: List[Dict[str, Any]]) -> str:
        """Convert data to JSON format when Excel generation fails."""
        import json
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def create_fallback_report(data: Dict[str, Any], format_type: str = "json") -> str:
        """Create fallback report in specified format."""
        if format_type == "csv":
            # Flatten data for CSV
            flattened_data = []
            for section, content in data.items():
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            item['section'] = section
                            flattened_data.append(item)
                        else:
                            flattened_data.append({'section': section, 'content': str(item)})
                else:
                    flattened_data.append({'section': section, 'content': str(content)})
            
            return AlternativeFormats.excel_to_csv_fallback(flattened_data, "fallback_report")
        
        elif format_type == "json":
            return AlternativeFormats.excel_to_json_fallback([data])
        
        else:
            # Plain text fallback
            text_output = []
            for section, content in data.items():
                text_output.append(f"\n{section.upper()}:")
                text_output.append("-" * len(section))
                if isinstance(content, list):
                    for item in content:
                        text_output.append(f"• {str(item)}")
                else:
                    text_output.append(str(content))
                text_output.append("")
            
            return "\n".join(text_output)


# Global instances
error_recovery = ErrorRecovery()
graceful_degradation = GracefulDegradation()
alternative_formats = AlternativeFormats()