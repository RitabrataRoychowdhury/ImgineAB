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
from src.ui.styling import UIStyler
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
    
    # No CSS injection - just use simple icons
    
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
    
    # Simple title with icon
    st.title(f"{UIStyler.get_icon('documents')} Document Q&A System")
    st.write("Upload and process documents for intelligent question answering")
    
    # System status indicator
    with st.sidebar:
        st.subheader(f"{UIStyler.get_icon('status')} System Status")
        status = st.session_state.get('system_status', {})
        if status:
            st.success(UIStyler.create_status_badge("online", "System Online"))
            with st.expander(f"{UIStyler.get_icon('info')} System Info", expanded=False):
                # System metrics
                storage_info = status.get('storage', {})
                workflow_info = status.get('workflow', {})
                config_info = status.get('config', {})
                
                st.write(f"**{UIStyler.get_icon('metrics')} Quick Stats:**")
                st.write(f"- {UIStyler.get_icon('documents')} Documents: {storage_info.get('total_documents', 0)}")
                st.write(f"- {UIStyler.get_icon('queue')} Queue: {workflow_info.get('queue_size', 0)} jobs")
                api_status = 'Configured' if config_info.get('api_key_configured') else 'Not configured'
                api_icon = UIStyler.get_icon('success') if config_info.get('api_key_configured') else UIStyler.get_icon('error')
                st.write(f"- {UIStyler.get_icon('api')} API: {api_icon} {api_status}")
        else:
            st.warning(UIStyler.create_status_badge("warning", "Status Unknown"))
    
    # Initialize upload interface
    try:
        upload_interface = UploadInterface()
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Failed to initialize upload interface: {error_info['user_message']}")
        logger.error(f"Upload interface error: {e}", exc_info=True)
        upload_interface = None
    
    # Simple sidebar navigation with icons
    with st.sidebar:
        st.markdown("---")
        st.subheader(f"{UIStyler.get_icon('home')} Navigation")
        
        # Navigation options with icons
        nav_options = [
            f"{UIStyler.get_icon('upload')} Upload Documents",
            f"{UIStyler.get_icon('documents')} Document Management", 
            f"{UIStyler.get_icon('qa')} Q&A Interface",
            f"{UIStyler.get_icon('history')} Upload History",
            f"{UIStyler.get_icon('status')} System Status",
            f"{UIStyler.get_icon('about')} About"
        ]
        
        selected_display = st.selectbox(
            "Choose a section:",
            nav_options,
            help="Select a section to navigate to"
        )
        
        # Extract page name
        page = selected_display.split(' ', 1)[1]  # Remove icon and get page name
    
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
    
    # Upload section with modern styling
    st.markdown("### 📤 Upload Documents")
    st.markdown("Select files to upload and process for intelligent Q&A")
    
    file_data = upload_interface.render_upload_section()
    
    if file_data:
        st.markdown("---")
        
        # Check if document has been processed
        if file_data.get('processing_complete'):
            st.success("🎉 Document Processing Complete!")
            
            # Show immediate Q&A access
            st.info("""
            **Your document is ready:**
            - ✅ Text extracted and analyzed
            - 🤖 AI processing complete  
            - 💬 Ready for intelligent Q&A!
            """)
            
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
    st.markdown("### 📋 Upload History")
    st.markdown("View and manage your document upload history")
    
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
    """Render the system status page with enhanced visual indicators"""
    
    st.markdown("---")
    st.markdown(f"### {UIStyler.get_icon('status')} System Status")
    st.markdown("Monitor system health and performance metrics")
    
    try:
        app = get_app()
        status = app.get_system_status()
        
        if status.get("error"):
            st.error(f"System status error: {status['error']}")
            return
        
        # System status metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            system_status = "Online" if status['initialized'] else "Offline"
            icon = UIStyler.get_icon('online') if status['initialized'] else UIStyler.get_icon('offline')
            st.metric("System Status", f"{icon} {system_status}")
        
        with col2:
            st.metric("Total Documents", f"{UIStyler.get_icon('documents')} {status['storage']['total_documents']}")
        
        with col3:
            queue_size = status['workflow']['queue_size']
            st.metric("Queue Size", f"{UIStyler.get_icon('queue')} {queue_size}")
        
        # Storage statistics with icons
        st.subheader(f"{UIStyler.get_icon('metrics')} Storage Statistics")
        storage_stats = status['storage']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{UIStyler.get_icon('documents')} Documents by Status:**")
            for status_name, count in storage_stats['documents_by_status'].items():
                status_icon = UIStyler.get_icon(status_name)
                st.write(f"{status_icon} {status_name}: {count}")
        
        with col2:
            st.write(f"**{UIStyler.get_icon('queue')} Processing Jobs by Status:**")
            for status_name, count in storage_stats['jobs_by_status'].items():
                status_icon = UIStyler.get_icon(status_name)
                st.write(f"{status_icon} {status_name}: {count}")
        
        # Database information
        st.subheader(f"{UIStyler.get_icon('database')} Database Information")
        db_info = status['database']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{UIStyler.get_icon('info')} Path:** `{db_info['path']}`")
            st.write(f"**{UIStyler.get_icon('metrics')} Size:** {db_info['size_bytes']:,} bytes")
        
        with col2:
            st.write(f"**{UIStyler.get_icon('database')} Tables:**")
            for table, count in db_info['tables'].items():
                st.write(f"{UIStyler.get_icon('documents')} {table}: {count} records")
        
        # Configuration
        st.subheader(f"{UIStyler.get_icon('settings')} Configuration")
        config_info = status['config']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{UIStyler.get_icon('metrics')} Max File Size:** {config_info['max_file_size_mb']} MB")
            debug_icon = UIStyler.get_icon('success') if config_info['debug_mode'] else UIStyler.get_icon('error')
            st.write(f"**{UIStyler.get_icon('settings')} Debug Mode:** {debug_icon} {'Enabled' if config_info['debug_mode'] else 'Disabled'}")
        
        with col2:
            api_icon = UIStyler.get_icon('success') if config_info['api_key_configured'] else UIStyler.get_icon('error')
            st.write(f"**{UIStyler.get_icon('api')} API Configured:** {api_icon} {'Yes' if config_info['api_key_configured'] else 'No'}")
            st.write(f"**{UIStyler.get_icon('documents')} Allowed Types:** {', '.join(config_info['allowed_file_types'])}")
        
        # Workflow status
        st.subheader(f"{UIStyler.get_icon('processing')} Workflow Status")
        workflow_info = status['workflow']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Queue Size", f"{UIStyler.get_icon('queue')} {workflow_info['queue_size']}")
        
        with col2:
            st.metric("Active Jobs", f"{UIStyler.get_icon('processing')} {workflow_info['active_jobs']}")
        
        with col3:
            manager_text = "Running" if workflow_info['running'] else "Stopped"
            manager_icon = UIStyler.get_icon('online') if workflow_info['running'] else UIStyler.get_icon('offline')
            st.metric("Manager Status", f"{manager_icon} {manager_text}")
        
        # Refresh button
        if st.button(f"{UIStyler.get_icon('refresh')} Refresh Status"):
            st.session_state.pop('system_status_checked', None)
            st.rerun()
        
    except Exception as e:
        error_info = format_error_for_ui(e)
        st.error(f"Error loading system status: {error_info['user_message']}")
        logger.error(f"System status page error: {e}", exc_info=True)


def render_about_page():
    """Render the about page"""
    
    st.markdown("---")
    
    st.subheader(f"{UIStyler.get_icon('about')} About Document Q&A System")
    
    st.write("This system allows you to upload documents and ask intelligent questions about their content using AI-powered analysis.")
    
    st.subheader(f"{UIStyler.get_icon('success')} Current Features")
    
    # Display features as simple list
    features = [
        "File Upload: Support for PDF, TXT, and DOCX formats",
        "File Validation: Format and size validation (max 10MB)",
        "Text Extraction: Intelligent text extraction from various formats",
        "LangGraph Processing: Enhanced document processing workflow with Gemini AI",
        "Document Storage: Persistent document management with SQLite",
        "Q&A Engine: Ask intelligent questions about your documents",
        "Context Search: Find relevant information quickly",
        "Document Management: View, organize, and delete processed documents",
        "Chat Interface: Interactive Q&A with conversation history",
        "Real-time Processing: Progress tracking and status updates",
        "Error Handling: Comprehensive error handling and recovery",
        "Logging: Detailed logging for debugging and monitoring",
        "System Integration: Unified application architecture"
    ]
    
    for feature in features:
        st.write(f"- {UIStyler.get_icon('success')} **{feature}**")
    
    st.markdown("""
    
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