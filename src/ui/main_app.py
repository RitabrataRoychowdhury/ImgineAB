"""
Main Streamlit application for the Document Q&A System.
Integrated application with comprehensive error handling and logging.
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app import get_app, initialize_app
from src.ui.upload_interface import UploadInterface
from src.ui.qa_interface import render_qa_page
from src.ui.document_manager import render_document_management_page
from src.utils.logging_config import get_logger
from src.utils.error_handling import DocumentQAError, format_error_for_ui

logger = get_logger(__name__)

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Document Q&A System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application if not already done
    if 'app_initialized' not in st.session_state:
        with st.spinner("Initializing application..."):
            try:
                success = initialize_app()
                if success:
                    st.session_state.app_initialized = True
                    logger.info("Application initialized successfully in Streamlit")
                else:
                    st.error("Failed to initialize application. Please check the logs.")
                    st.stop()
            except Exception as e:
                error_info = format_error_for_ui(e)
                st.error(f"Initialization error: {error_info['user_message']}")
                logger.error(f"Streamlit initialization error: {e}", exc_info=True)
                st.stop()
    
    # Get application instance
    try:
        app = get_app()
        
        # Check system status
        if 'system_status_checked' not in st.session_state:
            status = app.get_system_status()
            if status.get("error"):
                st.error(f"System health check failed: {status['error']}")
                st.stop()
            st.session_state.system_status_checked = True
            st.session_state.system_status = status
        
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Application error: {error_info['user_message']}")
        logger.error(f"Streamlit app error: {e}", exc_info=True)
        st.stop()
    
    # Main title
    st.title("📚 Document Q&A System")
    st.markdown("Upload and process documents for intelligent question answering")
    
    # System status indicator
    with st.sidebar:
        status = st.session_state.get('system_status', {})
        if status:
            st.success("🟢 System Online")
            with st.expander("System Info", expanded=False):
                st.write(f"Documents: {status.get('storage', {}).get('total_documents', 0)}")
                st.write(f"Queue: {status.get('workflow', {}).get('queue_size', 0)} jobs")
                st.write(f"API: {'✅' if status.get('config', {}).get('api_key_configured') else '❌'}")
        else:
            st.warning("🟡 System Status Unknown")
    
    # Initialize upload interface
    try:
        upload_interface = UploadInterface()
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Failed to initialize upload interface: {error_info['user_message']}")
        logger.error(f"Upload interface error: {e}", exc_info=True)
        upload_interface = None
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a section:",
            ["Upload Documents", "Document Management", "Q&A Interface", "Upload History", "System Status", "About"]
        )
    
    # Handle navigation switches from upload interface
    if st.session_state.get('switch_to_qa', False):
        st.session_state.switch_to_qa = False
        page = "Q&A Interface"
    elif st.session_state.get('switch_to_management', False):
        st.session_state.switch_to_management = False
        page = "Document Management"
    
    # Main content area with error handling
    try:
        if page == "Upload Documents":
            if upload_interface:
                render_upload_page(upload_interface)
            else:
                st.error("Upload interface not available")
        elif page == "Document Management":
            # Check if we need to show a specific document
            if st.session_state.get('view_document_id'):
                document_id = st.session_state.view_document_id
                st.session_state.view_document_id = None
                render_document_management_page(document_id)
            else:
                render_document_management_page()
        elif page == "Q&A Interface":
            # Check if we need to start Q&A with a specific document
            if st.session_state.get('qa_document_id'):
                document_id = st.session_state.qa_document_id
                st.session_state.qa_document_id = None
                render_qa_page_with_document(document_id)
            else:
                render_qa_page()
        elif page == "Upload History":
            if upload_interface:
                render_history_page(upload_interface)
            else:
                st.error("Upload interface not available")
        elif page == "System Status":
            render_system_status_page()
        elif page == "About":
            render_about_page()
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Page error: {error_info['user_message']}")
        logger.error(f"Page rendering error on {page}: {e}", exc_info=True)
        
        # Show error details in debug mode
        if st.session_state.get('system_status', {}).get('config', {}).get('debug_mode'):
            with st.expander("Error Details (Debug Mode)", expanded=False):
                st.code(str(e))
                if hasattr(e, '__traceback__'):
                    import traceback
                    st.code(traceback.format_exc())


def render_qa_page_with_document(document_id: str):
    """Render Q&A page with a specific document pre-selected."""
    from src.ui.qa_interface import render_qa_for_document
    render_qa_for_document(document_id)

def render_upload_page(upload_interface: UploadInterface):
    """Render the document upload page"""
    
    st.markdown("---")
    
    # Upload section
    file_data = upload_interface.render_upload_section()
    
    if file_data:
        st.markdown("---")
        
        # Check if document has been processed
        if file_data.get('processing_complete'):
            st.success("🎉 Document uploaded and AI processing complete!")
            
            # Show immediate Q&A access
            st.info(
                "**Your document is ready:**\n"
                "✅ Text extracted and analyzed\n"
                "🤖 AI processing complete\n"
                "💬 Ready for intelligent Q&A!"
            )
            
            # Quick access buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💬 Ask Questions Now", type="primary"):
                    st.session_state.qa_document_id = file_data['document_id']
                    st.session_state.switch_to_qa = True
                    st.rerun()
            
            with col2:
                if st.button("📄 View All Documents"):
                    st.session_state.switch_to_management = True
                    st.rerun()
        
        elif file_data.get('error'):
            st.error(f"❌ Processing failed: {file_data['error']}")
            st.info("The document was uploaded but AI processing failed. You can try uploading again.")
        
        else:
            st.success("🎉 File successfully processed!")
            st.warning("⚠️ AI processing is not available. Please configure your Gemini API key for Q&A functionality.")

def render_history_page(upload_interface: UploadInterface):
    """Render the upload history page"""
    
    st.markdown("---")
    
    uploaded_files = upload_interface.get_uploaded_files()
    
    if not uploaded_files:
        st.info("No documents uploaded yet. Go to 'Upload Documents' to get started!")
        return
    
    # Display upload history
    upload_interface.render_upload_history()
    
    # Clear history button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🗑️ Clear All History", type="secondary"):
            upload_interface.clear_upload_history()
            st.success("Upload history cleared!")
            st.rerun()

def render_system_status_page():
    """Render the system status page"""
    
    st.markdown("---")
    st.header("🔧 System Status")
    
    try:
        app = get_app()
        status = app.get_system_status()
        
        if status.get("error"):
            st.error(f"System status error: {status['error']}")
            return
        
        # Overall status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("System Status", "🟢 Online" if status['initialized'] else "🔴 Offline")
        
        with col2:
            st.metric("Total Documents", status['storage']['total_documents'])
        
        with col3:
            st.metric("Queue Size", status['workflow']['queue_size'])
        
        # Detailed information
        st.subheader("📊 Storage Statistics")
        storage_stats = status['storage']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Documents by Status:**")
            for status_name, count in storage_stats['documents_by_status'].items():
                st.write(f"- {status_name}: {count}")
        
        with col2:
            st.write("**Processing Jobs by Status:**")
            for status_name, count in storage_stats['jobs_by_status'].items():
                st.write(f"- {status_name}: {count}")
        
        # Database information
        st.subheader("🗄️ Database Information")
        db_info = status['database']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Path:** `{db_info['path']}`")
            st.write(f"**Size:** {db_info['size_bytes']:,} bytes")
        
        with col2:
            st.write("**Tables:**")
            for table, count in db_info['tables'].items():
                st.write(f"- {table}: {count} records")
        
        # Configuration
        st.subheader("⚙️ Configuration")
        config_info = status['config']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Max File Size:** {config_info['max_file_size_mb']} MB")
            st.write(f"**Debug Mode:** {'✅' if config_info['debug_mode'] else '❌'}")
        
        with col2:
            st.write(f"**API Configured:** {'✅' if config_info['api_key_configured'] else '❌'}")
            st.write(f"**Allowed Types:** {', '.join(config_info['allowed_file_types'])}")
        
        # Workflow status
        st.subheader("🔄 Workflow Status")
        workflow_info = status['workflow']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Queue Size", workflow_info['queue_size'])
        
        with col2:
            st.metric("Active Jobs", workflow_info['active_jobs'])
        
        with col3:
            st.metric("Manager Running", "✅" if workflow_info['running'] else "❌")
        
        # Refresh button
        if st.button("🔄 Refresh Status"):
            st.session_state.pop('system_status_checked', None)
            st.rerun()
        
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Error loading system status: {error_info['user_message']}")
        logger.error(f"System status page error: {e}", exc_info=True)


def render_about_page():
    """Render the about page"""
    
    st.markdown("---")
    
    st.markdown("""
    ## About Document Q&A System
    
    This system allows you to upload documents and ask intelligent questions about their content using AI-powered analysis.
    
    ### Current Features
    - ✅ **File Upload**: Support for PDF, TXT, and DOCX formats
    - ✅ **File Validation**: Format and size validation (max 10MB)
    - ✅ **Text Extraction**: Intelligent text extraction from various formats
    - ✅ **LangGraph Processing**: Enhanced document processing workflow with Gemini AI
    - ✅ **Document Storage**: Persistent document management with SQLite
    - ✅ **Q&A Engine**: Ask intelligent questions about your documents
    - ✅ **Context Search**: Find relevant information quickly
    - ✅ **Document Management**: View, organize, and delete processed documents
    - ✅ **Chat Interface**: Interactive Q&A with conversation history
    - ✅ **Real-time Processing**: Progress tracking and status updates
    - ✅ **Error Handling**: Comprehensive error handling and recovery
    - ✅ **Logging**: Detailed logging for debugging and monitoring
    - ✅ **System Integration**: Unified application architecture
    
    ### How It Works
    1. **Upload**: Upload your documents through the web interface
    2. **Process**: Documents are analyzed using Gemini AI through a LangGraph workflow
    3. **Store**: Processed results are stored with embeddings for fast retrieval
    4. **Query**: Ask questions and get intelligent answers with source citations
    
    ### Supported File Formats
    - **PDF**: Portable Document Format files
    - **TXT**: Plain text files (various encodings supported)
    - **DOCX**: Microsoft Word documents
    
    ### Technical Details
    - Built with Streamlit for the web interface
    - Uses LangGraph for document processing workflows
    - Integrates with Google Gemini AI for intelligent analysis
    - SQLite database for document and session storage
    - Context-aware question answering with source attribution
    - Comprehensive error handling and validation
    - Centralized logging and monitoring
    - Circuit breaker pattern for API resilience
    - Retry logic with exponential backoff
    
    ### Getting Started
    1. Go to **Upload Documents** to add your first document
    2. Wait for processing to complete (you'll see progress updates)
    3. Use **Document Management** to view and manage your documents
    4. Use **Q&A Interface** to ask questions about processed documents
    5. Check **System Status** to monitor system health
    
    ### Error Handling
    The system includes comprehensive error handling:
    - File upload validation and error recovery
    - API failure handling with retry logic
    - Database transaction safety
    - Workflow error recovery
    - User-friendly error messages
    - Detailed logging for debugging
    """)

if __name__ == "__main__":
    main()