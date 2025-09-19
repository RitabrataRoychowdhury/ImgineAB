"""Q&A Interface for document question answering with chat-like interaction."""

import streamlit as st
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.services.qa_engine import QAEngine, create_qa_engine
from src.storage.document_storage import DocumentStorage
from src.models.document import Document, QASession
from src.config import config
from src.ui.styling import UIStyler


class QAInterface:
    """Streamlit interface for document Q&A functionality."""
    
    def __init__(self):
        self.storage = DocumentStorage()
        self.qa_engine = None
        
        # Initialize session state
        if 'qa_sessions' not in st.session_state:
            st.session_state.qa_sessions = {}
        if 'current_qa_session' not in st.session_state:
            st.session_state.current_qa_session = None
        if 'selected_document' not in st.session_state:
            st.session_state.selected_document = None
    
    def render_qa_interface(self, document_id: Optional[str] = None) -> None:
        """
        Render the main Q&A interface.
        
        Args:
            document_id: Optional document ID to start Q&A with
        """
        # Get API key with enhanced error display
        api_key = config.get_gemini_api_key()
        if not api_key:
            st.error(f"{UIStyler.get_icon('error')} Gemini API key not configured. Please set GEMINI_API_KEY in your environment.")
            st.info(f"{UIStyler.get_icon('info')} You can get an API key from: https://makersuite.google.com/app/apikey")
            return
        
        # Initialize QA engine
        if not self.qa_engine:
            self.qa_engine = create_qa_engine(api_key, self.storage)
        
        # Document selection section
        selected_doc = self._render_document_selector(document_id)
        
        if not selected_doc:
            st.info("👆 Please select a document to start asking questions.")
            return
        
        # Q&A session section
        self._render_qa_session(selected_doc)
    
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
        
        # Display enhanced document info with icons
        with st.expander(f"{UIStyler.get_icon('info')} Document Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{UIStyler.get_icon('documents')} Title:** {selected_doc.title}")
                st.write(f"**{UIStyler.get_icon('info')} Type:** {selected_doc.document_type or 'Unknown'}")
                st.write(f"**{UIStyler.get_icon(selected_doc.file_type)} File Format:** {selected_doc.file_type.upper()}")
                st.write(f"**{UIStyler.get_icon('metrics')} Size:** {selected_doc.file_size:,} bytes")
            
            with col2:
                st.write(f"**{UIStyler.get_icon('upload')} Uploaded:** {selected_doc.upload_timestamp.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**{UIStyler.get_icon('processing')} Processed:** {selected_doc.updated_at.strftime('%Y-%m-%d %H:%M')}")
                status_badge = UIStyler.create_status_badge(selected_doc.processing_status)
                st.write(f"**Status:** {status_badge}")
            
            if selected_doc.summary:
                st.write(f"**{UIStyler.get_icon('info')} Summary:**")
                st.write(selected_doc.summary)
        
        # Store selected document in session state
        st.session_state.selected_document = selected_doc.id
        
        return selected_doc
    
    def _render_qa_session(self, document: Document) -> None:
        """Render Q&A session interface for the selected document."""
        st.subheader(f"{UIStyler.get_icon('qa')} Ask Questions")
        
        # Get or create Q&A session
        session_id = self._get_or_create_session(document.id)
        session = self.qa_engine.get_qa_session(session_id)
        
        # Display chat history
        self._render_chat_history(session)
        
        # Question input
        self._render_question_input(document, session_id)
        
        # Session management
        self._render_session_management(document.id)
    
    def _get_or_create_session(self, document_id: str) -> str:
        """Get existing session or create new one for the document."""
        session_key = f"session_{document_id}"
        
        if session_key not in st.session_state.qa_sessions:
            # Create new session
            session_id = self.qa_engine.create_qa_session(document_id)
            st.session_state.qa_sessions[session_key] = session_id
        
        return st.session_state.qa_sessions[session_key]
    
    def _render_chat_history(self, session: Optional[QASession]) -> None:
        """Render chat history for the session."""
        if not session or not session.questions:
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
                st.write(interaction['answer'])
                
                # Show sources if available with enhanced icon
                if interaction.get('sources'):
                    with st.expander(f"{UIStyler.get_icon('documents')} Sources", expanded=False):
                        for source in interaction['sources']:
                            st.write(f"{UIStyler.get_icon('info')} {source}")
                
                # Show timestamp
                if interaction.get('timestamp'):
                    timestamp = datetime.fromisoformat(interaction['timestamp'])
                    st.caption(f"Answered at {timestamp.strftime('%H:%M:%S')}")
    
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
        with st.spinner("🤔 Thinking about your question..."):
            try:
                # Get answer from QA engine
                result = self.qa_engine.answer_question(question, document.id, session_id)
                
                # Display the answer
                if result.get('error'):
                    st.error(f"❌ {result['answer']}")
                else:
                    st.success("✅ Answer generated!")
                    
                    # Show answer in chat format
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        st.write(result['answer'])
                        
                        # Show sources
                        if result.get('sources'):
                            with st.expander("📚 Sources", expanded=True):
                                for source in result['sources']:
                                    st.write(f"• {source}")
                        
                        # Show confidence if available
                        if 'confidence' in result:
                            confidence = result['confidence']
                            if confidence > 0.7:
                                st.success(f"Confidence: {confidence:.1%}")
                            elif confidence > 0.4:
                                st.warning(f"Confidence: {confidence:.1%}")
                            else:
                                st.error(f"Low confidence: {confidence:.1%}")
                
                # Refresh to show updated conversation
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing question: {str(e)}")
    
    def _show_example_questions(self, document: Document) -> None:
        """Show example questions based on document type."""
        st.subheader("💡 Example Questions")
        
        # General examples
        general_examples = [
            "What is the main topic of this document?",
            "Can you summarize the key points?",
            "What are the most important findings?",
            "Are there any action items mentioned?",
            "What dates or deadlines are mentioned?"
        ]
        
        # Document type specific examples
        type_specific = {
            'Legal Document': [
                "What are the key terms and conditions?",
                "Who are the parties involved?",
                "What are the obligations of each party?",
                "Are there any penalties mentioned?"
            ],
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
        st.write("**General Questions:**")
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
        """Render session management controls."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 New Session", help="Start a fresh conversation"):
                session_key = f"session_{document_id}"
                if session_key in st.session_state.qa_sessions:
                    del st.session_state.qa_sessions[session_key]
                st.success("New session started!")
                st.rerun()
        
        with col2:
            # Get current session info
            session_key = f"session_{document_id}"
            if session_key in st.session_state.qa_sessions:
                session_id = st.session_state.qa_sessions[session_key]
                session = self.qa_engine.get_qa_session(session_id)
                if session:
                    question_count = len(session.questions)
                    st.info(f"💬 {question_count} questions in this session")
        
        with col3:
            # Show session history
            sessions = self.qa_engine.get_document_qa_sessions(document_id)
            if len(sessions) > 1:
                st.info(f"📚 {len(sessions)} total sessions for this document")


def render_qa_page():
    """Render the Q&A page."""
    qa_interface = QAInterface()
    qa_interface.render_qa_interface()


def render_qa_for_document(document_id: str):
    """Render Q&A interface for a specific document."""
    qa_interface = QAInterface()
    qa_interface.render_qa_interface(document_id)