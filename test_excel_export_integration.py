#!/usr/bin/env python3
"""
Integration test runner for Excel Export Engine implementation.
Tests the complete workflow and never-fail guarantee.
"""

import sys
import os
import tempfile
import traceback
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from services.excel_export_engine import ExcelExportEngine, ExportRequest
from services.request_analyzer import RequestAnalyzer
from services.data_formatter import DataFormatter
from storage.document_storage import DocumentStorage
from unittest.mock import Mock


def test_never_fail_guarantee():
    """Test the never-fail guarantee with various scenarios."""
    print("🧪 Testing Never-Fail Guarantee...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        mock_storage = Mock(spec=DocumentStorage)
        export_engine = ExcelExportEngine(mock_storage, temp_dir)
        
        test_cases = [
            {
                'name': 'Simple Data',
                'data': {'key': 'value', 'number': 42},
                'request': 'Export this data'
            },
            {
                'name': 'Complex Nested Data',
                'data': {
                    'summary': {'title': 'Test', 'type': 'Contract'},
                    'risks': [
                        {'risk': 'Risk 1', 'severity': 'High'},
                        {'risk': 'Risk 2', 'severity': 'Low'}
                    ],
                    'parties': ['Party A', 'Party B']
                },
                'request': 'Create a comprehensive report'
            },
            {
                'name': 'Empty Data',
                'data': {},
                'request': 'Export empty data'
            },
            {
                'name': 'None Data',
                'data': None,
                'request': 'Export null data'
            },
            {
                'name': 'List Data',
                'data': [
                    {'item': 'Item 1', 'value': 100},
                    {'item': 'Item 2', 'value': 200}
                ],
                'request': 'Export list as table'
            }
        ]
        
        success_count = 0
        for test_case in test_cases:
            try:
                print(f"  Testing: {test_case['name']}")
                
                result = export_engine.export_tabular_data(
                    test_case['data'],
                    test_case['request'],
                    ['excel', 'csv', 'text']
                )
                
                if result.success and os.path.exists(result.file_path):
                    print(f"    ✅ Success - Format: {result.format_type}")
                    if result.fallback_used:
                        print(f"    ⚠️  Fallback used")
                    success_count += 1
                else:
                    print(f"    ❌ Failed - {result.error_message}")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
        
        print(f"Never-fail guarantee: {success_count}/{len(test_cases)} tests passed")
        return success_count == len(test_cases)


def test_request_analysis():
    """Test request analysis for export detection."""
    print("\n🔍 Testing Request Analysis...")
    
    analyzer = RequestAnalyzer()
    
    test_requests = [
        {
            'request': 'Can you export this to Excel?',
            'should_export': True,
            'expected_confidence': 0.8
        },
        {
            'request': 'List all the risks in this document',
            'should_export': True,
            'expected_confidence': 0.6
        },
        {
            'request': 'What is this document about?',
            'should_export': False,
            'expected_confidence': 0.3
        },
        {
            'request': 'Generate a risk analysis report',
            'should_export': True,
            'expected_confidence': 0.7
        },
        {
            'request': 'Show me all parties in a table format',
            'should_export': True,
            'expected_confidence': 0.8
        }
    ]
    
    success_count = 0
    for test in test_requests:
        try:
            analysis = analyzer.analyze_request(test['request'])
            
            export_correct = analysis.should_generate_export == test['should_export']
            confidence_reasonable = abs(analysis.confidence - test['expected_confidence']) < 0.3
            
            if export_correct and confidence_reasonable:
                print(f"  ✅ '{test['request'][:50]}...' - Export: {analysis.should_generate_export}, Confidence: {analysis.confidence:.2f}")
                success_count += 1
            else:
                print(f"  ❌ '{test['request'][:50]}...' - Expected export: {test['should_export']}, Got: {analysis.should_generate_export}")
                
        except Exception as e:
            print(f"  ❌ Exception analyzing request: {str(e)}")
    
    print(f"Request analysis: {success_count}/{len(test_requests)} tests passed")
    return success_count == len(test_requests)


def test_data_formatting():
    """Test data formatting capabilities."""
    print("\n📊 Testing Data Formatting...")
    
    formatter = DataFormatter()
    
    test_cases = [
        {
            'name': 'Text Response',
            'data': 'This is a test response with key information: Value 1, Value 2',
            'response_type': 'text'
        },
        {
            'name': 'Structured Data',
            'data': {
                'summary': 'Test summary',
                'items': [{'name': 'Item 1'}, {'name': 'Item 2'}]
            },
            'response_type': 'structured'
        },
        {
            'name': 'Q&A History',
            'data': [
                {
                    'question': 'What is this?',
                    'answer': 'This is a test',
                    'timestamp': '2024-01-01T10:00:00'
                }
            ],
            'response_type': 'qa_history'
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        try:
            print(f"  Testing: {test_case['name']}")
            
            result = formatter.format_response_for_export(
                test_case['data'],
                test_case['response_type']
            )
            
            if result.export_ready and 'tabular_data' in result.structured_data:
                print(f"    ✅ Formatted successfully")
                success_count += 1
            else:
                print(f"    ❌ Formatting failed")
                
        except Exception as e:
            print(f"    ❌ Exception: {str(e)}")
    
    print(f"Data formatting: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)


def test_template_generation():
    """Test template generation for different report types."""
    print("\n📋 Testing Template Generation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_storage = Mock(spec=DocumentStorage)
        export_engine = ExcelExportEngine(mock_storage, temp_dir)
        
        template_tests = [
            {
                'name': 'Risk Analysis',
                'data': {
                    'risks': [
                        {
                            'risk_id': 'R001',
                            'description': 'Test risk',
                            'severity': 'High',
                            'category': 'Legal'
                        }
                    ]
                },
                'document_info': {'title': 'Test Doc', 'id': 'test-1'}
            },
            {
                'name': 'Document Summary',
                'data': {
                    'overview': 'Test overview',
                    'key_terms': {'Term 1': 'Definition 1'},
                    'important_dates': [{'date': '2024-12-31', 'description': 'End date'}]
                }
            },
            {
                'name': 'Portfolio Analysis',
                'data': [
                    {
                        'title': 'Doc 1',
                        'document_type': 'Contract',
                        'status': 'Active'
                    }
                ]
            }
        ]
        
        success_count = 0
        for test in template_tests:
            try:
                print(f"  Testing: {test['name']}")
                
                if test['name'] == 'Risk Analysis':
                    result = export_engine.generate_risk_analysis_report(
                        test['data'], test['document_info']
                    )
                elif test['name'] == 'Document Summary':
                    result = export_engine.generate_document_summary_export(test['data'])
                elif test['name'] == 'Portfolio Analysis':
                    result = export_engine.generate_portfolio_analysis_report(test['data'])
                
                if result.success and os.path.exists(result.file_path):
                    print(f"    ✅ Generated {result.format_type} file: {result.filename}")
                    success_count += 1
                else:
                    print(f"    ❌ Failed to generate template")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
                traceback.print_exc()
        
        print(f"Template generation: {success_count}/{len(template_tests)} tests passed")
        return success_count == len(template_tests)


def test_fallback_mechanisms():
    """Test fallback mechanisms when primary export fails."""
    print("\n🔄 Testing Fallback Mechanisms...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_storage = Mock(spec=DocumentStorage)
        export_engine = ExcelExportEngine(mock_storage, temp_dir)
        
        # Test with data that might cause Excel generation issues
        problematic_data = {
            'large_text': 'x' * 50000,  # Very large text
            'special_chars': '™®©€£¥§¶•‰',
            'nested_deep': {'level1': {'level2': {'level3': {'level4': 'deep'}}}},
            'mixed_types': [1, 'string', {'key': 'value'}, [1, 2, 3]]
        }
        
        try:
            result = export_engine.export_tabular_data(
                problematic_data,
                'Export problematic data',
                ['excel', 'csv', 'text']
            )
            
            if result.success and os.path.exists(result.file_path):
                print(f"  ✅ Fallback successful - Format: {result.format_type}")
                if result.fallback_used:
                    print(f"    ⚠️  Fallback mechanism activated")
                return True
            else:
                print(f"  ❌ Fallback failed")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception in fallback test: {str(e)}")
            return False


def test_ui_integration_compatibility():
    """Test compatibility with UI integration requirements."""
    print("\n🖥️  Testing UI Integration Compatibility...")
    
    # Test that all required classes can be imported and instantiated
    try:
        from services.excel_export_engine import ExcelExportEngine
        from services.request_analyzer import RequestAnalyzer  
        from services.data_formatter import DataFormatter
        
        print("  ✅ All classes imported successfully")
        
        # Test instantiation
        mock_storage = Mock(spec=DocumentStorage)
        export_engine = ExcelExportEngine(mock_storage)
        analyzer = RequestAnalyzer()
        formatter = DataFormatter()
        
        print("  ✅ All classes instantiated successfully")
        
        # Test basic method calls
        analysis = analyzer.analyze_request("Test request")
        formatted = formatter.format_response_for_export("Test data", "text")
        
        print("  ✅ Basic method calls successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ UI integration compatibility failed: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("🚀 Excel Export Engine Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Never-Fail Guarantee", test_never_fail_guarantee),
        ("Request Analysis", test_request_analysis),
        ("Data Formatting", test_data_formatting),
        ("Template Generation", test_template_generation),
        ("Fallback Mechanisms", test_fallback_mechanisms),
        ("UI Integration Compatibility", test_ui_integration_compatibility)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
            traceback.print_exc()
        
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Excel Export Engine is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)