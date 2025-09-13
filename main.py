"""Main entry point for the Document Q&A System."""

import os
import sys
import argparse

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.app import initialize_app, shutdown_app, get_app
from src.utils.logging_config import get_logger
from src.utils.error_handling import DocumentQAError, format_error_for_ui

logger = get_logger(__name__)


def run_streamlit():
    """Run the Streamlit web interface."""
    import subprocess
    
    try:
        # Initialize the application first
        if not initialize_app():
            print("❌ Failed to initialize application")
            return False
        
        print("🌐 Starting Streamlit web interface...")
        print(f"   URL: http://localhost:8501")
        print("   Press Ctrl+C to stop")
        
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/ui/main_app.py",
            "--server.port", str(8501),
            "--server.headless", "true"
        ])
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping web interface...")
        return True
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}", exc_info=True)
        print(f"❌ Error starting web interface: {e}")
        return False
    finally:
        shutdown_app()


def run_system_check():
    """Run system health check."""
    try:
        print("🔍 Running system health check...")
        
        if not initialize_app():
            print("❌ Application initialization failed")
            return False
        
        app = get_app()
        status = app.get_system_status()
        
        if status.get("error"):
            print(f"❌ System check failed: {status['error']}")
            return False
        
        print("✅ System Health Check Results:")
        print(f"   Initialized: {status['initialized']}")
        print(f"   Documents: {status['storage']['total_documents']}")
        print(f"   Database size: {status['database']['size_bytes']} bytes")
        print(f"   Queue size: {status['workflow']['queue_size']}")
        print(f"   API configured: {status['config']['api_key_configured']}")
        print(f"   Debug mode: {status['config']['debug_mode']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during system check: {e}", exc_info=True)
        print(f"❌ System check error: {e}")
        return False
    finally:
        shutdown_app()


def run_init_only():
    """Initialize the system without starting the web interface."""
    try:
        print("🚀 Initializing Document Q&A System...")
        
        if not initialize_app():
            print("❌ Application initialization failed")
            return False
        
        app = get_app()
        status = app.get_system_status()
        
        print("✅ System initialized successfully!")
        print("\n📊 System Status:")
        print(f"   Documents: {status['storage']['total_documents']}")
        print(f"   Database: {status['database']['path']}")
        print(f"   Max file size: {status['config']['max_file_size_mb']}MB")
        print(f"   Allowed types: {', '.join(status['config']['allowed_file_types'])}")
        
        print("\n🌐 To start the web interface:")
        print("   python main.py --web")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        print(f"❌ Initialization error: {e}")
        return False
    finally:
        shutdown_app()


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Document Q&A System")
    parser.add_argument(
        "--web", 
        action="store_true", 
        help="Start the web interface (default)"
    )
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Run system health check"
    )
    parser.add_argument(
        "--init", 
        action="store_true", 
        help="Initialize system only (no web interface)"
    )
    
    args = parser.parse_args()
    
    # Default to web interface if no specific command
    if not any([args.check, args.init]):
        args.web = True
    
    success = False
    
    try:
        if args.check:
            success = run_system_check()
        elif args.init:
            success = run_init_only()
        elif args.web:
            success = run_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        success = True
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()