"""
File upload and text extraction service for the document Q&A system.
Handles file validation, text extraction from various formats, and error handling.
"""

import os
import io
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import streamlit as st
import PyPDF2
from docx import Document

from src.utils.logging_config import get_logger
from src.utils.error_handling import FileUploadError, FileProcessingError, handle_errors

logger = get_logger(__name__)

@dataclass
class FileMetadata:
    """Metadata for uploaded files"""
    filename: str
    file_type: str
    file_size: int
    is_valid: bool
    error_message: Optional[str] = None

class FileUploadHandler:
    """Handles file uploads, validation, and text extraction"""
    
    # Supported file formats and their MIME types
    SUPPORTED_FORMATS = {
        'pdf': ['application/pdf'],
        'txt': ['text/plain'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    def __init__(self):
        """Initialize the file upload handler"""
        self.supported_extensions = ['.pdf', '.txt', '.docx']
    
    def validate_file(self, uploaded_file) -> FileMetadata:
        """
        Validate uploaded file format and size
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            FileMetadata: Validation results and metadata
        """
        try:
            if uploaded_file is None:
                return FileMetadata(
                    filename="",
                    file_type="",
                    file_size=0,
                    is_valid=False,
                    error_message="No file uploaded"
                )
            
            filename = uploaded_file.name
            file_size = uploaded_file.size
            
            # Check file size
            if file_size > self.MAX_FILE_SIZE:
                return FileMetadata(
                    filename=filename,
                    file_type="",
                    file_size=file_size,
                    is_valid=False,
                    error_message=f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum limit of 10MB"
                )
            
            # Check file extension
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in self.supported_extensions:
                return FileMetadata(
                    filename=filename,
                    file_type=file_extension,
                    file_size=file_size,
                    is_valid=False,
                    error_message=f"Unsupported file format '{file_extension}'. Supported formats: {', '.join(self.supported_extensions)}"
                )
            
            return FileMetadata(
                filename=filename,
                file_type=file_extension,
                file_size=file_size,
                is_valid=True
            )
            
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return FileMetadata(
                filename=getattr(uploaded_file, 'name', 'unknown'),
                file_type="",
                file_size=0,
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )
    
    def extract_text(self, uploaded_file) -> Tuple[str, Optional[str]]:
        """
        Extract text content from uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple[str, Optional[str]]: (extracted_text, error_message)
        """
        try:
            # Validate file first
            metadata = self.validate_file(uploaded_file)
            if not metadata.is_valid:
                return "", metadata.error_message
            
            file_extension = metadata.file_type
            
            # Extract text based on file type
            if file_extension == '.pdf':
                return self._extract_pdf_text(uploaded_file)
            elif file_extension == '.txt':
                return self._extract_txt_text(uploaded_file)
            elif file_extension == '.docx':
                return self._extract_docx_text(uploaded_file)
            else:
                return "", f"Unsupported file format: {file_extension}"
                
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            return "", f"Text extraction failed: {str(e)}"
    
    def _extract_pdf_text(self, uploaded_file) -> Tuple[str, Optional[str]]:
        """Extract text from PDF file"""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            if not text_content:
                return "", "No readable text found in PDF file"
            
            return "\n\n".join(text_content), None
            
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return "", f"Failed to extract text from PDF: {str(e)}"
    
    def _extract_txt_text(self, uploaded_file) -> Tuple[str, Optional[str]]:
        """Extract text from TXT file"""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    content = uploaded_file.read()
                    if isinstance(content, bytes):
                        text = content.decode(encoding)
                    else:
                        text = str(content)
                    
                    if text.strip():
                        return text, None
                except UnicodeDecodeError:
                    continue
            
            return "", "Could not decode text file with any supported encoding"
            
        except Exception as e:
            logger.error(f"TXT extraction error: {str(e)}")
            return "", f"Failed to extract text from TXT file: {str(e)}"
    
    def _extract_docx_text(self, uploaded_file) -> Tuple[str, Optional[str]]:
        """Extract text from DOCX file"""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            doc = Document(uploaded_file)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            if not text_content:
                return "", "No readable text found in DOCX file"
            
            return "\n\n".join(text_content), None
            
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            return "", f"Failed to extract text from DOCX file: {str(e)}"
    
    def get_file_metadata(self, uploaded_file) -> Dict[str, Any]:
        """
        Get comprehensive metadata for uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dict[str, Any]: File metadata dictionary
        """
        metadata = self.validate_file(uploaded_file)
        
        return {
            'filename': metadata.filename,
            'file_type': metadata.file_type,
            'file_size': metadata.file_size,
            'file_size_mb': round(metadata.file_size / (1024 * 1024), 2),
            'is_valid': metadata.is_valid,
            'error_message': metadata.error_message,
            'supported_formats': self.supported_extensions
        }