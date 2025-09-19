"""
Simple icon system for the Document Q&A System UI.
Just provides icons - no complex styling or HTML.
"""

class UIStyler:
    """Simple icon system for UI enhancement."""
    
    # NO CSS INJECTION - JUST ICONS!
    
    # Simple icon system - just Unicode symbols
    ICONS = {
        # Status icons
        'online': '🟢',
        'offline': '🔴',
        'warning': '🟡',
        'processing': '🔄',
        'completed': '✅',
        'failed': '❌',
        'pending': '⏳',
        
        # Action icons
        'upload': '📤',
        'download': '📥',
        'delete': '🗑️',
        'edit': '✏️',
        'view': '👁️',
        'search': '🔍',
        'refresh': '🔄',
        'settings': '⚙️',
        'help': '❓',
        'info': 'ℹ️',
        
        # Navigation icons
        'home': '🏠',
        'documents': '📄',
        'qa': '💬',
        'history': '📋',
        'status': '📊',
        'about': 'ℹ️',
        
        # File type icons
        'pdf': '📕',
        'txt': '📄',
        'docx': '📘',
        'unknown': '📄',
        
        # System icons
        'database': '🗄️',
        'api': '🔗',
        'queue': '📋',
        'metrics': '📈',
        'error': '⚠️',
        'success': '✅',
        'loading': '⏳',
        
        # Legal document icons
        'legal': '🏛️',
        'contract': '📋',
        'mta': '🧬',
        'nda': '🤐',
        'analysis': '⚖️',
    }
    
    @classmethod
    def get_icon(cls, icon_name: str) -> str:
        """Get a simple icon."""
        return cls.ICONS.get(icon_name, '📄')
    
    @classmethod
    def create_status_badge(cls, status: str, text: str = None) -> str:
        """Create a simple status text with icon."""
        display_text = text or status.title()
        icon = cls.get_icon(status)
        return f"{icon} {display_text}"