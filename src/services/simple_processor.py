"""
Simple, direct document processor for immediate Q&A access.
No queues, no background processing - just direct Gemini API calls.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.models.document import Document
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger
from src.utils.error_handling import DocumentQAError, ErrorType

logger = get_logger(__name__)


class SimpleDocumentProcessor:
    """Simple processor that handles documents directly without complex workflows."""
    
    def __init__(self, api_key: str, storage: Optional[DocumentStorage] = None):
        self.api_key = api_key
        self.storage = storage or DocumentStorage()
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    def process_document_immediately(self, filename: str, file_type: str, 
                                   file_size: int, extracted_text: str) -> Document:
        """
        Process a document immediately and return a fully processed Document object.
        
        Args:
            filename: Name of the uploaded file
            file_type: File extension (pdf, txt, docx)
            file_size: Size of the file in bytes
            extracted_text: Extracted text content
            
        Returns:
            Document: Fully processed document ready for Q&A
        """
        logger.info(f"Starting immediate processing for {filename}")
        
        # Create document object
        document = Document(
            id=str(uuid.uuid4()),
            title=filename,
            file_type=file_type,
            file_size=file_size,
            upload_timestamp=datetime.now(),
            original_text=extracted_text,
            processing_status='processing'
        )
        
        # Try comprehensive AI processing in a single call to reduce API usage
        processing_errors = []
        
        try:
            # Single comprehensive processing call (reduces from 4 calls to 1)
            logger.info("Processing document with comprehensive AI analysis...")
            try:
                result = self._process_document_comprehensive(extracted_text)
                document.document_type = result.get('document_type', 'Unknown')
                document.extracted_info = result.get('extracted_info', {})
                document.analysis = result.get('analysis', '')
                document.summary = result.get('summary', '')
                logger.info(f"Comprehensive AI processing successful. Result keys: {list(result.keys())}")
                logger.debug(f"Extracted info type: {type(document.extracted_info)}")
            except Exception as e:
                processing_errors.append(f"Comprehensive processing failed: {str(e)}")
                logger.warning(f"Comprehensive processing failed, using fallback: {e}")
                
                # Fallback to basic processing
                document.document_type = "Unknown (AI processing failed)"
                document.extracted_info = self._create_basic_extraction(extracted_text)
                document.analysis = "Analysis unavailable due to API rate limits. Document text is available for Q&A."
                document.summary = self._create_basic_summary(extracted_text)
            
            # Determine final status
            if processing_errors:
                document.processing_status = 'partial'  # New status for partial processing
                logger.warning(f"Document processed with {len(processing_errors)} errors: {processing_errors}")
            else:
                document.processing_status = 'completed'
                logger.info("Document fully processed successfully")
            
            document.updated_at = datetime.now()
            
            # Store in database
            self.storage.create_document(document)
            
            logger.info(f"Document {document.id} stored with status: {document.processing_status}")
            return document
            
        except Exception as e:
            logger.error(f"Critical error processing document: {e}", exc_info=True)
            
            # Create minimal document for Q&A
            document.processing_status = 'minimal'
            document.document_type = "Unknown"
            document.extracted_info = self._create_basic_extraction(extracted_text)
            document.analysis = "Processing failed due to API issues. Basic Q&A available."
            document.summary = self._create_basic_summary(extracted_text)
            document.updated_at = datetime.now()
            
            # Still store the document so user can do basic Q&A
            try:
                self.storage.create_document(document)
                logger.info(f"Document {document.id} stored in minimal mode for basic Q&A")
                return document
            except Exception as storage_error:
                logger.error(f"Failed to store document: {storage_error}")
                raise DocumentQAError(
                    f"Complete processing failure: {str(e)}",
                    ErrorType.FILE_PROCESSING,
                    {"document_id": document.id, "filename": filename, "storage_error": str(storage_error)},
                    e
                )
    
    def _call_gemini(self, prompt: str, max_tokens: int = 1000, max_retries: int = 3) -> str:
        """Make a direct API call to Gemini with retry logic."""
        import requests
        import time
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Gemini API attempt {attempt + 1}/{max_retries}")
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
                
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                
                # Check if it's a retryable error
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    if status_code in [429, 500, 502, 503, 504]:  # Retryable errors
                        if attempt < max_retries - 1:
                            # Longer delays for rate limiting: 10, 30, 60 seconds
                            wait_time = 10 * (2 ** attempt)  
                            logger.info(f"Rate limited. Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                    else:
                        # Non-retryable error, don't retry
                        break
                else:
                    # Network error, retry
                    if attempt < max_retries - 1:
                        wait_time = 10 * (2 ** attempt)
                        logger.info(f"Network error, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                
            except (KeyError, IndexError) as e:
                last_error = e
                logger.error(f"Unexpected Gemini response format: {e}")
                break  # Don't retry format errors
        
        # All retries failed
        if isinstance(last_error, requests.exceptions.RequestException):
            raise DocumentQAError(
                f"Gemini API error after {max_retries} attempts: {str(last_error)}",
                ErrorType.API_ERROR,
                {"attempts": max_retries, "last_status": getattr(last_error.response, 'status_code', None) if hasattr(last_error, 'response') else None},
                last_error
            )
        else:
            raise DocumentQAError(
                f"Unexpected API response format: {str(last_error)}",
                ErrorType.API_ERROR,
                original_error=last_error
            )
    
    def _classify_document(self, text: str) -> str:
        """Classify the document type."""
        prompt = f"""
        Classify the following document into one of these categories:
        1. Legal Document (contracts, agreements, legal text)
        2. Technical Documentation (manuals, specifications, code documentation)
        3. Business Document (reports, proposals, memos)
        4. Academic Paper (research, thesis, academic writing)
        5. Personal Document (letters, diary entries, personal notes)
        6. News Article (journalism, news reports)
        7. Other
        
        Document to classify (first 1000 chars):
        {text[:1000]}...
        
        Respond with just the category name and a brief 1-sentence explanation.
        """
        
        return self._call_gemini(prompt, max_tokens=100)
    
    def _extract_information(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract key information from the document."""
        prompt = f"""
        Extract the following key information from this document:
        
        1. Main Topic/Subject
        2. Key Entities (people, organizations, places)
        3. Important Dates
        4. Key Numbers/Statistics
        5. Action Items or Requirements
        6. Summary (2-3 sentences)
        
        Document Type: {doc_type}
        
        Document:
        {text}
        
        Format your response as JSON with the above fields as keys. Use clear, descriptive values.
        """
        
        result = self._call_gemini(prompt, max_tokens=800)
        
        try:
            # Clean up the response to extract JSON
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON found", result, 0)
                
        except json.JSONDecodeError:
            # Fallback to structured text parsing
            return {
                "Main Topic": "Could not parse structured data",
                "Raw Extraction": result
            }
    
    def _analyze_document(self, text: str, extracted_info: Dict[str, Any], doc_type: str) -> str:
        """Analyze the document for insights and recommendations."""
        prompt = f"""
        Based on the following document and extracted information, provide:
        
        1. Key Insights (3-5 bullet points)
        2. Potential Issues or Concerns
        3. Recommendations or Next Steps
        4. Risk Assessment (Low/Medium/High) with reasoning
        5. Priority Level (Low/Medium/High/Urgent)
        
        Document Type: {doc_type}
        
        Extracted Information:
        {json.dumps(extracted_info, indent=2)}
        
        Original Document:
        {text}
        
        Provide a structured analysis with clear sections.
        """
        
        return self._call_gemini(prompt, max_tokens=1000)
    
    def _generate_summary(self, text: str, extracted_info: Dict[str, Any], 
                         analysis: str, doc_type: str) -> str:
        """Generate a comprehensive summary."""
        prompt = f"""
        Create a comprehensive executive summary based on the following processing results:
        
        Document Type: {doc_type}
        Document Length: {len(text)} characters
        
        Extracted Information:
        {json.dumps(extracted_info, indent=2)}
        
        Analysis:
        {analysis}
        
        Create a clear, actionable executive summary that includes:
        1. Document Overview
        2. Key Findings
        3. Critical Information
        4. Recommended Actions
        5. Executive Recommendation
        
        Keep it concise but comprehensive. Use clear headings and bullet points where appropriate.
        """
        
        return self._call_gemini(prompt, max_tokens=800)
    
    def _process_document_comprehensive(self, text: str) -> Dict[str, Any]:
        """Process document with a single comprehensive API call to reduce rate limiting."""
        prompt = f"""
        Please analyze the following document comprehensively and provide a structured response with ALL of the following information:

        1. DOCUMENT CLASSIFICATION:
        Classify into one of these categories: Legal Document, Technical Documentation, Business Document, Academic Paper, Personal Document, News Article, or Other. Provide the category name and a brief explanation.

        2. KEY INFORMATION EXTRACTION:
        Extract the following as JSON:
        - Main Topic/Subject
        - Key Entities (people, organizations, places)
        - Important Dates
        - Key Numbers/Statistics
        - Action Items or Requirements
        - Summary (2-3 sentences)

        3. DETAILED ANALYSIS:
        Provide:
        - Key Insights (3-5 bullet points)
        - Potential Issues or Concerns
        - Recommendations or Next Steps
        - Risk Assessment (Low/Medium/High) with reasoning
        - Priority Level (Low/Medium/High/Urgent)

        4. EXECUTIVE SUMMARY:
        Create a comprehensive executive summary including:
        - Document Overview
        - Key Findings
        - Critical Information
        - Recommended Actions
        - Executive Recommendation

        Document to analyze:
        {text}

        Please format your response as JSON with these exact keys:
        {{
            "document_type": "category and explanation",
            "extracted_info": {{
                "Main Topic": "...",
                "Key Entities": [...],
                "Important Dates": [...],
                "Key Numbers/Statistics": [...],
                "Action Items or Requirements": [...],
                "Summary": "..."
            }},
            "analysis": "detailed analysis text",
            "summary": "executive summary text"
        }}
        """
        
        result_text = self._call_gemini(prompt, max_tokens=2000)
        
        try:
            # Try to parse as JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                parsed_result = json.loads(json_str)
                
                # Ensure analysis and summary are strings, not dicts
                if isinstance(parsed_result.get('analysis'), dict):
                    analysis_dict = parsed_result['analysis']
                    analysis_text = ""
                    for key, value in analysis_dict.items():
                        if isinstance(value, list):
                            analysis_text += f"\n\n**{key}:**\n" + "\n".join(f"- {item}" for item in value)
                        else:
                            analysis_text += f"\n\n**{key}:**\n{value}"
                    parsed_result['analysis'] = analysis_text.strip()
                
                if isinstance(parsed_result.get('summary'), dict):
                    summary_dict = parsed_result['summary']
                    summary_text = ""
                    for key, value in summary_dict.items():
                        summary_text += f"\n\n**{key}:**\n{value}"
                    parsed_result['summary'] = summary_text.strip()
                
                return parsed_result
            else:
                raise json.JSONDecodeError("No JSON found", result_text, 0)
                
        except json.JSONDecodeError:
            # Fallback: parse the text manually
            logger.warning("Could not parse JSON response, using text parsing fallback")
            return {
                "document_type": "Document processed (format parsing failed)",
                "extracted_info": {
                    "Main Topic": "Document content available for Q&A",
                    "Summary": "Document processed successfully. Full text available for question answering.",
                    "Processing Note": "Comprehensive analysis completed but format parsing failed"
                },
                "analysis": result_text[:500] + "..." if len(result_text) > 500 else result_text,
                "summary": "Document has been processed and is ready for Q&A. Full analysis available in the analysis section."
            }
    
    def _create_basic_extraction(self, text: str) -> Dict[str, Any]:
        """Create basic information extraction without AI."""
        words = text.split()
        sentences = text.split('.')
        
        # Simple heuristics for basic extraction
        return {
            "Main Topic": "Document content available for Q&A",
            "Document Length": f"{len(text)} characters, {len(words)} words",
            "Key Statistics": f"{len(sentences)} sentences",
            "Summary": f"Document uploaded successfully. Full text available for question answering.",
            "Processing Note": "AI analysis unavailable - using basic extraction"
        }
    
    def _create_basic_summary(self, text: str) -> str:
        """Create a basic summary without AI."""
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Take first few sentences as basic summary
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        basic_summary = '. '.join(summary_sentences)
        
        if len(basic_summary) > 300:
            basic_summary = basic_summary[:300] + "..."
        
        return f"""
## Basic Document Summary

**Document Statistics:**
- Length: {len(text):,} characters
- Words: {len(words):,}
- Sentences: {len(sentences)}

**Content Preview:**
{basic_summary}

**Note:** This is a basic summary. AI analysis was unavailable, but you can still ask questions about the document content.
"""