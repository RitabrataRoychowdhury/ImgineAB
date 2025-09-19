#!/usr/bin/env python3
"""
Simple test to verify the UI components work without HTML issues
"""

import streamlit as st
import sys
import os

# Add src directory to path
sys.path.append('.')

from src.ui.styling import UIStyler

def main():
    """Test the simplified UI components"""
    
    st.set_page_config(
        page_title="Simple UI Test",
        page_icon="🧪",
        layout="wide"
    )
    
    # Test title with icon
    st.title(f"{UIStyler.get_icon('documents')} Simple UI Test")
    st.write("Testing simplified UI components without complex HTML")
    
    # Test sidebar
    with st.sidebar:
        st.subheader(f"{UIStyler.get_icon('status')} Status")
        st.success(UIStyler.create_status_badge("online", "System Online"))
        
        st.subheader(f"{UIStyler.get_icon('home')} Navigation")
        nav_options = [
            f"{UIStyler.get_icon('upload')} Upload",
            f"{UIStyler.get_icon('documents')} Documents", 
            f"{UIStyler.get_icon('qa')} Q&A",
            f"{UIStyler.get_icon('status')} Status"
        ]
        
        selected = st.selectbox("Choose:", nav_options)
        st.write(f"Selected: {selected}")
    
    # Test main content
    st.markdown("---")
    
    # Test metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents", f"{UIStyler.get_icon('documents')} 5")
    
    with col2:
        st.metric("Status", f"{UIStyler.get_icon('online')} Online")
    
    with col3:
        st.metric("Queue", f"{UIStyler.get_icon('queue')} 0")
    
    # Test status badges
    st.subheader(f"{UIStyler.get_icon('info')} Status Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(UIStyler.create_status_badge("completed", "Success"))
    
    with col2:
        st.warning(UIStyler.create_status_badge("warning", "Warning"))
    
    with col3:
        st.error(UIStyler.create_status_badge("failed", "Error"))
    
    # Test buttons
    st.subheader(f"{UIStyler.get_icon('settings')} Button Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"{UIStyler.get_icon('upload')} Upload"):
            st.success("Upload clicked!")
    
    with col2:
        if st.button(f"{UIStyler.get_icon('refresh')} Refresh"):
            st.info("Refresh clicked!")
    
    with col3:
        if st.button(f"{UIStyler.get_icon('delete')} Delete"):
            st.error("Delete clicked!")
    
    # Test icons
    st.subheader(f"{UIStyler.get_icon('info')} All Icons")
    
    icons_to_test = [
        'online', 'offline', 'warning', 'processing', 'completed', 'failed', 'pending',
        'upload', 'download', 'delete', 'edit', 'view', 'search', 'refresh', 'settings',
        'home', 'documents', 'qa', 'history', 'status', 'about',
        'pdf', 'txt', 'docx', 'database', 'api', 'queue', 'metrics', 'error', 'success'
    ]
    
    cols = st.columns(5)
    for i, icon_name in enumerate(icons_to_test):
        with cols[i % 5]:
            st.write(f"{UIStyler.get_icon(icon_name)} {icon_name}")

if __name__ == "__main__":
    main()