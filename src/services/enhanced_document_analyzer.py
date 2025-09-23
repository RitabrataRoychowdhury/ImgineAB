"""
Enhanced Document Analyzer for comprehensive document analysis and content extraction.
Supports multi-format parsing and intelligent content extraction for legal documents.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Document parsing imports
try:
    import PyPDF2
    import docx
    from docx import Document as DocxDocument
except ImportError:
    PyPDF2 = None
    docx = None
    DocxDocument = None

logger = logging.getLogger(__name__)

@dataclass
class Party:
    """Represents a party in a legal document"""
    name: str
    role: str  # e.g., "Provider", "Recipient", "Buyer", "Seller"
    contact_info: Optional[str] = None
    legal_entity_type: Optional[str] = None

@dataclass
class ImportantDate:
    """Represents an important date in a document"""
    date: datetime
    description: str
    date_type: str  # e.g., "effective", "expiration", "deadline", "milestone"
    criticality: str  # "high", "medium", "low"

@dataclass
class FinancialTerm:
    """Represents financial information in a document"""
    amount: Optional[float]
    currency: str
    description: str
    term_type: str  # e.g., "payment", "penalty", "deposit", "total_value"
    payment_schedule: Optional[str] = None

@dataclass
class Obligation:
    """Represents an obligation or commitment in a document"""
    party: str
    description: str
    deadline: Optional[datetime]
    obligation_type: str  # e.g., "delivery", "payment", "compliance", "reporting"
    criticality: str  # "high", "medium", "low"

@dataclass
class KeyInformation:
    """Container for all key information extracted from a document"""
    parties: List[Party]
    financial_terms: List[FinancialTerm]
    key_dates: List[ImportantDate]
    obligations: List[Obligation]
    definitions: Dict[str, str]
    governing_clauses: List[str]

@dataclass
class DocumentMetadata:
    """Metadata about the analyzed document"""
    title: str
    document_type: str
    classification_confidence: float
    language: str
    page_count: int
    word_count: int
    analysis_timestamp: datetime
    file_format: str

@dataclass
class DocumentAnalysis:
    """Complete analysis result for a document"""
    document_id: str
    metadata: DocumentMetadata
    key_information: KeyInformation
    content_structure: Dict[str, Any]
    extracted_text: str
    confidence_scores: Dict[str, float]

class EnhancedDocumentAnalyzer:
    """
    Enhanced document analyzer with multi-format parsing and intelligent content extraction.
    Supports PDF, Word, and text documents with specialized legal document analysis.
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        self.legal_terms_patterns = self._initialize_legal_patterns()
        self.financial_patterns = self._initialize_financial_patterns()
        self.date_patterns = self._initialize_date_patterns()
        
    def _initialize_legal_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for legal term recognition"""
        return {
            'parties': [
                r'(?i)\b(?:party|parties|provider|recipient|buyer|seller|vendor|client|contractor|subcontractor)\b',
                r'(?i)\b(?:company|corporation|llc|inc|ltd|partnership)\b',
                r'(?i)\b(?:hereinafter referred to as|shall be referred to as)\b'
            ],
            'obligations': [
                r'(?i)\b(?:shall|must|will|agrees to|undertakes to|commits to|responsible for)\b',
                r'(?i)\b(?:deliver|provide|perform|complete|maintain|ensure|comply)\b',
                r'(?i)\b(?:obligation|duty|responsibility|requirement|commitment)\b'
            ],
            'financial': [
                r'(?i)\b(?:payment|fee|cost|price|amount|sum|total|deposit|penalty)\b',
                r'(?i)\b(?:invoice|billing|remuneration|compensation|reimbursement)\b',
                r'(?i)\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|usd|eur|gbp)\b'
            ],
            'dates': [
                r'(?i)\b(?:effective|expiration|deadline|due|completion|termination)\s+date\b',
                r'(?i)\b(?:within|by|before|after|on or before)\s+\d+\s+(?:days|weeks|months|years)\b',
                r'(?i)\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
            ]
        }
    
    def _initialize_financial_patterns(self) -> List[str]:
        """Initialize patterns for financial information extraction"""
        return [
            r'\$[\d,]+(?:\.\d{2})?',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|usd|eur|gbp|cents)\b',
            r'(?i)\b(?:total|sum|amount|fee|cost|price|payment)\s*:?\s*\$?[\d,]+(?:\.\d{2})?\b',
            r'(?i)\b(?:monthly|annual|quarterly|weekly)\s+(?:payment|fee|cost)\s*:?\s*\$?[\d,]+(?:\.\d{2})?\b'
        ]
    
    def _initialize_date_patterns(self) -> List[str]:
        """Initialize patterns for date extraction"""
        return [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'(?i)\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b',
            r'(?i)\b\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b'
        ]
    
    def analyze_document_comprehensive(self, file_path: str, document_id: str) -> DocumentAnalysis:
        """
        Perform comprehensive analysis of a document including content extraction,
        metadata analysis, and key information identification.
        """
        try:
            # Extract text content
            extracted_text = self._extract_text_from_file(file_path)
            if not extracted_text:
                raise ValueError(f"Could not extract text from {file_path}")
            
            # Generate metadata
            metadata = self._generate_document_metadata(file_path, extracted_text, document_id)
            
            # Extract key information
            key_information = self._extract_key_information(extracted_text)
            
            # Analyze content structure
            content_structure = self._analyze_content_structure(extracted_text)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(extracted_text, key_information)
            
            return DocumentAnalysis(
                document_id=document_id,
                metadata=metadata,
                key_information=key_information,
                content_structure=content_structure,
                extracted_text=extracted_text,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            logger.error(f"Error analyzing document {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.txt':
                return self._extract_from_text(file_path)
            elif extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not available for PDF parsing")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting from PDF {file_path}: {str(e)}")
            
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from Word documents"""
        if docx is None:
            raise ImportError("python-docx not available for Word document parsing")
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting from Word document {file_path}: {str(e)}")
            return ""
    
    def _generate_document_metadata(self, file_path: str, content: str, document_id: str) -> DocumentMetadata:
        """Generate metadata for the document"""
        file_path = Path(file_path)
        
        # Basic counts
        word_count = len(content.split())
        page_count = max(1, content.count('\f') + 1)  # Form feed characters indicate page breaks
        
        # Estimate page count for different formats
        if file_path.suffix.lower() == '.pdf' and PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
            except:
                pass
        
        # Extract title (first non-empty line or filename)
        title = file_path.stem
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 100 and not first_line.lower().startswith(('page', 'document')):
                title = first_line
        
        return DocumentMetadata(
            title=title,
            document_type="unknown",  # Will be set by classifier
            classification_confidence=0.0,  # Will be set by classifier
            language="en",  # Default to English
            page_count=page_count,
            word_count=word_count,
            analysis_timestamp=datetime.now(),
            file_format=file_path.suffix.lower()
        )
    
    def _extract_key_information(self, content: str) -> KeyInformation:
        """Extract key information from document content"""
        return KeyInformation(
            parties=self._extract_parties(content),
            financial_terms=self._extract_financial_terms(content),
            key_dates=self._extract_key_dates(content),
            obligations=self._extract_obligations(content),
            definitions=self._extract_definitions(content),
            governing_clauses=self._extract_governing_clauses(content)
        )
    
    def _extract_parties(self, content: str) -> List[Party]:
        """Extract parties from document content"""
        parties = []
        
        # Look for party definitions
        party_patterns = [
            r'(?i)(?:party|provider|recipient|buyer|seller|vendor|client)\s*[:\-]\s*([^,\n]+)',
            r'(?i)([^,\n]+)\s*(?:hereinafter referred to as|shall be referred to as)\s*["\']?([^"\']+)["\']?',
            r'(?i)between\s+([^,\n]+)\s*,?\s*(?:and|&)\s*([^,\n]+)'
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    for party_name in match:
                        party_name = party_name.strip()
                        if party_name and len(party_name) > 2:
                            parties.append(Party(
                                name=party_name,
                                role=self._determine_party_role(party_name, content)
                            ))
                else:
                    party_name = match.strip()
                    if party_name and len(party_name) > 2:
                        parties.append(Party(
                            name=party_name,
                            role=self._determine_party_role(party_name, content)
                        ))
        
        # Remove duplicates
        unique_parties = []
        seen_names = set()
        for party in parties:
            if party.name.lower() not in seen_names:
                unique_parties.append(party)
                seen_names.add(party.name.lower())
        
        return unique_parties[:10]  # Limit to reasonable number
    
    def _determine_party_role(self, party_name: str, content: str) -> str:
        """Determine the role of a party based on context"""
        party_context = content.lower()
        name_lower = party_name.lower()
        
        role_indicators = {
            'provider': ['provide', 'supply', 'deliver', 'service'],
            'recipient': ['receive', 'accept', 'obtain'],
            'buyer': ['buy', 'purchase', 'acquire'],
            'seller': ['sell', 'vendor', 'supplier'],
            'contractor': ['contract', 'perform', 'execute'],
            'client': ['client', 'customer', 'user']
        }
        
        for role, indicators in role_indicators.items():
            if any(indicator in party_context for indicator in indicators):
                return role
        
        return 'party'
    
    def _extract_financial_terms(self, content: str) -> List[FinancialTerm]:
        """Extract financial terms from document content"""
        financial_terms = []
        
        for pattern in self.financial_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                amount_text = match.group()
                
                # Extract numeric amount
                amount_match = re.search(r'[\d,]+(?:\.\d{2})?', amount_text)
                amount = None
                if amount_match:
                    try:
                        amount = float(amount_match.group().replace(',', ''))
                    except ValueError:
                        pass
                
                # Determine currency
                currency = 'USD'  # Default
                if any(curr in amount_text.lower() for curr in ['eur', 'euro']):
                    currency = 'EUR'
                elif any(curr in amount_text.lower() for curr in ['gbp', 'pound']):
                    currency = 'GBP'
                
                # Get context for description
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                financial_terms.append(FinancialTerm(
                    amount=amount,
                    currency=currency,
                    description=context,
                    term_type=self._classify_financial_term(context)
                ))
        
        return financial_terms[:20]  # Limit to reasonable number
    
    def _classify_financial_term(self, context: str) -> str:
        """Classify the type of financial term based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['total', 'sum', 'amount']):
            return 'total_value'
        elif any(term in context_lower for term in ['payment', 'pay', 'remit']):
            return 'payment'
        elif any(term in context_lower for term in ['penalty', 'fine', 'late']):
            return 'penalty'
        elif any(term in context_lower for term in ['deposit', 'down payment']):
            return 'deposit'
        elif any(term in context_lower for term in ['fee', 'charge', 'cost']):
            return 'fee'
        else:
            return 'other'
    
    def _extract_key_dates(self, content: str) -> List[ImportantDate]:
        """Extract important dates from document content"""
        key_dates = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                date_text = match.group()
                
                # Parse the date
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    # Get context for description
                    start = max(0, match.start() - 30)
                    end = min(len(content), match.end() + 30)
                    context = content[start:end].strip()
                    
                    key_dates.append(ImportantDate(
                        date=parsed_date,
                        description=context,
                        date_type=self._classify_date_type(context),
                        criticality=self._assess_date_criticality(context)
                    ))
        
        # Sort by date and remove duplicates
        key_dates.sort(key=lambda x: x.date)
        unique_dates = []
        seen_dates = set()
        for date_item in key_dates:
            date_key = (date_item.date.date(), date_item.date_type)
            if date_key not in seen_dates:
                unique_dates.append(date_item)
                seen_dates.add(date_key)
        
        return unique_dates[:15]  # Limit to reasonable number
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse various date formats"""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%B %d, %Y', '%B %d %Y',
            '%d %B %Y', '%d %B, %Y'
        ]
        
        # Clean the date text
        date_text = re.sub(r'(?i)(st|nd|rd|th)', '', date_text).strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        
        return None
    
    def _classify_date_type(self, context: str) -> str:
        """Classify the type of date based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['effective', 'start', 'begin']):
            return 'effective'
        elif any(term in context_lower for term in ['expir', 'end', 'terminat']):
            return 'expiration'
        elif any(term in context_lower for term in ['deadline', 'due', 'by']):
            return 'deadline'
        elif any(term in context_lower for term in ['milestone', 'delivery', 'completion']):
            return 'milestone'
        else:
            return 'other'
    
    def _assess_date_criticality(self, context: str) -> str:
        """Assess the criticality of a date based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['critical', 'mandatory', 'required', 'must']):
            return 'high'
        elif any(term in context_lower for term in ['important', 'should', 'deadline']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_obligations(self, content: str) -> List[Obligation]:
        """Extract obligations from document content"""
        obligations = []
        
        # Look for obligation patterns
        obligation_patterns = [
            r'(?i)([^.]+)\s+(?:shall|must|will|agrees to|undertakes to)\s+([^.]+)',
            r'(?i)([^.]+)\s+(?:is responsible for|is obligated to|commits to)\s+([^.]+)',
            r'(?i)([^.]+)\s+(?:deliver|provide|perform|complete|maintain|ensure)\s+([^.]+)'
        ]
        
        for pattern in obligation_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) >= 2:
                    party = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    if len(party) < 100 and len(description) < 200:  # Reasonable length
                        obligations.append(Obligation(
                            party=party,
                            description=description,
                            deadline=None,  # Could be enhanced to extract deadlines
                            obligation_type=self._classify_obligation_type(description),
                            criticality=self._assess_obligation_criticality(description)
                        ))
        
        return obligations[:15]  # Limit to reasonable number
    
    def _classify_obligation_type(self, description: str) -> str:
        """Classify the type of obligation based on description"""
        desc_lower = description.lower()
        
        if any(term in desc_lower for term in ['deliver', 'ship', 'transport']):
            return 'delivery'
        elif any(term in desc_lower for term in ['pay', 'payment', 'remit']):
            return 'payment'
        elif any(term in desc_lower for term in ['comply', 'follow', 'adhere']):
            return 'compliance'
        elif any(term in desc_lower for term in ['report', 'notify', 'inform']):
            return 'reporting'
        elif any(term in desc_lower for term in ['maintain', 'keep', 'preserve']):
            return 'maintenance'
        else:
            return 'other'
    
    def _assess_obligation_criticality(self, description: str) -> str:
        """Assess the criticality of an obligation"""
        desc_lower = description.lower()
        
        if any(term in desc_lower for term in ['critical', 'essential', 'mandatory', 'required']):
            return 'high'
        elif any(term in desc_lower for term in ['important', 'should', 'necessary']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_definitions(self, content: str) -> Dict[str, str]:
        """Extract definitions from document content"""
        definitions = {}
        
        # Look for definition patterns
        definition_patterns = [
            r'(?i)"([^"]+)"\s+(?:means|shall mean|is defined as|refers to)\s+([^.]+)',
            r'(?i)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:means|shall mean|is defined as)\s+([^.]+)',
            r'(?i)for purposes of this agreement,\s*"?([^"]+)"?\s+(?:means|shall mean)\s+([^.]+)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) >= 2:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    if len(term) < 50 and len(definition) < 300:  # Reasonable length
                        definitions[term] = definition
        
        return dict(list(definitions.items())[:20])  # Limit to reasonable number
    
    def _extract_governing_clauses(self, content: str) -> List[str]:
        """Extract governing clauses from document content"""
        clauses = []
        
        # Look for governing clause patterns
        clause_patterns = [
            r'(?i)this agreement shall be governed by\s+([^.]+)',
            r'(?i)governing law[:\-]\s*([^.]+)',
            r'(?i)jurisdiction[:\-]\s*([^.]+)',
            r'(?i)disputes shall be resolved\s+([^.]+)'
        ]
        
        for pattern in clause_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                clause = match.group(1).strip()
                if len(clause) < 200:  # Reasonable length
                    clauses.append(clause)
        
        return clauses[:10]  # Limit to reasonable number
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of the document content"""
        lines = content.split('\n')
        
        # Count different types of content
        structure = {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'sections': self._identify_sections(content),
            'has_numbered_sections': bool(re.search(r'^\s*\d+\.', content, re.MULTILINE)),
            'has_bullet_points': bool(re.search(r'^\s*[•\-\*]', content, re.MULTILINE)),
            'paragraph_count': len([para for para in content.split('\n\n') if para.strip()]),
            'average_paragraph_length': 0
        }
        
        # Calculate average paragraph length
        paragraphs = [para.strip() for para in content.split('\n\n') if para.strip()]
        if paragraphs:
            structure['average_paragraph_length'] = sum(len(para.split()) for para in paragraphs) / len(paragraphs)
        
        return structure
    
    def _identify_sections(self, content: str) -> List[str]:
        """Identify document sections"""
        sections = []
        
        # Look for section headers
        section_patterns = [
            r'(?i)^\s*(?:section|article|part)\s+\d+[:\-\.]?\s*([^\n]+)',
            r'(?i)^\s*\d+\.\s*([A-Z][^\n]+)',
            r'(?i)^\s*([A-Z][A-Z\s]+)$'  # All caps headers
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                section = match.group(1).strip()
                if len(section) < 100:  # Reasonable length for a section title
                    sections.append(section)
        
        return sections[:20]  # Limit to reasonable number
    
    def _calculate_confidence_scores(self, content: str, key_info: KeyInformation) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of the analysis"""
        scores = {}
        
        # Content quality score
        word_count = len(content.split())
        scores['content_quality'] = min(1.0, word_count / 1000)  # Higher score for longer documents
        
        # Information extraction scores
        scores['parties_extraction'] = min(1.0, len(key_info.parties) / 5)
        scores['financial_extraction'] = min(1.0, len(key_info.financial_terms) / 10)
        scores['dates_extraction'] = min(1.0, len(key_info.key_dates) / 10)
        scores['obligations_extraction'] = min(1.0, len(key_info.obligations) / 10)
        
        # Overall confidence
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores