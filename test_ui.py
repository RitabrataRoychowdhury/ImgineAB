#!/usr/bin/env python3
"""
Simple test script to verify UI components are working
"""

import sys
import os
sys.path.append('.')

def test_icons():
    """Test icon functionality"""
    try:
        from src.ui.styling import UIStyler
        
        print("Testing icon system...")
        print(f"Documents icon: {UIStyler.get_icon('documents')}")
        print(f"Success icon: {UIStyler.get_icon('success')}")
        print(f"Status badge: {UIStyler.create_status_badge('success', 'Test')}")
        print("✅ Icon system working!")
        return True
    except Exception as e:
        print(f"❌ Icon system error: {e}")
        return False

def test_colors():
    """Test color system"""
    try:
        from src.ui.styling import UIStyler
        
        print("Testing color system...")
        print(f"Primary color: {UIStyler.COLORS['primary']}")
        print(f"Success color: {UIStyler.COLORS['success']}")
        print("✅ Color system working!")
        return True
    except Exception as e:
        print(f"❌ Color system error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing UI Components...")
    
    icon_test = test_icons()
    color_test = test_colors()
    
    if icon_test and color_test:
        print("🎉 All UI components working correctly!")
    else:
        print("⚠️ Some UI components have issues")