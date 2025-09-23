"""Enhanced Q&A Interface with comprehensive analysis, conversational AI, and Excel generation."""

import streamlit as st
import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.services.qa_engine import QAEngine, create_qa_engine
from src.services.contract_analyst_engine import ContractAnalystEngine, create_contract_analyst_engine
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.services.excel_export_engine import ExcelExportEngine
from src.services.request_analyzer import RequestAnalyzer
from src.services.data_formatter import DataFormatter
from src.services.template_engine import TemplateEngine
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.storage.document_storage import DocumentStorage
from src.storage.enhanced_storage import enhanced_storage
from src.storage.migrations import migrator
from src.models.document import Document, QASession, AnalysisTemplate
from src.models.conversational import ConversationContext
from src.config import config
from src.ui.styling import UIStyler
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedQAInterface:
    """Enhanced Streamlit interface for document Q&A with comprehensive analysis capabilities."""
    
    def __init__(self):
        self.storage = DocumentStorage()
        self.enhanced_storage = enhanced_storage
        self.qa_engine = None
        self.contract_engine = None
        self.enhanced_analyzer = None
        self.conversational_engine = None
        self.excel_generator = None
        self.excel_export_engine = None
        self.request_analyzer = None
        self.data_formatter = None
        self.template_engine = None
        self.enhanced_router = None
        
        # Run database migrations on initialization
        self._ensure_database_ready()
        
        # Initialize session state
        if 'qa_sessions' not in st.session_state:
            st.session_state.qa_sessions = {}
        if 'current_qa_session' not in st.session_state:
            st.session_state.current_qa_session = None
        if 'selected_document' not in st.session_state:
            st.session_state.selected_document = None
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'standard'
        if 'legal_document_info' not in st.session_state:
            st.session_state.legal_document_info = {}
        if 'enhanced_summary_visible' not in st.session_state:
            st.session_state.enhanced_summary_visible = False
        if 'selected_template' not in st.session_state:
            st.session_state.selected_template = None
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {}
        if 'excel_reports' not in st.session_state:
            st.session_state.excel_reports = []
        if 'enhanced_mode_enabled' not in st.session_state:
            st.session_state.enhanced_mode_enabled = True  # Enable enhanced mode by default
        if 'conversation_context_persistence' not in st.session_state:
            st.session_state.conversation_context_persistence = {}
    
    def _ensure_database_ready(self):
        """Ensure database schema is up to date."""
        try:
            migrator.run_migrations()
        except Exception as e:
            st.error(f"Database migration failed: {e}")
            st.stop()
    
    def _ensure_engines_initialized(self):
        """Ensure all engines are properly initialized."""
        try:
            # Initialize QA engine if needed
            if not self.qa_engine:
                from src.services.qa_engine import QAEngine
                import os
                api_key = os.getenv('GEMINI_API_KEY', 'test_key')
                self.qa_engine = QAEngine(self.storage, api_key)
            
            # Initialize contract engine if needed
            if not self.contract_engine:
                from src.services.contract_analyst_engine import ContractAnalystEngine
                import os
                api_key = os.getenv('GEMINI_API_KEY', 'test_key')
                self.contract_engine = ContractAnalystEngine(self.storage, api_key)
            
            # Initialize enhanced router if needed and enhanced mode is enabled
            if st.session_state.enhanced_mode_enabled and not self.enhanced_router:
                try:
                    from src.services.enhanced_response_router import EnhancedResponseRouter
                    import os
                    api_key = os.getenv('GEMINI_API_KEY', 'test_key')
                    self.enhanced_router = EnhancedResponseRouter(self.storage, api_key)
                except Exception as e:
                    logger.warning(f"Could not initialize enhanced router: {e}")
                    # Disable enhanced mode if initialization fails
                    st.session_state.enhanced_mode_enabled = False
                    
        except Exception as e:
            logger.error(f"Error initializing engines: {e}")
            # Fallback to basic functionality
            st.session_state.enhanced_mode_enabled = False
    
    def render_qa_interface(self, document_id: Optional[str] = None) -> None:
        """
        Render the enhanced Q&A interface with comprehensive analysis capabilities.
        
        Args:
            document_id: Optional document ID to start Q&A with
        """
        # Get API key with enhanced error display
        api_key = config.get_gemini_api_key()
        if not api_key:
            st.error(f"{UIStyler.get_icon('error')} Gemini API key not configured. Please set GEMINI_API_KEY in your environment.")
            st.info(f"{UIStyler.get_icon('info')} You can get an API key from: https://makersuite.google.com/app/apikey")
            return
        
        # Initialize all engines
        if not self.qa_engine:
            self.qa_engine = create_qa_engine(api_key, self.storage)
        if not self.contract_engine:
            self.contract_engine = create_contract_analyst_engine(api_key, self.storage)
        if not self.enhanced_analyzer:
            self.enhanced_analyzer = EnhancedSummaryAnalyzer(self.storage, api_key)
        if not self.conversational_engine:
            self.conversational_engine = ConversationalAIEngine(self.qa_engine, self.contract_engine)
        if not self.excel_generator:
            self.excel_generator = ExcelReportGenerator(self.storage)
        if not self.excel_export_engine:
            self.excel_export_engine = ExcelExportEngine(self.storage)
        if not self.request_analyzer:
            self.request_analyzer = RequestAnalyzer()
        if not self.data_formatter:
            self.data_formatter = DataFormatter()
        if not self.template_engine:
            self.template_engine = TemplateEngine(self.storage)
        if not self.enhanced_router:
            self.enhanced_router = EnhancedResponseRouter(self.storage, api_key)
        
        # Ensure backward compatibility
        self._ensure_backward_compatibility()
        
        # Document selection section
        selected_doc = self._render_document_selector(document_id)
        
        if not selected_doc:
            st.info("👆 Please select a document to start asking questions.")
            return
        
        # Enhanced mode configuration
        self._render_enhanced_mode_configuration()
        
        # Enhanced summary section
        self._render_enhanced_summary_section(selected_doc)
        
        # Template selection section
        self._render_template_selection(selected_doc)
        
        # Q&A session section with enhanced routing
        self._render_enhanced_qa_session(selected_doc)
        
        # Enhanced Excel export section
        self._render_enhanced_export_section(selected_doc)
    
    def _render_document_selector(self, preselected_doc_id: Optional[str] = None) -> Optional[Document]:
        """Render document selection interface with enhanced visual indicators."""
        st.subheader(f"{UIStyler.get_icon('documents')} Select Document")
        
        # Get processed documents
        processed_docs = self.storage.list_documents(status_filter='completed')
        
        if not processed_docs:
            st.warning(f"{UIStyler.get_icon('warning')} No processed documents available. Please upload and process documents first.")
            return None
        
        # Create document options with enhanced icons
        doc_options = {}
        for doc in processed_docs:
            file_icon = UIStyler.get_icon(doc.file_type)
            display_name = f"{file_icon} {doc.title} ({doc.file_type.upper()}) - {doc.created_at.strftime('%Y-%m-%d %H:%M')}"
            doc_options[display_name] = doc
        
        # Document selection
        if preselected_doc_id:
            # Find preselected document
            preselected_doc = next((doc for doc in processed_docs if doc.id == preselected_doc_id), None)
            if preselected_doc:
                preselected_name = next((name for name, doc in doc_options.items() if doc.id == preselected_doc_id), None)
                if preselected_name:
                    default_index = list(doc_options.keys()).index(preselected_name)
                else:
                    default_index = 0
            else:
                default_index = 0
        else:
            default_index = 0
        
        selected_name = st.selectbox(
            "Choose a document:",
            options=list(doc_options.keys()),
            index=default_index,
            key="document_selector"
        )
        
        selected_doc = doc_options[selected_name]
        
        # Detect legal document and set analysis mode
        self._detect_and_set_analysis_mode(selected_doc)
        
        # Display enhanced document info with legal document indicators
        with st.expander(f"{UIStyler.get_icon('info')} Document Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{UIStyler.get_icon('documents')} Title:** {selected_doc.title}")
                
                # Show legal document type if detected
                if selected_doc.is_legal_document or st.session_state.legal_document_info.get(selected_doc.id, {}).get('is_legal'):
                    legal_info = st.session_state.legal_document_info.get(selected_doc.id, {})
                    legal_type = selected_doc.legal_document_type or legal_info.get('document_type', 'Legal Document')
                    confidence = selected_doc.legal_analysis_confidence or legal_info.get('confidence', 0.0)
                    st.write(f"**{UIStyler.get_icon('success')} Legal Document:** {legal_type} (Confidence: {confidence:.1%})")
                    
                    # Show contract analysis badge
                    st.success(f"🏛️ **Contract Analysis Mode Active**")
                else:
                    st.write(f"**{UIStyler.get_icon('info')} Type:** {selected_doc.document_type or 'Unknown'}")
                
                st.write(f"**{UIStyler.get_icon(selected_doc.file_type)} File Format:** {selected_doc.file_type.upper()}")
                st.write(f"**{UIStyler.get_icon('metrics')} Size:** {selected_doc.file_size:,} bytes")
            
            with col2:
                st.write(f"**{UIStyler.get_icon('upload')} Uploaded:** {selected_doc.upload_timestamp.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**{UIStyler.get_icon('processing')} Processed:** {selected_doc.updated_at.strftime('%Y-%m-%d %H:%M')}")
                status_badge = UIStyler.create_status_badge(selected_doc.processing_status)
                st.write(f"**Status:** {status_badge}")
                
                # Show analysis mode
                mode_icon = "🏛️" if st.session_state.analysis_mode == 'contract' else "💬"
                mode_text = "Contract Analysis" if st.session_state.analysis_mode == 'contract' else "Standard Q&A"
                st.write(f"**{mode_icon} Analysis Mode:** {mode_text}")
            
            if selected_doc.summary:
                st.write(f"**{UIStyler.get_icon('info')} Summary:**")
                st.write(selected_doc.summary)
            
            # Show legal terms if available
            legal_info = st.session_state.legal_document_info.get(selected_doc.id, {})
            if legal_info.get('legal_terms'):
                st.write(f"**🏛️ Key Legal Terms Found:**")
                st.write(", ".join(legal_info['legal_terms'][:10]))  # Show first 10 terms
        
        # Store selected document in session state
        st.session_state.selected_document = selected_doc.id
        
        return selected_doc
    
    def _render_enhanced_mode_configuration(self) -> None:
        """Render enhanced mode configuration toggles."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🚀 Enhanced Assistant Configuration")
        
        with col2:
            enhanced_enabled = st.toggle(
                "Enhanced Mode", 
                value=st.session_state.enhanced_mode_enabled,
                help="Enable enhanced conversational AI with fallback responses and context awareness"
            )
            st.session_state.enhanced_mode_enabled = enhanced_enabled
        
        with col3:
            if enhanced_enabled:
                st.success("🚀 Enhanced")
            else:
                st.info("📝 Standard")
        
        if enhanced_enabled:
            st.info("🚀 **Enhanced Mode Active** - The assistant will provide graceful responses to off-topic questions, maintain conversation context, and offer specialized MTA expertise when applicable.")
        else:
            st.info("📝 **Standard Mode** - Traditional document Q&A with structured contract analysis for legal documents.")
    
    def _detect_and_set_analysis_mode(self, document: Document) -> None:
        """Detect if document is legal and set appropriate analysis mode."""
        # Check if we already have legal document info for this document
        if document.id not in st.session_state.legal_document_info:
            # Use contract engine to detect legal document
            if self.contract_engine:
                is_legal, doc_type, confidence = self.contract_engine.detect_legal_document(document)
                
                # Store legal document information
                st.session_state.legal_document_info[document.id] = {
                    'is_legal': is_legal,
                    'document_type': doc_type,
                    'confidence': confidence,
                    'legal_terms': self.contract_engine.extract_legal_terms(document.original_text or "") if is_legal else []
                }
                
                # Update document model if not already set
                if is_legal and not document.is_legal_document:
                    document.is_legal_document = is_legal
                    document.legal_document_type = doc_type
                    document.legal_analysis_confidence = confidence
                    # Note: In a real implementation, you might want to save this to the database
        
        # Set analysis mode based on legal document detection
        legal_info = st.session_state.legal_document_info.get(document.id, {})
        if document.is_legal_document or legal_info.get('is_legal', False):
            st.session_state.analysis_mode = 'contract'
        else:
            st.session_state.analysis_mode = 'standard'
    
    def _render_qa_session(self, document: Document) -> None:
        """Render Q&A session interface for the selected document."""
        # Show analysis mode header
        if st.session_state.analysis_mode == 'contract':
            st.subheader(f"🏛️ Contract Analysis - Ask Questions")
            st.info("**Contract Analysis Mode Active** - Responses will be structured with Direct Evidence, Plain-English Explanation, and Implication/Analysis sections.")
        else:
            st.subheader(f"{UIStyler.get_icon('qa')} Ask Questions")
        
        # Get or create Q&A session
        session_id = self._get_or_create_session(document.id)
        
        # Use appropriate engine based on analysis mode
        engine = self.contract_engine if st.session_state.analysis_mode == 'contract' else self.qa_engine
        session = engine.get_qa_session(session_id)
        
        # Display chat history
        self._render_chat_history(session)
        
        # Question input
        self._render_question_input(document, session_id)
        
        # Session management
        self._render_session_management(document.id)
    
    def _get_or_create_session(self, document_id: str) -> str:
        """Get existing session or create new one for the document."""
        analysis_mode = st.session_state.analysis_mode
        session_key = f"session_{document_id}_{analysis_mode}"
        
        if session_key not in st.session_state.qa_sessions:
            # Create new session using appropriate engine
            engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
            session_id = engine.create_qa_session(document_id)
            st.session_state.qa_sessions[session_key] = session_id
        
        return st.session_state.qa_sessions[session_key]
    
    def _render_chat_history(self, session: Optional[QASession]) -> None:
        """Render chat history for the session with support for structured responses."""
        if not session or not session.questions:
            if st.session_state.analysis_mode == 'contract':
                st.info(f"🏛️ Start by asking a question about this legal document! Try questions about parties, obligations, or key terms.")
            else:
                st.info(f"{UIStyler.get_icon('info')} Start by asking a question about the document!")
            return
        
        st.write(f"**{UIStyler.get_icon('history')} Conversation History:**")
        
        # Display questions and answers
        for i, interaction in enumerate(session.questions):
            # Question
            with st.chat_message("user"):
                st.write(interaction['question'])
            
            # Answer
            with st.chat_message("assistant"):
                # Check if this is a structured contract analysis response
                if interaction.get('analysis_mode') == 'contract' and interaction.get('structured_response'):
                    self._render_structured_response(interaction['structured_response'])
                else:
                    st.write(interaction['answer'])
                
                # Show sources if available with enhanced icon
                if interaction.get('sources'):
                    with st.expander(f"{UIStyler.get_icon('documents')} Sources", expanded=False):
                        for source in interaction['sources']:
                            st.write(f"{UIStyler.get_icon('info')} {source}")
                
                # Show legal terms found (for contract analysis)
                if interaction.get('legal_terms_found'):
                    with st.expander("🏛️ Legal Terms Identified", expanded=False):
                        st.write(", ".join(interaction['legal_terms_found']))
                
                # Show analysis mode indicator
                if interaction.get('analysis_mode'):
                    mode_icon = "🏛️" if interaction['analysis_mode'] == 'contract' else "💬"
                    mode_text = "Contract Analysis" if interaction['analysis_mode'] == 'contract' else "Standard Q&A"
                    st.caption(f"{mode_icon} {mode_text}")
                
                # Show timestamp
                if interaction.get('timestamp'):
                    timestamp = datetime.fromisoformat(interaction['timestamp'])
                    st.caption(f"Answered at {timestamp.strftime('%H:%M:%S')}")
    
    def _render_structured_response(self, structured_response: Dict[str, str]) -> None:
        """Render a structured contract analysis response with clear section headers."""
        if structured_response.get('direct_evidence'):
            st.markdown("### 📋 Direct Evidence")
            st.write(structured_response['direct_evidence'])
        
        if structured_response.get('plain_explanation'):
            st.markdown("### 💡 Plain-English Explanation")
            st.write(structured_response['plain_explanation'])
        
        if structured_response.get('implication_analysis'):
            st.markdown("### ⚖️ Implication/Analysis")
            st.write(structured_response['implication_analysis'])
    
    def _render_question_input(self, document: Document, session_id: str) -> None:
        """Render question input interface."""
        # Question input form
        with st.form("question_form", clear_on_submit=True):
            question = st.text_area(
                "Ask a question about the document:",
                placeholder="e.g., What are the main points discussed in this document?",
                height=100,
                key="question_input"
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button("🤔 Ask Question", type="primary")
            
            with col2:
                example_button = st.form_submit_button("💡 Show Examples")
        
        # Handle question submission
        if submit_button and question.strip():
            self._process_question(question.strip(), document, session_id)
        
        # Handle example questions
        if example_button:
            self._show_example_questions(document)
    
    def _process_question(self, question: str, document: Document, session_id: str) -> None:
        """Process a user question and display the answer."""
        # Analyze request for export needs
        request_analysis = self.request_analyzer.analyze_request(
            question, 
            context={
                'document_id': document.id,
                'analysis_mode': st.session_state.analysis_mode,
                'has_structured_data': True
            }
        )
        
        # Check if enhanced mode is enabled and try it first
        if st.session_state.enhanced_mode_enabled:
            self._process_enhanced_question(question, document, session_id, request_analysis)
        else:
            self._process_standard_question(question, document, session_id, request_analysis)
    
    def _process_enhanced_question(self, question: str, document: Document, session_id: str, request_analysis) -> None:
        """Process question with enhanced export capabilities."""
        analysis_mode = st.session_state.analysis_mode
        spinner_text = "🏛️ Analyzing legal document..." if analysis_mode == 'contract' else "🤔 Thinking about your question..."
        
        with st.spinner(spinner_text):
            try:
                # Initialize engines if needed
                self._ensure_engines_initialized()
                
                # Use enhanced router for better responses
                if self.enhanced_router:
                    result = self.enhanced_router.route_and_respond(question, document.id, session_id)
                else:
                    # Fallback to standard processing
                    engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
                    result = engine.answer_question(question, document.id, session_id)
                
                # Display the answer
                if result.get('error'):
                    st.error(f"❌ {result['answer']}")
                else:
                    success_text = "✅ Analysis complete!" 
                    st.success(success_text)
                    
                    # Show answer in chat format
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        # Display structured response for contract analysis
                        if result.get('structured_response'):
                            self._render_structured_response(result['structured_response'])
                        else:
                            st.write(result['answer'])
                        
                        # Show sources
                        if result.get('sources'):
                            with st.expander("📚 Sources", expanded=True):
                                for source in result['sources']:
                                    st.write(f"• {source}")
                        
                        # Show export options if request analysis suggests it
                        if request_analysis.should_generate_export:
                            self._render_export_options(result, request_analysis, document)
                
                # Refresh to show updated conversation
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error in enhanced question processing: {e}")
                st.error(f"❌ Error processing question: {str(e)}")
    
    def _process_standard_question(self, question: str, document: Document, session_id: str, request_analysis=None) -> None:
        """Process question using standard contract analysis."""
        analysis_mode = st.session_state.analysis_mode
        spinner_text = "🏛️ Analyzing legal document..." if analysis_mode == 'contract' else "🤔 Thinking about your question..."
        
        with st.spinner(spinner_text):
            try:
                # Initialize engines if needed
                self._ensure_engines_initialized()
                
                # Use appropriate engine based on analysis mode
                engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
                
                if not engine:
                    st.error("❌ Analysis engine not available. Please try again.")
                    return
                
                result = engine.answer_question(question, document.id, session_id)
                
                # Display the answer
                if result.get('error'):
                    st.error(f"❌ {result['answer']}")
                else:
                    success_text = "✅ Contract analysis complete!" if analysis_mode == 'contract' else "✅ Answer generated!"
                    st.success(success_text)
                    
                    # Show answer in chat format
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        # Display structured response for contract analysis
                        if result.get('structured_response'):
                            self._render_structured_response(result['structured_response'])
                        else:
                            st.write(result['answer'])
                        
                        # Show sources
                        if result.get('sources'):
                            with st.expander("📚 Sources", expanded=True):
                                for source in result['sources']:
                                    st.write(f"• {source}")
                        
                        # Show legal terms found (for contract analysis)
                        if result.get('legal_terms_found'):
                            with st.expander("🏛️ Legal Terms Identified", expanded=False):
                                st.write(", ".join(result['legal_terms_found']))
                        
                        # Show document type for contract analysis
                        if result.get('document_type') and analysis_mode == 'contract':
                            st.caption(f"🏛️ Document Type: {result['document_type']}")
                        
                        # Show analysis mode
                        mode_icon = "🏛️" if analysis_mode == 'contract' else "💬"
                        mode_text = "Contract Analysis" if analysis_mode == 'contract' else "Standard Q&A"
                        st.caption(f"{mode_icon} {mode_text}")
                        
                        # Show confidence if available
                        if 'confidence' in result:
                            confidence = result['confidence']
                            if confidence > 0.7:
                                st.success(f"Confidence: {confidence:.1%}")
                            elif confidence > 0.4:
                                st.warning(f"Confidence: {confidence:.1%}")
                            else:
                                st.error(f"Low confidence: {confidence:.1%}")
                        
                        # Show export options if request analysis suggests it
                        if request_analysis and request_analysis.should_generate_export:
                            self._render_export_options(result, request_analysis, document)
                
                # Refresh to show updated conversation
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error in standard question processing: {e}")
                st.error(f"❌ Error processing question: {str(e)}")
    
    def _show_example_questions(self, document: Document) -> None:
        """Show example questions based on document type and analysis mode."""
        st.subheader("💡 Example Questions")
        
        # Contract-specific examples for legal documents
        if st.session_state.analysis_mode == 'contract':
            legal_info = st.session_state.legal_document_info.get(document.id, {})
            doc_type = legal_info.get('document_type', 'Legal Document')
            
            st.info(f"🏛️ **Contract Analysis Mode** - Questions optimized for {doc_type}")
            
            # MTA-specific examples
            if doc_type == 'MTA':
                mta_examples = [
                    "Who are the parties to this Material Transfer Agreement?",
                    "What materials are being transferred?",
                    "What are the permitted uses of the materials?",
                    "Who owns the intellectual property rights?",
                    "What are the reporting requirements?",
                    "Are there any restrictions on publication?",
                    "What happens to derivative materials?",
                    "Who benefits more from this agreement?",
                    "What are the liability terms?",
                    "Can the materials be shared with third parties?"
                ]
                
                st.write("**🧬 MTA-Specific Questions:**")
                for example in mta_examples:
                    if st.button(f"🏛️ {example}", key=f"mta_{hash(example)}"):
                        st.session_state.question_input = example
                        st.rerun()
            
            # General legal document examples
            legal_examples = [
                "Who are the parties involved in this agreement?",
                "What are the key obligations of each party?",
                "What are the termination conditions?",
                "Who bears the liability in case of disputes?",
                "What are the intellectual property provisions?",
                "Are there any confidentiality requirements?",
                "What governing law applies?",
                "What are the payment terms?",
                "Who benefits more from this arrangement?",
                "What risks does each party face?"
            ]
            
            st.write("**🏛️ Legal Document Questions:**")
            for example in legal_examples:
                if st.button(f"⚖️ {example}", key=f"legal_{hash(example)}"):
                    st.session_state.question_input = example
                    st.rerun()
        
        else:
            # Standard Q&A examples
            general_examples = [
                "What is the main topic of this document?",
                "Can you summarize the key points?",
                "What are the most important findings?",
                "Are there any action items mentioned?",
                "What dates or deadlines are mentioned?"
            ]
            
            # Document type specific examples
            type_specific = {
                'Technical Documentation': [
                    "What are the system requirements?",
                    "How do I configure this system?",
                    "What are the troubleshooting steps?",
                    "Are there any known limitations?"
                ],
                'Business Document': [
                    "What are the financial implications?",
                    "What decisions need to be made?",
                    "Who are the stakeholders?",
                    "What are the next steps?"
                ],
                'Academic Paper': [
                    "What is the research methodology?",
                    "What are the main conclusions?",
                    "What are the limitations of this study?",
                    "What future research is suggested?"
                ]
            }
            
            # Show examples
            st.write("**💬 General Questions:**")
            for example in general_examples:
                if st.button(f"📝 {example}", key=f"general_{hash(example)}"):
                    st.session_state.question_input = example
                    st.rerun()
            
            # Show type-specific examples if document type is known
            doc_type = document.document_type
            if doc_type and any(key in doc_type for key in type_specific.keys()):
                matching_type = next((key for key in type_specific.keys() if key in doc_type), None)
                if matching_type:
                    st.write(f"**{matching_type} Questions:**")
                    for example in type_specific[matching_type]:
                        if st.button(f"📝 {example}", key=f"specific_{hash(example)}"):
                            st.session_state.question_input = example
                            st.rerun()
    
    def _render_session_management(self, document_id: str) -> None:
        """Render session management controls with contract analysis context."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 New Session", help="Start a fresh conversation"):
                analysis_mode = st.session_state.analysis_mode
                session_key = f"session_{document_id}_{analysis_mode}"
                if session_key in st.session_state.qa_sessions:
                    del st.session_state.qa_sessions[session_key]
                st.success("New session started!")
                st.rerun()
        
        with col2:
            # Get current session info
            analysis_mode = st.session_state.analysis_mode
            session_key = f"session_{document_id}_{analysis_mode}"
            if session_key in st.session_state.qa_sessions:
                session_id = st.session_state.qa_sessions[session_key]
                engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
                session = engine.get_qa_session(session_id)
                if session:
                    question_count = len(session.questions)
                    mode_icon = "🏛️" if analysis_mode == 'contract' else "💬"
                    st.info(f"{mode_icon} {question_count} questions in this session")
        
        with col3:
            # Show session history for both modes
            standard_sessions = self.qa_engine.get_document_qa_sessions(document_id)
            contract_sessions = self.contract_engine.get_document_qa_sessions(document_id)
            total_sessions = len(standard_sessions) + len(contract_sessions)
            
            if total_sessions > 1:
                st.info(f"📚 {total_sessions} total sessions for this document")
                
                # Show breakdown if both modes have sessions
                if len(standard_sessions) > 0 and len(contract_sessions) > 0:
                    st.caption(f"💬 {len(standard_sessions)} standard, 🏛️ {len(contract_sessions)} contract")
    
    # Enhanced Q&A Interface Methods
    
    def _render_enhanced_summary_section(self, document: Document) -> None:
        """Render enhanced summary section with risk assessment and comprehensive analysis."""
        st.markdown("---")
        
        # Enhanced summary header with toggle
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🔍 Enhanced Document Analysis")
        
        with col2:
            if st.button("📊 Generate Analysis", help="Generate comprehensive analysis"):
                self._generate_comprehensive_analysis(document)
        
        with col3:
            show_summary = st.toggle("Show Analysis", value=st.session_state.enhanced_summary_visible)
            st.session_state.enhanced_summary_visible = show_summary
        
        if show_summary:
            # Get existing analysis or show placeholder
            analysis = self.enhanced_storage.get_document_analysis(document.id)
            
            if analysis:
                self._display_comprehensive_analysis(analysis)
            else:
                st.info("🔍 No comprehensive analysis available. Click 'Generate Analysis' to create one.")
    
    def _generate_comprehensive_analysis(self, document: Document) -> None:
        """Generate comprehensive analysis for the document."""
        with st.spinner("🔍 Generating comprehensive analysis..."):
            try:
                # Get selected template
                template = None
                if st.session_state.selected_template:
                    template = self.enhanced_storage.get_analysis_template(st.session_state.selected_template)
                
                # Generate analysis
                analysis = self.enhanced_analyzer.analyze_document_comprehensive(document, template)
                
                # Save to database
                self.enhanced_storage.save_comprehensive_analysis(analysis)
                
                st.success("✅ Comprehensive analysis generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating analysis: {str(e)}")
    
    def _display_comprehensive_analysis(self, analysis) -> None:
        """Display comprehensive analysis results."""
        # Create tabs for different analysis sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Overview", "⚠️ Risks", "📝 Commitments", "📅 Dates", "🔑 Key Terms"
        ])
        
        with tab1:
            self._display_analysis_overview(analysis)
        
        with tab2:
            self._display_risk_assessment(analysis.risks)
        
        with tab3:
            self._display_commitments(analysis.commitments)
        
        with tab4:
            self._display_deliverable_dates(analysis.deliverable_dates)
        
        with tab5:
            self._display_key_terms(analysis.key_legal_terms)
    
    def _display_analysis_overview(self, analysis) -> None:
        """Display analysis overview section."""
        st.markdown("### 📋 Document Overview")
        st.write(analysis.document_overview)
        
        if analysis.key_findings:
            st.markdown("### 🔍 Key Findings")
            for i, finding in enumerate(analysis.key_findings, 1):
                st.write(f"{i}. {finding}")
        
        if analysis.critical_information:
            st.markdown("### ⚠️ Critical Information")
            for i, info in enumerate(analysis.critical_information, 1):
                st.warning(f"{i}. {info}")
        
        if analysis.recommended_actions:
            st.markdown("### 📋 Recommended Actions")
            for i, action in enumerate(analysis.recommended_actions, 1):
                st.write(f"{i}. {action}")
        
        if analysis.executive_recommendation:
            st.markdown("### 🎯 Executive Recommendation")
            st.info(analysis.executive_recommendation)
        
        # Show confidence score
        confidence_color = "green" if analysis.confidence_score > 0.7 else "orange" if analysis.confidence_score > 0.4 else "red"
        st.markdown(f"**Confidence Score:** :{confidence_color}[{analysis.confidence_score:.1%}]")
    
    def _display_risk_assessment(self, risks: List) -> None:
        """Display risk assessment section."""
        if not risks:
            st.info("No risks identified in this document.")
            return
        
        # Risk summary
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        for risk in risks:
            risk_counts[risk.severity] = risk_counts.get(risk.severity, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Risks", len(risks))
        with col2:
            st.metric("High Risk", risk_counts["High"], delta=None if risk_counts["High"] == 0 else "⚠️")
        with col3:
            st.metric("Medium Risk", risk_counts["Medium"])
        with col4:
            st.metric("Low Risk", risk_counts["Low"])
        
        # Risk details
        for risk in risks:
            severity_color = {"High": "red", "Medium": "orange", "Low": "green"}[risk.severity]
            
            with st.expander(f":{severity_color}[{risk.severity}] {risk.description[:100]}..."):
                st.write(f"**Category:** {risk.category}")
                st.write(f"**Affected Parties:** {', '.join(risk.affected_parties)}")
                
                if risk.mitigation_suggestions:
                    st.write("**Mitigation Suggestions:**")
                    for suggestion in risk.mitigation_suggestions:
                        st.write(f"• {suggestion}")
                
                st.write(f"**Source:** {risk.source_text[:200]}...")
                st.write(f"**Confidence:** {risk.confidence:.1%}")
    
    def _display_commitments(self, commitments: List) -> None:
        """Display commitments section."""
        if not commitments:
            st.info("No commitments identified in this document.")
            return
        
        # Commitments summary
        active_commitments = [c for c in commitments if c.status == "Active"]
        upcoming_deadlines = [c for c in commitments if c.deadline and c.deadline > datetime.now()]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Commitments", len(commitments))
        with col2:
            st.metric("Active Commitments", len(active_commitments))
        
        # Commitments table
        if commitments:
            commitment_data = []
            for commitment in commitments:
                commitment_data.append({
                    "Description": commitment.description[:50] + "..." if len(commitment.description) > 50 else commitment.description,
                    "Obligated Party": commitment.obligated_party,
                    "Beneficiary": commitment.beneficiary_party,
                    "Deadline": commitment.deadline.strftime("%Y-%m-%d") if commitment.deadline else "No deadline",
                    "Status": commitment.status,
                    "Type": commitment.commitment_type
                })
            
            st.dataframe(commitment_data, use_container_width=True)
    
    def _display_deliverable_dates(self, dates: List) -> None:
        """Display deliverable dates section."""
        if not dates:
            st.info("No important dates identified in this document.")
            return
        
        # Dates summary
        upcoming_dates = [d for d in dates if d.date > datetime.now()]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Dates", len(dates))
        with col2:
            st.metric("Upcoming Dates", len(upcoming_dates))
        
        # Dates timeline
        if dates:
            date_data = []
            for date in sorted(dates, key=lambda x: x.date):
                status_icon = "🔴" if date.date < datetime.now() else "🟡" if date.date < datetime.now().replace(day=datetime.now().day + 30) else "🟢"
                date_data.append({
                    "Date": date.date.strftime("%Y-%m-%d"),
                    "Description": date.description,
                    "Responsible Party": date.responsible_party,
                    "Type": date.deliverable_type,
                    "Status": f"{status_icon} {date.status}"
                })
            
            st.dataframe(date_data, use_container_width=True)
    
    def _display_key_terms(self, terms: List[str]) -> None:
        """Display key legal terms section."""
        if not terms:
            st.info("No key legal terms identified in this document.")
            return
        
        # Display terms in a grid
        cols = st.columns(3)
        for i, term in enumerate(terms):
            with cols[i % 3]:
                st.write(f"• {term}")
    
    def _render_template_selection(self, document: Document) -> None:
        """Render template selection interface."""
        st.markdown("---")
        st.subheader("📋 Analysis Templates")
        
        # Get available templates
        templates = self.enhanced_storage.list_analysis_templates()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if templates:
                template_options = {"Default Analysis": None}
                for template in templates:
                    template_options[f"{template.name} - {template.description}"] = template.template_id
                
                selected_template_name = st.selectbox(
                    "Choose analysis template:",
                    options=list(template_options.keys()),
                    help="Select a template to customize the analysis focus"
                )
                
                st.session_state.selected_template = template_options[selected_template_name]
            else:
                st.info("No custom templates available. Using default analysis.")
        
        with col2:
            if st.button("➕ Create Template"):
                self._show_template_creation_dialog()
        
        with col3:
            if templates and st.button("📝 Manage Templates"):
                self._show_template_management()
    
    def _render_enhanced_qa_session(self, document: Document) -> None:
        """Render enhanced Q&A session with conversational AI capabilities."""
        st.markdown("---")
        
        # Show analysis mode header with conversational indicator
        if st.session_state.analysis_mode == 'contract':
            st.subheader("🏛️ Contract Analysis - Conversational Q&A")
            st.info("**Enhanced Mode Active** - Natural conversation with legal analysis capabilities")
        else:
            st.subheader("💬 Conversational Q&A")
            st.info("**Conversational Mode** - Ask questions naturally, I'll understand context and provide detailed responses")
        
        # Get or create Q&A session
        session_id = self._get_or_create_session(document.id)
        
        # Use conversational engine for enhanced interactions
        session = self._get_enhanced_session(session_id)
        
        # Display enhanced chat history
        self._render_enhanced_chat_history(session, document)
        
        # Enhanced question input with conversation features
        self._render_enhanced_question_input(document, session_id)
        
        # Session management with conversation context
        self._render_enhanced_session_management(document.id, session_id)
    
    def _get_enhanced_session(self, session_id: str):
        """Get enhanced session with conversation context."""
        # Get base session
        analysis_mode = st.session_state.analysis_mode
        engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
        session = engine.get_qa_session(session_id)
        
        # Get conversation context
        context = self.enhanced_storage.get_conversation_context(session_id)
        if context:
            st.session_state.conversation_context[session_id] = context
        
        return session
    
    def _render_enhanced_chat_history(self, session, document: Document) -> None:
        """Render enhanced chat history with conversation context."""
        if not session or not session.questions:
            st.info("💬 Start a conversation! Ask me anything about the document - I can handle complex questions and remember our discussion.")
            
            # Show conversation starters
            self._show_conversation_starters(document)
            return
        
        st.write("**💬 Conversation History:**")
        
        # Display questions and answers with enhanced formatting
        for i, interaction in enumerate(session.questions):
            # Question
            with st.chat_message("user"):
                st.write(interaction['question'])
            
            # Enhanced answer with conversation features
            with st.chat_message("assistant"):
                # Check for conversational response
                if interaction.get('conversation_tone'):
                    tone_icon = {"professional": "🏛️", "casual": "💬", "technical": "🔧"}.get(
                        interaction.get('conversation_tone', 'professional'), "💬"
                    )
                    st.caption(f"{tone_icon} {interaction.get('conversation_tone', 'professional').title()} tone")
                
                # Display main answer
                if interaction.get('analysis_mode') == 'contract' and interaction.get('structured_response'):
                    self._render_structured_response(interaction['structured_response'])
                else:
                    st.write(interaction['answer'])
                
                # Show follow-up suggestions
                if interaction.get('follow_up_suggestions'):
                    with st.expander("💡 Follow-up suggestions", expanded=False):
                        for suggestion in interaction['follow_up_suggestions']:
                            if st.button(f"💬 {suggestion}", key=f"followup_{i}_{hash(suggestion)}"):
                                st.session_state.question_input = suggestion
                                st.rerun()
                
                # Show sources and context
                if interaction.get('sources'):
                    with st.expander(f"{UIStyler.get_icon('documents')} Sources & Context", expanded=False):
                        for source in interaction['sources']:
                            st.write(f"{UIStyler.get_icon('info')} {source}")
                
                # Show conversation metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    if interaction.get('analysis_mode'):
                        mode_icon = "🏛️" if interaction['analysis_mode'] == 'contract' else "💬"
                        st.caption(f"{mode_icon} {interaction['analysis_mode'].title()}")
                
                with col2:
                    if interaction.get('confidence'):
                        confidence = interaction['confidence']
                        conf_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
                        st.caption(f":{conf_color}[Confidence: {confidence:.1%}]")
                
                with col3:
                    if interaction.get('timestamp'):
                        timestamp = datetime.fromisoformat(interaction['timestamp'])
                        st.caption(f"🕒 {timestamp.strftime('%H:%M:%S')}")
    
    def _show_conversation_starters(self, document: Document) -> None:
        """Show conversation starter suggestions."""
        with st.expander("💡 Conversation Starters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔍 Analysis Questions:**")
                starters = [
                    "What are the main points in this document?",
                    "Are there any risks I should be aware of?",
                    "What actions do I need to take?",
                    "Can you explain this in simple terms?"
                ]
                
                for starter in starters:
                    if st.button(f"💬 {starter}", key=f"starter_{hash(starter)}"):
                        st.session_state.question_input = starter
                        st.rerun()
            
            with col2:
                if st.session_state.analysis_mode == 'contract':
                    st.write("**🏛️ Legal Questions:**")
                    legal_starters = [
                        "Who are the parties in this agreement?",
                        "What are the key obligations?",
                        "Are there any concerning clauses?",
                        "What are the termination conditions?"
                    ]
                    
                    for starter in legal_starters:
                        if st.button(f"🏛️ {starter}", key=f"legal_starter_{hash(starter)}"):
                            st.session_state.question_input = starter
                            st.rerun()
    
    def _render_enhanced_question_input(self, document: Document, session_id: str) -> None:
        """Render enhanced question input with conversational features."""
        with st.form("enhanced_question_form", clear_on_submit=True):
            question = st.text_area(
                "Ask me anything about the document:",
                placeholder="e.g., 'What are the main risks and what should I do about them?' or 'Explain the key terms in simple language'",
                height=100,
                key="question_input",
                help="I can handle complex questions, follow-up questions, and remember our conversation context."
            )
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                submit_button = st.form_submit_button("💬 Ask", type="primary")
            
            with col2:
                excel_button = st.form_submit_button("📊 Ask & Export")
            
            with col3:
                example_button = st.form_submit_button("💡 Examples")
            
            with col4:
                clear_button = st.form_submit_button("🔄 Clear Context")
        
        # Handle different types of submissions
        if submit_button and question.strip():
            self._process_conversational_question(question.strip(), document, session_id)
        
        if excel_button and question.strip():
            self._process_question_with_excel(question.strip(), document, session_id)
        
        if example_button:
            self._show_example_questions(document)
        
        if clear_button:
            self._clear_conversation_context(session_id)
    
    def _clear_conversation_context(self, session_id: str) -> None:
        """Clear conversation context for enhanced mode."""
        try:
            # Clear enhanced context manager
            if self.enhanced_router and hasattr(self.enhanced_router.context_manager, 'conversations'):
                if session_id in self.enhanced_router.context_manager.conversations:
                    del self.enhanced_router.context_manager.conversations[session_id]
            
            # Clear session state context
            if session_id in st.session_state.conversation_context_persistence:
                del st.session_state.conversation_context_persistence[session_id]
            
            st.success("🔄 Conversation context cleared! Starting fresh.")
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error clearing conversation context: {e}")
            st.error("❌ Error clearing context. Please try again.")
    
    def _handle_enhanced_mode_error(self, error: Exception, question: str, document: Document, session_id: str) -> None:
        """Handle enhanced mode errors with graceful degradation."""
        logger.error(f"Enhanced mode error: {error}")
        
        # Show user-friendly error message
        st.warning("⚠️ Enhanced mode encountered an issue. Falling back to standard analysis...")
        
        # Temporarily disable enhanced mode
        st.session_state.enhanced_mode_enabled = False
        
        # Try with standard mode
        try:
            # Ensure engines are initialized
            self._ensure_engines_initialized()
            
            analysis_mode = st.session_state.analysis_mode
            engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
            
            if not engine:
                # Create a basic response if no engine is available
                self._create_basic_fallback_response(question)
                return
            
            result = engine.answer_question(question, document.id, session_id)
            
            # Display fallback response
            with st.chat_message("user"):
                st.write(question)
            
            with st.chat_message("assistant"):
                answer = result.get('answer', 'I apologize, but I encountered an error processing your question.')
                
                # If we still get an error, provide a helpful response
                if result.get('error') or not answer or answer.strip() == "":
                    answer = self._generate_helpful_fallback_response(question, document)
                
                st.write(answer)
                
                if result.get('sources'):
                    with st.expander("📚 Sources", expanded=False):
                        for source in result['sources']:
                            st.write(f"• {source}")
                
                st.caption("📝 Standard mode (enhanced mode temporarily disabled)")
            
            # Offer to re-enable enhanced mode
            if st.button("🚀 Try Enhanced Mode Again"):
                st.session_state.enhanced_mode_enabled = True
                st.rerun()
                
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            self._create_basic_fallback_response(question)
    
    def _create_basic_fallback_response(self, question: str) -> None:
        """Create a basic fallback response when all engines fail."""
        with st.chat_message("user"):
            st.write(question)
        
        with st.chat_message("assistant"):
            st.write("I apologize, but I encountered an issue processing your question. Let me try to help in a different way.")
            st.write("Could you try rephrasing your question, or ask about a specific aspect of the contract?")
            st.caption("📝 Basic fallback mode")
    
    def _generate_helpful_fallback_response(self, question: str, document: Document) -> str:
        """Generate a helpful fallback response based on question patterns."""
        question_lower = question.lower()
        
        # Check for common question patterns and provide helpful responses
        # Order matters - check more specific patterns first
        if any(word in question_lower for word in ['risk', 'risks', 'liability', 'danger', 'dangerous']):
            return "This appears to be asking about risks or liability. Look for sections on 'Liability', 'Risk', 'Indemnification', or 'Limitation of Liability' in the document."
        
        elif 'intellectual property' in question_lower or (question_lower.startswith('ip ') or ' ip ' in question_lower or question_lower.endswith(' ip')) or any(word in question_lower for word in ['ownership', 'owns', 'owner']) or ('rights' in question_lower and any(word in question_lower for word in ['property', 'ownership'])):
            return "This appears to be asking about intellectual property or ownership rights. Check sections on 'Intellectual Property', 'Ownership', or 'Rights' in the document."
        
        elif any(word in question_lower for word in ['who', 'parties', 'involved']) and not any(word in question_lower for word in ['owns', 'ownership']):
            return "This appears to be asking about the parties involved in the agreement. Please check the beginning of the document for party information, typically in the first few paragraphs or sections."
        
        elif any(word in question_lower for word in ['when', 'date', 'expire', 'term']):
            return "This appears to be asking about dates or terms. Look for sections mentioning 'Term', 'Effective Date', or 'Expiration' in the document."
        
        elif any(word in question_lower for word in ['what', 'obligations', 'requirements', 'must']):
            return "This appears to be asking about obligations or requirements. Check sections related to 'Obligations', 'Requirements', or 'Responsibilities' in the document."
        
        else:
            return f"I'm having trouble processing your specific question right now. However, I can help you analyze this document. Try asking about specific sections, parties, dates, obligations, or risks mentioned in the document."
    
    def _ensure_backward_compatibility(self) -> None:
        """Ensure backward compatibility with existing functionality."""
        # Verify all required engines are initialized
        required_engines = ['qa_engine', 'contract_engine', 'enhanced_router']
        
        for engine_name in required_engines:
            if not hasattr(self, engine_name) or getattr(self, engine_name) is None:
                logger.warning(f"Missing {engine_name}, enhanced mode may not work properly")
        
        # Ensure session state has required keys
        required_keys = ['enhanced_mode_enabled', 'conversation_context_persistence']
        for key in required_keys:
            if key not in st.session_state:
                if key == 'enhanced_mode_enabled':
                    st.session_state[key] = True
                else:
                    st.session_state[key] = {}
    
    def _validate_enhanced_response(self, enhanced_response) -> bool:
        """Validate enhanced response before processing."""
        try:
            # Check required attributes
            required_attrs = ['content', 'response_type', 'confidence', 'sources', 'suggestions']
            
            for attr in required_attrs:
                if not hasattr(enhanced_response, attr):
                    logger.warning(f"Enhanced response missing attribute: {attr}")
                    return False
            
            # Validate content is not empty
            if not enhanced_response.content or not enhanced_response.content.strip():
                logger.warning("Enhanced response has empty content")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating enhanced response: {e}")
            return False
    
    def _process_conversational_question(self, question: str, document: Document, session_id: str) -> None:
        """Process question using enhanced response router or fallback to conversational AI."""
        spinner_text = "🚀 Processing with enhanced AI..." if st.session_state.enhanced_mode_enabled else "💬 Understanding your question..."
        
        with st.spinner(spinner_text):
            try:
                # Ensure engines are initialized
                self._ensure_engines_initialized()
                
                if st.session_state.enhanced_mode_enabled and self.enhanced_router:
                    # Use enhanced response router
                    enhanced_response = self.enhanced_router.route_question(
                        question, document.id, session_id, document
                    )
                    
                    # Validate enhanced response
                    if not self._validate_enhanced_response(enhanced_response):
                        raise ValueError("Invalid enhanced response received")
                    
                    # Convert enhanced response to display format
                    response_data = self._convert_enhanced_response_to_display(enhanced_response, question, document)
                    
                    # Save enhanced interaction with context persistence
                    self._save_enhanced_interaction_with_context(session_id, question, enhanced_response, document)
                    
                    # Display immediate response
                    st.success("✅ Enhanced response generated!")
                    self._display_immediate_response(question, response_data)
                    
                else:
                    # Fall back to standard processing
                    self._process_standard_question(question, document, session_id)
                    return
                
                # Refresh to show in history
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error processing conversational question: {e}")
                # Graceful degradation
                self._handle_enhanced_mode_error(e, question, document, session_id)
    
    def _convert_enhanced_response_to_display(self, enhanced_response, question: str, document: Document) -> Dict[str, Any]:
        """Convert enhanced response to display format."""
        return {
            'answer': enhanced_response.content,
            'follow_up_suggestions': enhanced_response.suggestions,
            'sources': enhanced_response.sources,
            'confidence': enhanced_response.confidence,
            'response_type': enhanced_response.response_type,
            'tone': enhanced_response.tone,
            'structured_format': enhanced_response.structured_format,
            'context_used': enhanced_response.context_used,
            'enhanced_metadata': {
                'timestamp': enhanced_response.timestamp,
                'response_type': enhanced_response.response_type,
                'tone': enhanced_response.tone
            }
        }
    
    def _save_enhanced_interaction_with_context(self, session_id: str, question: str, enhanced_response, document: Document) -> None:
        """Save enhanced interaction with conversation context persistence."""
        try:
            # Save to conversation context persistence
            if session_id not in st.session_state.conversation_context_persistence:
                st.session_state.conversation_context_persistence[session_id] = []
            
            interaction_data = {
                'question': question,
                'answer': enhanced_response.content,
                'response_type': enhanced_response.response_type,
                'tone': enhanced_response.tone,
                'confidence': enhanced_response.confidence,
                'sources': enhanced_response.sources,
                'suggestions': enhanced_response.suggestions,
                'context_used': enhanced_response.context_used,
                'timestamp': enhanced_response.timestamp.isoformat(),
                'enhanced_mode': True,
                'structured_response': enhanced_response.structured_format
            }
            
            st.session_state.conversation_context_persistence[session_id].append(interaction_data)
            
            # Also save to standard storage for backward compatibility
            analysis_mode = st.session_state.analysis_mode
            engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
            
            # Format for standard storage
            formatted_answer = enhanced_response.content
            if enhanced_response.structured_format:
                # If we have structured format, use it
                formatted_answer = self._format_structured_response_for_storage(enhanced_response.structured_format)
            
            engine.storage.add_qa_interaction(session_id, question, formatted_answer, enhanced_response.sources)
            
        except Exception as e:
            logger.error(f"Error saving enhanced interaction: {e}")
    
    def _display_immediate_response(self, question: str, response_data: Dict[str, Any]) -> None:
        """Display immediate response in chat format with enhanced structured patterns."""
        with st.chat_message("user"):
            st.write(question)
        
        with st.chat_message("assistant"):
            # Show enhanced mode indicator with tone adaptation
            if st.session_state.enhanced_mode_enabled and response_data.get('enhanced_metadata'):
                metadata = response_data['enhanced_metadata']
                tone_value = metadata.get('tone', 'professional')
                # Handle enum values
                if hasattr(tone_value, 'value'):
                    tone_str = tone_value.value
                else:
                    tone_str = str(tone_value)
                
                tone_icon = {"professional": "🏛️", "conversational": "💬", "playful": "😊"}.get(tone_str, "💬")
                
                # Show structured pattern indicator
                structured_format = response_data.get('structured_format', {})
                pattern_type = structured_format.get('pattern', 'standard')
                
                pattern_indicators = {
                    'document': '📋 Document Analysis',
                    'general_legal': 'ℹ️ General Legal',
                    'data_table': '📊 Data Export',
                    'ambiguous': '🤔 Multi-Interpretation',
                    'ambiguous_enhanced': '🤔 Enhanced Analysis'
                }
                
                pattern_text = pattern_indicators.get(pattern_type, '💬 Standard')
                st.caption(f"{tone_icon} {tone_str.title()} Tone | {pattern_text}")
            
            # Display the main response content
            self._display_structured_response_content(response_data)
            
            # Show follow-up suggestions if available
            if response_data.get('follow_up_suggestions'):
                self._display_follow_up_suggestions(response_data['follow_up_suggestions'])
            
            # Show sources and metadata
            self._display_response_metadata(response_data)
    
    def _display_structured_response_content(self, response_data: Dict[str, Any]) -> None:
        """Display structured response content with appropriate formatting."""
        structured_format = response_data.get('structured_format', {})
        pattern_type = structured_format.get('pattern', 'standard')
        
        # Display based on pattern type
        if pattern_type == 'document':
            self._display_document_pattern_response(structured_format)
        elif pattern_type == 'general_legal':
            self._display_general_legal_pattern_response(structured_format)
        elif pattern_type == 'data_table':
            self._display_data_table_pattern_response(structured_format)
        elif pattern_type in ['ambiguous', 'ambiguous_enhanced']:
            self._display_ambiguous_pattern_response(structured_format)
        else:
            # Standard response display
            st.write(response_data.get('answer', 'No response available'))
    
    def _display_document_pattern_response(self, structured_format: Dict[str, Any]) -> None:
        """Display document pattern response with Evidence, Plain English, Implications."""
        evidence = structured_format.get('evidence', '')
        plain_english = structured_format.get('plain_english', '')
        implications = structured_format.get('implications', '')
        
        if evidence:
            st.markdown("### 📋 Evidence")
            st.write(evidence)
        
        if plain_english:
            st.markdown("### 🔍 Plain English")
            st.write(plain_english)
        
        if implications:
            st.markdown("### ⚖️ Implications")
            st.write(implications)
    
    def _display_general_legal_pattern_response(self, structured_format: Dict[str, Any]) -> None:
        """Display general legal pattern response with Status, General Rule, Application."""
        status = structured_format.get('status', '')
        general_rule = structured_format.get('general_rule', '')
        application = structured_format.get('application', '')
        
        if status:
            st.markdown("### ℹ️ Status")
            st.write(status)
        
        if general_rule:
            st.markdown("### 📚 General Rule")
            st.write(general_rule)
        
        if application:
            st.markdown("### 🎯 Application")
            st.write(application)
    
    def _display_data_table_pattern_response(self, structured_format: Dict[str, Any]) -> None:
        """Display data table pattern response with exports."""
        table = structured_format.get('table')
        exports = structured_format.get('exports', [])
        
        if table and hasattr(table, 'headers') and hasattr(table, 'rows'):
            # Display table
            st.markdown("### 📊 Data Summary")
            
            # Create DataFrame for better display
            import pandas as pd
            try:
                df = pd.DataFrame(table.rows, columns=table.headers)
                st.dataframe(df, use_container_width=True)
            except Exception:
                # Fallback to simple table display
                st.write("**Headers:**", ", ".join(table.headers))
                for i, row in enumerate(table.rows[:10]):  # Limit display
                    st.write(f"**Row {i+1}:**", ", ".join(str(cell) for cell in row))
        
        # Display export links
        if exports:
            st.markdown("### 📥 Export Options")
            for export_file in exports:
                if hasattr(export_file, 'download_url') and hasattr(export_file, 'format_type'):
                    st.markdown(f"- [{export_file.format_type.upper()} Download]({export_file.download_url})")
    
    def _display_ambiguous_pattern_response(self, structured_format: Dict[str, Any]) -> None:
        """Display ambiguous pattern response with interpretations and alternatives."""
        primary = structured_format.get('primary_interpretation', {})
        alternatives = structured_format.get('alternatives', [])
        synthesis = structured_format.get('synthesis', {})
        
        # Display primary interpretation
        if primary:
            intent = primary.get('intent', 'general_inquiry').replace('_', ' ').title()
            confidence = primary.get('confidence', 0.5)
            reasoning = primary.get('reasoning', '')
            
            st.markdown(f"### 🤔 Primary Interpretation: {intent}")
            st.write(f"**Confidence:** {confidence:.0%}")
            if reasoning:
                st.write(reasoning)
        
        # Display alternatives
        if alternatives:
            st.markdown("### 🔄 Alternative Interpretations")
            for i, alt in enumerate(alternatives, 1):
                with st.expander(f"Option {chr(64+i)}: {alt.get('focus', 'Alternative')}", expanded=False):
                    st.write(f"**Description:** {alt.get('description', '')}")
                    st.write(f"**Analysis Path:** {alt.get('analysis_path', '')}")
                    st.write(f"**Confidence:** {alt.get('confidence', 0.5):.0%}")
        
        # Display synthesis
        if synthesis:
            st.markdown("### 🔗 Synthesis")
            recommendation = synthesis.get('recommendation', '')
            if recommendation:
                st.write(recommendation)
            
            connections = synthesis.get('connections', [])
            if connections:
                st.write("**Connections:**")
                for connection in connections:
                    st.write(f"- {connection}")
    
    def _display_follow_up_suggestions(self, suggestions: List[str]) -> None:
        """Display follow-up suggestions with enhanced formatting."""
        if suggestions:
            st.markdown("### 💡 Follow-up Suggestions")
            for suggestion in suggestions[:4]:  # Limit to 4 suggestions
                if st.button(f"💬 {suggestion}", key=f"suggestion_{hash(suggestion)}"):
                    # Set the suggestion as the next question
                    st.session_state.question_input = suggestion
                    st.rerun()
    
    def _display_response_metadata(self, response_data: Dict[str, Any]) -> None:
        """Display response metadata including sources and confidence."""
        # Show confidence if available
        confidence = response_data.get('confidence')
        if confidence is not None:
            if confidence > 0.8:
                st.success(f"High confidence: {confidence:.0%}")
            elif confidence > 0.6:
                st.info(f"Good confidence: {confidence:.0%}")
            elif confidence > 0.4:
                st.warning(f"Moderate confidence: {confidence:.0%}")
            else:
                st.error(f"Low confidence: {confidence:.0%}")
        
        # Show sources in expandable section
        sources = response_data.get('sources', [])
        if sources:
            with st.expander("📚 Sources", expanded=False):
                for source in sources:
                    st.write(f"• {source}")
        
        # Show context used
        context_used = response_data.get('context_used', [])
        if context_used:
            with st.expander("🔍 Analysis Context", expanded=False):
                for context in context_used:
                    st.write(f"• {context.replace('_', ' ').title()}")
                
                response_type_value = metadata.get('response_type', 'response')
                if hasattr(response_type_value, 'value'):
                    response_type_str = response_type_value.value
                else:
                    response_type_str = str(response_type_value)
                
                response_type_text = response_type_str.replace('_', ' ').title()
                st.caption(f"{tone_icon} Enhanced {response_type_text}")
            
            # Display main answer
            if response_data.get('structured_format'):
                self._render_structured_response(response_data['structured_format'])
            else:
                st.write(response_data['answer'])
            
            # Show follow-up suggestions
            if response_data.get('follow_up_suggestions'):
                with st.expander("💡 Follow-up suggestions", expanded=True):
                    for suggestion in response_data['follow_up_suggestions']:
                        if st.button(f"💬 {suggestion}", key=f"immediate_followup_{hash(suggestion)}"):
                            st.session_state.question_input = suggestion
                            st.rerun()
            
            # Show sources and context
            if response_data.get('sources'):
                with st.expander("📚 Sources & Context", expanded=False):
                    for source in response_data['sources']:
                        st.write(f"• {source}")
            
            # Show enhanced context if available
            if st.session_state.enhanced_mode_enabled and response_data.get('context_used'):
                with st.expander("🧠 AI Context Used", expanded=False):
                    for context in response_data['context_used']:
                        st.write(f"• {context.replace('_', ' ').title()}")
    
    def _format_structured_response_for_storage(self, structured_format: Dict[str, Any]) -> str:
        """Format structured response for storage compatibility."""
        if not structured_format:
            return ""
        
        parts = []
        if structured_format.get('direct_evidence'):
            parts.append(f"**Direct Evidence:**\n{structured_format['direct_evidence']}")
        if structured_format.get('plain_explanation'):
            parts.append(f"**Plain-English Explanation:**\n{structured_format['plain_explanation']}")
        if structured_format.get('implication_analysis'):
            parts.append(f"**Implication/Analysis:**\n{structured_format['implication_analysis']}")
        
        return "\n\n".join(parts)
    
    def _process_question_with_excel(self, question: str, document: Document, session_id: str) -> None:
        """Process question and generate Excel report."""
        with st.spinner("💬 Processing question and preparing Excel report..."):
            try:
                # First process the question
                response = self.conversational_engine.answer_conversational_question(
                    question, document.id, session_id
                )
                
                # Save interaction
                self._save_enhanced_interaction(session_id, question, response, document)
                
                # Generate Excel report
                excel_report = self.excel_generator.generate_conversation_report(session_id)
                
                # Save report metadata
                self.enhanced_storage.save_excel_report(excel_report)
                st.session_state.excel_reports.append(excel_report)
                
                st.success("✅ Response generated and Excel report created!")
                
                # Show download link
                col1, col2 = st.columns(2)
                with col1:
                    st.write(response.answer)
                
                with col2:
                    st.download_button(
                        label="📊 Download Excel Report",
                        data=open(excel_report.file_path, 'rb').read(),
                        file_name=excel_report.filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing question with Excel: {str(e)}")
    
    def _save_enhanced_interaction(self, session_id: str, question: str, response, document: Document) -> None:
        """Save enhanced interaction with conversational metadata."""
        # Get appropriate engine
        analysis_mode = st.session_state.analysis_mode
        engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
        
        # Create enhanced interaction data
        interaction_data = {
            'question': question,
            'answer': response.answer,
            'sources': response.context_used,
            'analysis_mode': response.analysis_mode,
            'conversation_tone': response.conversation_tone,
            'follow_up_suggestions': response.follow_up_suggestions,
            'confidence': response.confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to session
        session = engine.get_qa_session(session_id)
        if session:
            session.questions.append(interaction_data)
            
            # Update conversation context
            if session_id in st.session_state.conversation_context:
                context = st.session_state.conversation_context[session_id]
                self.conversational_engine.manage_conversation_context(session_id, question, response.answer)
    
    def _clear_conversation_context(self, session_id: str) -> None:
        """Clear conversation context for fresh start."""
        if session_id in st.session_state.conversation_context:
            del st.session_state.conversation_context[session_id]
        
        # Clear from conversational engine
        if hasattr(self.conversational_engine, 'conversation_contexts'):
            if session_id in self.conversational_engine.conversation_contexts:
                del self.conversational_engine.conversation_contexts[session_id]
        
        st.success("🔄 Conversation context cleared!")
        st.rerun()
    
    def _render_enhanced_session_management(self, document_id: str, session_id: str) -> None:
        """Render enhanced session management with conversation features."""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 New Session", help="Start a fresh conversation"):
                analysis_mode = st.session_state.analysis_mode
                session_key = f"session_{document_id}_{analysis_mode}"
                if session_key in st.session_state.qa_sessions:
                    del st.session_state.qa_sessions[session_key]
                self._clear_conversation_context(session_id)
                st.success("New session started!")
                st.rerun()
        
        with col2:
            # Show enhanced mode status and context info
            if st.session_state.enhanced_mode_enabled:
                context_count = len(st.session_state.conversation_context_persistence.get(session_id, []))
                st.info(f"🚀 Enhanced: {context_count} turns")
            else:
                st.info("📝 Standard mode")
        
        with col3:
            # Show session stats
            analysis_mode = st.session_state.analysis_mode
            engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
            session = engine.get_qa_session(session_id)
            if session:
                question_count = len(session.questions)
                mode_icon = "🏛️" if analysis_mode == 'contract' else "💬"
                st.info(f"{mode_icon} {question_count} questions")
        
        with col4:
            # Excel report generation
            if st.button("📊 Generate Report", help="Create Excel report from conversation"):
                self._generate_conversation_excel(session_id)
    
    def _generate_conversation_excel(self, session_id: str) -> None:
        """Generate Excel report from conversation."""
        with st.spinner("📊 Generating Excel report from conversation..."):
            try:
                excel_report = self.excel_generator.generate_conversation_report(session_id)
                self.enhanced_storage.save_excel_report(excel_report)
                st.session_state.excel_reports.append(excel_report)
                
                st.success("✅ Excel report generated!")
                
                # Show download button
                st.download_button(
                    label="📊 Download Conversation Report",
                    data=open(excel_report.file_path, 'rb').read(),
                    file_name=excel_report.filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating Excel report: {str(e)}")
    
    def _render_excel_generation_section(self, document: Document) -> None:
        """Render Excel report generation section."""
        st.markdown("---")
        st.subheader("📊 Excel Report Generation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Document Analysis Report", help="Generate comprehensive document analysis report"):
                self._generate_document_excel(document.id, "comprehensive")
        
        with col2:
            if st.button("⚠️ Risks Only Report", help="Generate report focusing on risks"):
                self._generate_document_excel(document.id, "risks_only")
        
        with col3:
            if st.button("📝 Commitments Report", help="Generate report focusing on commitments"):
                self._generate_document_excel(document.id, "commitments_only")
        
        # Show existing reports
        if st.session_state.excel_reports:
            st.write("**📊 Generated Reports:**")
            for report in st.session_state.excel_reports[-5:]:  # Show last 5 reports
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"📄 {report.filename}")
                
                with col2:
                    st.write(f"🕒 {report.created_at.strftime('%H:%M:%S')}")
                
                with col3:
                    if os.path.exists(report.file_path):
                        st.download_button(
                            label="⬇️ Download",
                            data=open(report.file_path, 'rb').read(),
                            file_name=report.filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{report.report_id}"
                        )
    
    def _generate_document_excel(self, document_id: str, report_type: str) -> None:
        """Generate Excel report for document analysis."""
        with st.spinner(f"📊 Generating {report_type} Excel report..."):
            try:
                excel_report = self.excel_generator.generate_document_report(document_id, report_type)
                self.enhanced_storage.save_excel_report(excel_report)
                st.session_state.excel_reports.append(excel_report)
                
                st.success(f"✅ {report_type.title()} report generated!")
                
                # Show immediate download
                st.download_button(
                    label=f"📊 Download {report_type.title()} Report",
                    data=open(excel_report.file_path, 'rb').read(),
                    file_name=excel_report.filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating {report_type} report: {str(e)}")
    
    def _show_template_creation_dialog(self) -> None:
        """Show template creation dialog."""
        st.info("Template creation feature coming soon!")
    
    def _show_template_management(self) -> None:
        """Show template management interface."""
        st.info("Template management feature coming soon!")
    
    def _render_export_options(self, result: Dict[str, Any], request_analysis, document: Document) -> None:
        """Render export options based on request analysis."""
        st.markdown("---")
        st.subheader("📊 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export as Excel", key=f"excel_export_{hash(str(result))}"):
                self._generate_response_export(result, 'excel', request_analysis, document)
        
        with col2:
            if st.button("📄 Export as CSV", key=f"csv_export_{hash(str(result))}"):
                self._generate_response_export(result, 'csv', request_analysis, document)
        
        with col3:
            if st.button("📋 Export as Text", key=f"text_export_{hash(str(result))}"):
                self._generate_response_export(result, 'text', request_analysis, document)
        
        # Show export confidence
        confidence_text = f"Export confidence: {request_analysis.confidence:.1%}"
        if request_analysis.confidence >= 0.8:
            st.success(f"🎯 {confidence_text} - Strong export recommendation")
        elif request_analysis.confidence >= 0.6:
            st.info(f"📊 {confidence_text} - Tabular data detected")
        else:
            st.warning(f"⚠️ {confidence_text} - Potential export need")
    
    def _generate_response_export(self, result: Dict[str, Any], format_type: str, 
                                request_analysis, document: Document) -> None:
        """Generate export for the response data."""
        try:
            with st.spinner(f"Generating {format_type.upper()} export..."):
                # Format the response data
                formatted_data = self.data_formatter.format_response_for_export(
                    result,
                    response_type='qa_response',
                    context={
                        'document_id': document.id,
                        'document_title': document.title,
                        'analysis_mode': st.session_state.analysis_mode,
                        'request_analysis': request_analysis
                    }
                )
                
                # Generate export using the export engine
                export_result = self.excel_export_engine.export_tabular_data(
                    formatted_data.structured_data,
                    user_request=f"Export response data as {format_type}",
                    format_preferences=[format_type, 'csv', 'text']
                )
                
                if export_result.success:
                    st.success(f"✅ {format_type.upper()} export generated successfully!")
                    
                    # Provide download link
                    st.markdown(f"**📥 [Download {export_result.filename}]({export_result.download_url})**")
                    
                    # Show file info
                    with st.expander("📋 Export Details", expanded=False):
                        st.write(f"**File:** {export_result.filename}")
                        st.write(f"**Format:** {export_result.format_type.upper()}")
                        st.write(f"**Expires:** {export_result.expiration_time.strftime('%Y-%m-%d %H:%M')}")
                        if export_result.fallback_used:
                            st.warning("⚠️ Fallback format used due to complexity")
                        
                        # Show metadata
                        if export_result.metadata:
                            st.json(export_result.metadata)
                    
                    # Add to session state for tracking
                    if 'generated_exports' not in st.session_state:
                        st.session_state.generated_exports = []
                    
                    st.session_state.generated_exports.append({
                        'filename': export_result.filename,
                        'format': export_result.format_type,
                        'generated_at': datetime.now(),
                        'download_url': export_result.download_url
                    })
                    
                else:
                    st.error(f"❌ Failed to generate {format_type.upper()} export: {export_result.error_message}")
                    
        except Exception as e:
            logger.error(f"Error generating export: {e}")
            st.error(f"❌ Error generating export: {str(e)}")
    
    def _render_enhanced_export_section(self, document: Document) -> None:
        """Render enhanced export generation section with never-fail guarantee."""
        st.markdown("---")
        st.subheader("📊 Enhanced Export Generation")
        
        # Export type selection
        col1, col2 = st.columns(2)
        
        with col1:
            export_type = st.selectbox(
                "Select Export Type:",
                options=[
                    "Document Summary",
                    "Risk Analysis",
                    "Q&A History", 
                    "Portfolio Analysis",
                    "Custom Data Export"
                ],
                key="export_type_selector"
            )
        
        with col2:
            format_preference = st.selectbox(
                "Preferred Format:",
                options=["Excel (Recommended)", "CSV", "JSON", "Text"],
                key="format_preference_selector"
            )
        
        # Generate export button
        if st.button("🚀 Generate Export", type="primary", key="generate_export_btn"):
            self._generate_enhanced_export(document, export_type, format_preference)
        
        # Show recent exports
        if 'generated_exports' in st.session_state and st.session_state.generated_exports:
            st.subheader("📥 Recent Exports")
            
            for export_info in reversed(st.session_state.generated_exports[-5:]):  # Show last 5
                with st.expander(f"📄 {export_info['filename']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Format:** {export_info['format'].upper()}")
                    
                    with col2:
                        st.write(f"**Generated:** {export_info['generated_at'].strftime('%H:%M:%S')}")
                    
                    with col3:
                        st.markdown(f"**[Download]({export_info['download_url']})**")
    
    def _generate_enhanced_export(self, document: Document, export_type: str, format_preference: str) -> None:
        """Generate enhanced export with never-fail guarantee."""
        try:
            with st.spinner(f"Generating {export_type} export..."):
                format_map = {
                    "Excel (Recommended)": "excel",
                    "CSV": "csv", 
                    "JSON": "json",
                    "Text": "text"
                }
                
                preferred_format = format_map.get(format_preference, "excel")
                
                if export_type == "Document Summary":
                    # Get document summary data
                    summary_data = self._get_document_summary_data(document)
                    export_result = self.excel_export_engine.generate_document_summary_export(summary_data)
                    
                elif export_type == "Risk Analysis":
                    # Get risk analysis data
                    risk_data = self._get_risk_analysis_data(document)
                    document_info = {'title': document.title, 'id': document.id}
                    export_result = self.excel_export_engine.generate_risk_analysis_report(risk_data, document_info)
                    
                elif export_type == "Q&A History":
                    # Get Q&A history
                    qa_history = self._get_qa_history_data(document.id)
                    export_result = self.excel_export_engine.export_tabular_data(
                        {'qa_history': qa_history},
                        user_request="Export Q&A history",
                        format_preferences=[preferred_format, 'csv', 'text']
                    )
                    
                elif export_type == "Portfolio Analysis":
                    # Get portfolio data
                    portfolio_data = self._get_portfolio_data()
                    export_result = self.excel_export_engine.generate_portfolio_analysis_report(portfolio_data)
                    
                else:  # Custom Data Export
                    # Get custom data based on current context
                    custom_data = self._get_custom_export_data(document)
                    export_result = self.excel_export_engine.export_tabular_data(
                        custom_data,
                        user_request=f"Custom export for {document.title}",
                        format_preferences=[preferred_format, 'csv', 'text']
                    )
                
                # Display results
                if export_result.success:
                    st.success(f"✅ {export_type} export generated successfully!")
                    
                    # Provide download link
                    st.markdown(f"**📥 [Download {export_result.filename}]({export_result.download_url})**")
                    
                    # Show export details
                    with st.expander("📋 Export Details", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**File:** {export_result.filename}")
                            st.write(f"**Format:** {export_result.format_type.upper()}")
                            st.write(f"**Size:** {self._get_file_size(export_result.file_path)}")
                        
                        with col2:
                            st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            st.write(f"**Expires:** {export_result.expiration_time.strftime('%Y-%m-%d %H:%M')}")
                            
                            if export_result.fallback_used:
                                st.warning("⚠️ Fallback format used")
                            else:
                                st.success("✅ Full format generated")
                    
                    # Add to session tracking
                    if 'generated_exports' not in st.session_state:
                        st.session_state.generated_exports = []
                    
                    st.session_state.generated_exports.append({
                        'filename': export_result.filename,
                        'format': export_result.format_type,
                        'generated_at': datetime.now(),
                        'download_url': export_result.download_url,
                        'export_type': export_type
                    })
                    
                else:
                    st.error(f"❌ Export generation failed: {export_result.error_message}")
                    
        except Exception as e:
            logger.error(f"Error in enhanced export generation: {e}")
            st.error(f"❌ Error generating export: {str(e)}")
    
    def _get_document_summary_data(self, document: Document) -> Dict[str, Any]:
        """Get document summary data for export."""
        return {
            'title': document.title,
            'document_type': document.document_type or 'Unknown',
            'upload_date': document.upload_timestamp.isoformat(),
            'summary': document.summary or 'No summary available',
            'file_size': document.file_size,
            'processing_status': document.processing_status,
            'key_terms': getattr(document, 'key_terms', {}),
            'important_dates': getattr(document, 'important_dates', [])
        }
    
    def _get_risk_analysis_data(self, document: Document) -> Dict[str, Any]:
        """Get risk analysis data for export."""
        # This would integrate with the risk analysis engine
        return {
            'risks': [
                {
                    'risk_id': 'R001',
                    'description': 'Sample risk for demonstration',
                    'severity': 'Medium',
                    'category': 'Legal',
                    'probability': 0.6,
                    'impact_description': 'Potential compliance issues',
                    'affected_parties': ['Organization'],
                    'mitigation_strategies': ['Regular compliance review'],
                    'materialization_timeframe': '6-12 months'
                }
            ]
        }
    
    def _get_qa_history_data(self, document_id: str) -> List[Dict[str, Any]]:
        """Get Q&A history data for export."""
        qa_history = []
        
        # Get sessions for this document
        analysis_mode = st.session_state.analysis_mode
        session_key = f"session_{document_id}_{analysis_mode}"
        
        if session_key in st.session_state.qa_sessions:
            session_id = st.session_state.qa_sessions[session_key]
            engine = self.contract_engine if analysis_mode == 'contract' else self.qa_engine
            
            if engine:
                session = engine.get_qa_session(session_id)
                if session and session.questions:
                    for i, interaction in enumerate(session.questions, 1):
                        qa_history.append({
                            'question_number': i,
                            'question': interaction['question'],
                            'answer': interaction['answer'],
                            'timestamp': interaction.get('timestamp', ''),
                            'analysis_mode': interaction.get('analysis_mode', analysis_mode),
                            'confidence': interaction.get('confidence', 'N/A'),
                            'sources': ', '.join(interaction.get('sources', []))
                        })
        
        return qa_history
    
    def _get_portfolio_data(self) -> List[Dict[str, Any]]:
        """Get portfolio data for export."""
        documents = self.storage.list_documents(status_filter='completed')
        portfolio_data = []
        
        for doc in documents:
            portfolio_data.append({
                'title': doc.title,
                'document_type': doc.document_type or 'Unknown',
                'upload_date': doc.upload_timestamp.isoformat(),
                'status': doc.processing_status,
                'file_size': doc.file_size,
                'is_legal_document': getattr(doc, 'is_legal_document', False),
                'risks': [],  # Would be populated by risk analysis
                'key_terms': getattr(doc, 'key_terms', [])
            })
        
        return portfolio_data
    
    def _get_custom_export_data(self, document: Document) -> Dict[str, Any]:
        """Get custom export data based on current context."""
        return {
            'document_info': self._get_document_summary_data(document),
            'qa_history': self._get_qa_history_data(document.id),
            'analysis_context': {
                'analysis_mode': st.session_state.analysis_mode,
                'enhanced_mode_enabled': st.session_state.enhanced_mode_enabled,
                'legal_document_info': st.session_state.legal_document_info.get(document.id, {})
            }
        }
    
    def _get_file_size(self, file_path: str) -> str:
        """Get human-readable file size."""
        try:
            import os
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"


def render_qa_page():
    """Render the enhanced Q&A page."""
    qa_interface = EnhancedQAInterface()
    qa_interface.render_qa_interface()


def render_qa_for_document(document_id: str):
    """Render enhanced Q&A interface for a specific document."""
    qa_interface = EnhancedQAInterface()
    qa_interface.render_qa_interface(document_id)


# Backward compatibility
QAInterface = EnhancedQAInterface