"""
Data Formatter for converting any response content into exportable formats.
Handles conversion of various data types into structured formats suitable for Excel export.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class FormattedData:
    """Formatted data ready for export."""
    structured_data: Dict[str, Any]
    export_ready: bool
    format_type: str
    metadata: Dict[str, Any]
    warnings: List[str] = None


class DataFormatter:
    """
    Converts any response content into exportable formats.
    Handles text responses, structured data, Q&A history, and analysis results.
    """
    
    def __init__(self):
        # Patterns for extracting structured information from text
        self.extraction_patterns = {
            'lists': [
                r'(?:^|\n)(?:\d+\.|\*|-|\•)\s*(.+?)(?=\n(?:\d+\.|\*|-|\•)|$)',
                r'(?:^|\n)([A-Z][^:\n]+):\s*([^\n]+)',
                r'(?:^|\n)•\s*(.+?)(?=\n•|$)'
            ],
            'key_value_pairs': [
                r'([A-Z][^:\n]+):\s*([^\n]+)',
                r'(\w+(?:\s+\w+)*)\s*[-–—]\s*([^\n]+)',
                r'(\w+(?:\s+\w+)*)\s*=\s*([^\n]+)'
            ],
            'dates': [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})'
            ],
            'monetary_amounts': [
                r'\$([0-9,]+(?:\.\d{2})?)',
                r'([0-9,]+(?:\.\d{2})?\s*(?:USD|dollars?))',
                r'([0-9,]+(?:\.\d{2})?\s*(?:EUR|euros?))'
            ],
            'percentages': [
                r'(\d+(?:\.\d+)?%)',
                r'(\d+(?:\.\d+)?\s*percent)'
            ]
        }
        
        # Common section headers that indicate structured content
        self.section_headers = [
            'summary', 'overview', 'key points', 'main findings', 'conclusions',
            'recommendations', 'action items', 'next steps', 'risks', 'issues',
            'parties', 'terms', 'dates', 'deadlines', 'obligations', 'benefits',
            'requirements', 'specifications', 'details', 'analysis', 'assessment'
        ]
    
    def format_response_for_export(self, response_content: Any, 
                                 response_type: str = 'text',
                                 context: Dict[str, Any] = None) -> FormattedData:
        """
        Format any response content for export.
        
        Args:
            response_content: The content to format (text, dict, list, etc.)
            response_type: Type of response ('text', 'structured', 'qa_history', etc.)
            context: Additional context about the response
            
        Returns:
            FormattedData object ready for export
        """
        logger.info(f"Formatting {response_type} response for export")
        
        warnings = []
        
        try:
            if response_type == 'text':
                structured_data = self._format_text_response(response_content, context)
            elif response_type == 'structured':
                structured_data = self._format_structured_response(response_content, context)
            elif response_type == 'qa_history':
                structured_data = self._format_qa_history(response_content, context)
            elif response_type == 'analysis_result':
                structured_data = self._format_analysis_result(response_content, context)
            elif response_type == 'contract_analysis':
                structured_data = self._format_contract_analysis(response_content, context)
            elif response_type == 'document_summary':
                structured_data = self._format_document_summary(response_content, context)
            else:
                # Generic formatting
                structured_data = self._format_generic_content(response_content, context)
                warnings.append(f"Unknown response type '{response_type}', using generic formatting")
            
            # Validate and enhance the structured data
            structured_data = self._enhance_structured_data(structured_data, context)
            
            return FormattedData(
                structured_data=structured_data,
                export_ready=True,
                format_type=response_type,
                metadata={
                    'formatted_at': datetime.now().isoformat(),
                    'original_type': type(response_content).__name__,
                    'context': context or {}
                },
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            # Fallback to basic formatting
            fallback_data = self._create_fallback_format(response_content, str(e))
            
            return FormattedData(
                structured_data=fallback_data,
                export_ready=True,
                format_type='fallback',
                metadata={
                    'formatted_at': datetime.now().isoformat(),
                    'error': str(e),
                    'fallback_used': True
                },
                warnings=[f"Formatting failed, using fallback: {str(e)}"]
            )
    
    def _format_text_response(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format plain text response into structured data."""
        if not isinstance(text, str):
            text = str(text)
        
        structured = {
            'response_text': text,
            'extracted_data': {},
            'sections': [],
            'key_information': []
        }
        
        # Extract sections based on headers
        sections = self._extract_sections(text)
        if sections:
            structured['sections'] = sections
        
        # Extract lists and bullet points
        lists = self._extract_lists(text)
        if lists:
            structured['extracted_data']['lists'] = lists
        
        # Extract key-value pairs
        key_values = self._extract_key_value_pairs(text)
        if key_values:
            structured['extracted_data']['key_value_pairs'] = key_values
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            structured['extracted_data']['dates'] = dates
        
        # Extract monetary amounts
        amounts = self._extract_monetary_amounts(text)
        if amounts:
            structured['extracted_data']['monetary_amounts'] = amounts
        
        # Extract percentages
        percentages = self._extract_percentages(text)
        if percentages:
            structured['extracted_data']['percentages'] = percentages
        
        # Create tabular representation
        structured['tabular_data'] = self._create_tabular_from_text(text, structured['extracted_data'])
        
        return structured
    
    def _format_structured_response(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format already structured response data."""
        if not isinstance(data, dict):
            return self._format_generic_content(data, context)
        
        structured = {
            'original_structure': data,
            'tabular_data': [],
            'summary': {},
            'details': {}
        }
        
        # Convert nested dictionaries to tabular format
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                # This is already tabular data
                structured['tabular_data'].append({
                    'sheet_name': key.replace('_', ' ').title(),
                    'data': value
                })
            elif isinstance(value, dict):
                # Convert dict to key-value table
                kv_data = [{'Key': k, 'Value': str(v)} for k, v in value.items()]
                structured['tabular_data'].append({
                    'sheet_name': key.replace('_', ' ').title(),
                    'data': kv_data
                })
            elif isinstance(value, list):
                # Convert list to single-column table
                list_data = [{'Item': str(item)} for item in value]
                structured['tabular_data'].append({
                    'sheet_name': key.replace('_', ' ').title(),
                    'data': list_data
                })
            else:
                # Add to summary
                structured['summary'][key] = str(value)
        
        return structured
    
    def _format_qa_history(self, qa_data: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format Q&A history for export."""
        if not isinstance(qa_data, list):
            qa_data = [qa_data] if qa_data else []
        
        # Format Q&A entries
        formatted_qa = []
        for i, entry in enumerate(qa_data, 1):
            formatted_entry = {
                'Question_Number': i,
                'Question': entry.get('question', ''),
                'Answer': entry.get('answer', ''),
                'Timestamp': entry.get('timestamp', ''),
                'Analysis_Mode': entry.get('analysis_mode', 'Standard'),
                'Confidence': entry.get('confidence', 'N/A'),
                'Sources': ', '.join(entry.get('sources', [])) if entry.get('sources') else 'N/A'
            }
            formatted_qa.append(formatted_entry)
        
        # Create summary statistics
        summary = {
            'Total_Questions': len(qa_data),
            'Analysis_Modes_Used': list(set(entry.get('analysis_mode', 'Standard') for entry in qa_data)),
            'Average_Confidence': self._calculate_average_confidence(qa_data),
            'Session_Duration': self._calculate_session_duration(qa_data)
        }
        
        return {
            'qa_history': formatted_qa,
            'session_summary': [{'Metric': k, 'Value': str(v)} for k, v in summary.items()],
            'tabular_data': [
                {'sheet_name': 'Q&A History', 'data': formatted_qa},
                {'sheet_name': 'Session Summary', 'data': [{'Metric': k, 'Value': str(v)} for k, v in summary.items()]}
            ]
        }
    
    def _format_analysis_result(self, analysis: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format analysis results for export."""
        structured = {
            'analysis_overview': {},
            'detailed_results': [],
            'tabular_data': []
        }
        
        # Extract overview information
        overview_keys = ['summary', 'conclusion', 'recommendation', 'confidence', 'analysis_type']
        for key in overview_keys:
            if key in analysis:
                structured['analysis_overview'][key] = analysis[key]
        
        # Format detailed results
        if 'results' in analysis and isinstance(analysis['results'], list):
            structured['detailed_results'] = analysis['results']
            structured['tabular_data'].append({
                'sheet_name': 'Analysis Results',
                'data': analysis['results']
            })
        
        # Add overview as tabular data
        if structured['analysis_overview']:
            overview_table = [{'Aspect': k, 'Value': str(v)} for k, v in structured['analysis_overview'].items()]
            structured['tabular_data'].append({
                'sheet_name': 'Analysis Overview',
                'data': overview_table
            })
        
        return structured
    
    def _format_contract_analysis(self, contract_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format contract analysis results for export."""
        structured = {
            'contract_overview': {},
            'parties': [],
            'key_terms': [],
            'obligations': [],
            'risks': [],
            'dates': [],
            'tabular_data': []
        }
        
        # Extract contract overview
        overview_keys = ['document_type', 'effective_date', 'expiration_date', 'governing_law']
        for key in overview_keys:
            if key in contract_data:
                structured['contract_overview'][key] = contract_data[key]
        
        # Format parties
        if 'parties' in contract_data:
            parties = contract_data['parties']
            if isinstance(parties, list):
                structured['parties'] = [{'Party': party} for party in parties]
            else:
                structured['parties'] = [{'Party': str(parties)}]
        
        # Format key terms
        if 'key_terms' in contract_data:
            terms = contract_data['key_terms']
            if isinstance(terms, dict):
                structured['key_terms'] = [{'Term': k, 'Definition': str(v)} for k, v in terms.items()]
            elif isinstance(terms, list):
                structured['key_terms'] = [{'Term': str(term)} for term in terms]
        
        # Format obligations
        if 'obligations' in contract_data:
            obligations = contract_data['obligations']
            if isinstance(obligations, list):
                structured['obligations'] = obligations
            else:
                structured['obligations'] = [{'Obligation': str(obligations)}]
        
        # Format risks
        if 'risks' in contract_data:
            risks = contract_data['risks']
            if isinstance(risks, list):
                structured['risks'] = risks
            else:
                structured['risks'] = [{'Risk': str(risks)}]
        
        # Create tabular data
        for key in ['contract_overview', 'parties', 'key_terms', 'obligations', 'risks']:
            if structured[key]:
                sheet_name = key.replace('_', ' ').title()
                if key == 'contract_overview':
                    data = [{'Aspect': k, 'Value': str(v)} for k, v in structured[key].items()]
                else:
                    data = structured[key]
                
                structured['tabular_data'].append({
                    'sheet_name': sheet_name,
                    'data': data
                })
        
        return structured
    
    def _format_document_summary(self, summary_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format document summary for export."""
        structured = {
            'summary_overview': {},
            'key_points': [],
            'recommendations': [],
            'tabular_data': []
        }
        
        # Extract overview
        overview_keys = ['title', 'document_type', 'summary', 'word_count', 'page_count']
        for key in overview_keys:
            if key in summary_data:
                structured['summary_overview'][key] = summary_data[key]
        
        # Format key points
        if 'key_points' in summary_data:
            points = summary_data['key_points']
            if isinstance(points, list):
                structured['key_points'] = [{'Point': str(point)} for point in points]
        
        # Format recommendations
        if 'recommendations' in summary_data:
            recommendations = summary_data['recommendations']
            if isinstance(recommendations, list):
                structured['recommendations'] = [{'Recommendation': str(rec)} for rec in recommendations]
        
        # Create tabular data
        if structured['summary_overview']:
            structured['tabular_data'].append({
                'sheet_name': 'Document Overview',
                'data': [{'Aspect': k, 'Value': str(v)} for k, v in structured['summary_overview'].items()]
            })
        
        if structured['key_points']:
            structured['tabular_data'].append({
                'sheet_name': 'Key Points',
                'data': structured['key_points']
            })
        
        if structured['recommendations']:
            structured['tabular_data'].append({
                'sheet_name': 'Recommendations',
                'data': structured['recommendations']
            })
        
        return structured
    
    def _format_generic_content(self, content: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic formatting for unknown content types."""
        structured = {
            'content': str(content),
            'content_type': type(content).__name__,
            'tabular_data': []
        }
        
        if isinstance(content, dict):
            # Convert dict to key-value table
            table_data = [{'Key': str(k), 'Value': str(v)} for k, v in content.items()]
            structured['tabular_data'].append({
                'sheet_name': 'Data',
                'data': table_data
            })
        elif isinstance(content, list):
            # Convert list to single-column table
            if content and isinstance(content[0], dict):
                # List of dicts - already tabular
                structured['tabular_data'].append({
                    'sheet_name': 'Data',
                    'data': content
                })
            else:
                # List of values
                table_data = [{'Item': str(item)} for item in content]
                structured['tabular_data'].append({
                    'sheet_name': 'Data',
                    'data': table_data
                })
        else:
            # Single value
            structured['tabular_data'].append({
                'sheet_name': 'Data',
                'data': [{'Content': str(content)}]
            })
        
        return structured
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract sections from text based on headers."""
        sections = []
        
        # Look for section headers (lines that end with : or are in ALL CAPS)
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this looks like a header
            is_header = (
                line.endswith(':') or
                (line.isupper() and len(line) > 3) or
                any(header.lower() in line.lower() for header in self.section_headers)
            )
            
            if is_header:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'header': current_section,
                        'content': '\n'.join(current_content)
                    })
                
                # Start new section
                current_section = line.rstrip(':')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections.append({
                'header': current_section,
                'content': '\n'.join(current_content)
            })
        
        return sections
    
    def _extract_lists(self, text: str) -> List[List[str]]:
        """Extract lists from text."""
        lists = []
        
        for pattern in self.extraction_patterns['lists']:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            if matches:
                # Handle both string matches and tuple matches
                clean_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        # Take the first non-empty element from tuple
                        for item in match:
                            if item and item.strip():
                                clean_matches.append(item.strip())
                                break
                    else:
                        clean_matches.append(match.strip())
                
                if clean_matches:
                    lists.append(clean_matches)
        
        return lists
    
    def _extract_key_value_pairs(self, text: str) -> Dict[str, str]:
        """Extract key-value pairs from text."""
        pairs = {}
        
        for pattern in self.extraction_patterns['key_value_pairs']:
            matches = re.findall(pattern, text, re.MULTILINE)
            for key, value in matches:
                pairs[key.strip()] = value.strip()
        
        return pairs
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        
        for pattern in self.extraction_patterns['dates']:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    def _extract_monetary_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text."""
        amounts = []
        
        for pattern in self.extraction_patterns['monetary_amounts']:
            matches = re.findall(pattern, text)
            amounts.extend(matches)
        
        return amounts
    
    def _extract_percentages(self, text: str) -> List[str]:
        """Extract percentages from text."""
        percentages = []
        
        for pattern in self.extraction_patterns['percentages']:
            matches = re.findall(pattern, text)
            percentages.extend(matches)
        
        return percentages
    
    def _create_tabular_from_text(self, text: str, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tabular representation from text and extracted data."""
        tabular = []
        
        # Create a summary table
        summary_data = []
        
        if extracted_data.get('key_value_pairs'):
            for key, value in extracted_data['key_value_pairs'].items():
                summary_data.append({'Type': 'Key-Value', 'Key': key, 'Value': value})
        
        if extracted_data.get('dates'):
            for date in extracted_data['dates']:
                summary_data.append({'Type': 'Date', 'Key': 'Date Found', 'Value': date})
        
        if extracted_data.get('monetary_amounts'):
            for amount in extracted_data['monetary_amounts']:
                summary_data.append({'Type': 'Amount', 'Key': 'Monetary Amount', 'Value': amount})
        
        if extracted_data.get('percentages'):
            for percentage in extracted_data['percentages']:
                summary_data.append({'Type': 'Percentage', 'Key': 'Percentage Found', 'Value': percentage})
        
        if summary_data:
            tabular.append({
                'sheet_name': 'Extracted Information',
                'data': summary_data
            })
        
        # Add lists as separate tables
        if extracted_data.get('lists'):
            for i, list_items in enumerate(extracted_data['lists'], 1):
                list_data = [{'Item': item} for item in list_items]
                tabular.append({
                    'sheet_name': f'List {i}',
                    'data': list_data
                })
        
        return tabular
    
    def _enhance_structured_data(self, structured_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance structured data with additional metadata and formatting."""
        # Add metadata
        structured_data['export_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'data_source': context.get('source', 'Unknown') if context else 'Unknown',
            'format_version': '1.0'
        }
        
        # Ensure all tabular data has proper structure
        if 'tabular_data' in structured_data:
            for table in structured_data['tabular_data']:
                if 'data' in table and table['data']:
                    # Ensure all rows have the same keys
                    if isinstance(table['data'], list) and table['data']:
                        all_keys = set()
                        for row in table['data']:
                            if isinstance(row, dict):
                                all_keys.update(row.keys())
                        
                        # Fill missing keys with empty values
                        for row in table['data']:
                            if isinstance(row, dict):
                                for key in all_keys:
                                    if key not in row:
                                        row[key] = ''
        
        return structured_data
    
    def _create_fallback_format(self, content: Any, error_message: str) -> Dict[str, Any]:
        """Create fallback format when normal formatting fails."""
        return {
            'fallback_content': str(content),
            'error_message': error_message,
            'tabular_data': [{
                'sheet_name': 'Content',
                'data': [{'Content': str(content), 'Error': error_message}]
            }],
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'fallback_used': True,
                'original_error': error_message
            }
        }
    
    def _calculate_average_confidence(self, qa_data: List[Dict[str, Any]]) -> str:
        """Calculate average confidence from Q&A data."""
        confidences = []
        for entry in qa_data:
            confidence = entry.get('confidence')
            if confidence and isinstance(confidence, (int, float)):
                confidences.append(confidence)
        
        if confidences:
            avg = sum(confidences) / len(confidences)
            return f"{avg:.1%}"
        return "N/A"
    
    def _calculate_session_duration(self, qa_data: List[Dict[str, Any]]) -> str:
        """Calculate session duration from Q&A data."""
        timestamps = []
        for entry in qa_data:
            timestamp = entry.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = timestamp
                    timestamps.append(dt)
                except:
                    continue
        
        if len(timestamps) >= 2:
            duration = max(timestamps) - min(timestamps)
            return str(duration)
        return "N/A"