#!/usr/bin/env python3
"""
Simple Streamlit test app to verify UI components
"""

import streamlit as st
import sys
import os

# Add src directory to path
sys.path.append('.')

from src.ui.styling import UIStyler

def main():
    """Test the UI components"""
    
    st.set_page_config(
        page_title="UI Test",
        page_icon="🧪",
        layout="wide"
    )
    
    # Apply basic styling
    UIStyler.inject_css()
    
    # Test title with icon
    st.title(f"{UIStyler.get_icon('documents')} UI Component Test")
    
    # Test icons
    st.subheader(f"{UIStyler.get_icon('success')} Icon Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"Documents: {UIStyler.get_icon('documents')}")
        st.write(f"Success: {UIStyler.get_icon('success')}")
        st.write(f"Error: {UIStyler.get_icon('error')}")
    
    with col2:
        st.write(f"Upload: {UIStyler.get_icon('upload')}")
        st.write(f"Processing: {UIStyler.get_icon('processing')}")
        st.write(f"Queue: {UIStyler.get_icon('queue')}")
    
    with col3:
        st.write(f"Settings: {UIStyler.get_icon('settings')}")
        st.write(f"Database: {UIStyler.get_icon('database')}")
        st.write(f"API: {UIStyler.get_icon('api')}")
    
    # Test status badges
    st.subheader(f"{UIStyler.get_icon('info')} Status Badge Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(UIStyler.create_status_badge("success", "Success Test"))
    
    with col2:
        st.warning(UIStyler.create_status_badge("warning", "Warning Test"))
    
    with col3:
        st.error(UIStyler.create_status_badge("error", "Error Test"))
    
    # Test metrics
    st.subheader(f"{UIStyler.get_icon('metrics')} Metric Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"{UIStyler.get_icon('documents')} Documents", "5")
    
    with col2:
        st.metric(f"{UIStyler.get_icon('queue')} Queue", "2")
    
    with col3:
        st.metric(f"{UIStyler.get_icon('online')} Status", "Online")
    
    # Test buttons
    st.subheader(f"{UIStyler.get_icon('settings')} Button Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"{UIStyler.get_icon('upload')} Upload"):
            st.success("Upload button clicked!")
    
    with col2:
        if st.button(f"{UIStyler.get_icon('refresh')} Refresh"):
            st.info("Refresh button clicked!")
    
    with col3:
        if st.button(f"{UIStyler.get_icon('delete')} Delete"):
            st.error("Delete button clicked!")

if __name__ == "__main__":
    main()