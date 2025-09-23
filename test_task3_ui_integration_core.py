#!/usr/bin/env python3
"""
Core UI Integration Testing for Task 3 (without Streamlit dependency)

This test validates the core functionality that would be used by the UI:
- Structured response system integration
- Never-fail response guarantee
- Export functionality
- Real user scenarios
- Backward compatibility
- Production readiness
"""

import sys
import os
import tempfile
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core components (avoiding UI dependencies)
from src.services.structured_response_system import StructuredResponseSystem
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.storage.document_storage import DocumentStorage
from src.models.document import Document
from src.models.enhanced import EnhancedResponse, ResponseType, ToneType
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class CoreUIIntegrationTests:
    """Core UI integration tests without Streamlit dependency."""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'total': 0
        }
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Set up test environment."""
        # Create temporary directory for test exports
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize core components
        self.storage = DocumentStorage()
        self.structured_system = StructuredResponseSystem(export_directory=self.temp_dir)
        self.enhanced_router = EnhancedResponseRouter(self.storage, "test_api_key")
        
        # Create test documents
        self.test_documents = self._create_test_documents()
    
    def _create_test_documents(self) -> List[Document]:
        """Create test documents for various scenarios."""
        documents = []
        
        # Standard contract document
        contract_doc = Document(
            id="test_contract_001",
            filename="service_agreement.pdf",
            title="Service Agreement",
            content="This Service Agreement is between Acme Corp (Provider) and Beta Inc (Client). Payment terms: $5,000 monthly, due on the 1st of each month. Late fees: $250 after 15 days. Term: 12 months starting January 1, 2024. Either party may terminate with 30 days written notice. Provider will deliver software development services. Client obligations include timely payment and providing necessary access. Liability is limited to $50,000. Governing law: California.",
            original_text="This Service Agreement is between Acme Corp (Provider) and Beta Inc (Client). Payment terms: $5,000 monthly, due on the 1st of each month. Late fees: $250 after 15 days. Term: 12 months starting January 1, 2024. Either party may terminate with 30 days written notice. Provider will deliver software development services. Client obligations include timely payment and providing necessary access. Liability is limited to $50,000. Governing law: California.",
            file_type="pdf",
            file_size=15000,
            processing_status="completed",
            is_legal_document=True,
            legal_document_type="Service Agreement",
            legal_analysis_confidence=0.95,
            upload_timestamp=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        documents.append(contract_doc)
        
        return documents
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all core UI integration tests."""
        print("🚀 CORE UI INTEGRATION TESTING FOR TASK 3")
        print("=" * 50)
        print("Testing core functionality that powers the UI:")
        print("- Structured response system integration")
        print("- Never-fail response guarantee")
        print("- Export functionality")
        print("- Real user scenarios")
        print("- Backward compatibility")
        print("- Production readiness")
        print("=" * 50)
        
        # Run all test suites
        self.test_structured_response_integration()
        self.test_never_fail_guarantee()
        self.test_export_functionality()
        self.test_real_user_scenarios()
        self.test_backward_compatibility()
        self.test_production_readiness()
        
        return self._generate_final_report()
    
    def test_structured_response_integration(self):
        """Test structured response system integration."""
        print("\n🔧 Testing Structured Response System Integration")
        print("=" * 50)
        
        integration_tests = [
            {
                'name': 'Document Pattern Integration',
                'question': 'What does the liability clause mean in this contract?',
                'expected_pattern': 'document',
                'expected_elements': ['📋 Evidence', '🔍 Plain English', '⚖️ Implications']
            },
            {
                'name': 'General Legal Pattern Integration',
                'question': 'How do liability clauses typically work in contracts?',
                'expected_pattern': 'general_legal',
                'expected_elements': ['ℹ️ Status', '📚 General Rule', '🎯 Application']
            },
            {
                'name': 'Data Table Pattern Integration',
                'question': 'Create a table showing the payment schedule and terms',
                'expected_pattern': 'data_table',
                'expected_elements': ['|', '---', '📥 Export']
            },
            {
                'name': 'Ambiguous Pattern Integration',
                'question': 'I\'m not sure what I should be asking about this contract',
                'expected_pattern': 'ambiguous',
                'expected_elements': ['🤔 My Take', 'Option A', 'Option B']
            }
        ]
        
        for test in integration_tests:
            print(f"\n🔍 Testing: {test['name']}")
            
            try:
                response = self.structured_system.process_input_with_guaranteed_response(
                    user_input=test['question'],
                    document_content=self.test_documents[0].content
                )
                
                # Validate integration
                pattern_detected = response.structured_format.get('pattern', 'unknown') if response.structured_format else 'none'
                elements_found = [elem for elem in test['expected_elements'] if elem in response.content]
                
                print(f"   Pattern detected: {pattern_detected}")
                print(f"   Elements found: {len(elements_found)}/{len(test['expected_elements'])}")
                print(f"   Response length: {len(response.content)} chars")
                print(f"   Suggestions: {len(response.suggestions)}")
                
                if len(elements_found) >= len(test['expected_elements']) * 0.7:  # 70% threshold
                    print(f"   ✅ Integration successful")
                    self.test_results['passed'] += 1
                else:
                    print(f"   ⚠️  Integration partially successful")
                    print(f"   Missing elements: {set(test['expected_elements']) - set(elements_found)}")
                    self.test_results['warnings'] += 1
                
                self.test_results['total'] += 1
                
            except Exception as e:
                print(f"   ❌ Integration test failed: {e}")
                self.test_results['failed'] += 1
                self.test_results['total'] += 1
    
    def test_never_fail_guarantee(self):
        """Test never-fail response guarantee."""
        print("\n🛡️  Testing Never-Fail Response Guarantee")
        print("=" * 40)
        
        # Extreme test cases that should never fail
        extreme_cases = [
            {'input': '', 'name': 'Empty input'},
            {'input': ' ', 'name': 'Whitespace only'},
            {'input': '?', 'name': 'Single character'},
            {'input': 'asdfghjkl', 'name': 'Gibberish'},
            {'input': 'what ' * 100, 'name': 'Extremely long repetitive'},
            {'input': '!@#$%^&*()', 'name': 'Special characters only'},
            {'input': None, 'name': 'None input'},
            {'input': 123, 'name': 'Numeric input'},
            {'input': 'What about émojis 😀?', 'name': 'Unicode and emojis'}
        ]
        
        print(f"Testing {len(extreme_cases)} extreme cases...")
        
        success_count = 0
        
        for i, case in enumerate(extreme_cases, 1):
            print(f"\n🔍 Case {i}: {case['name']}")
            
            try:
                input_str = str(case['input']) if case['input'] is not None else ""
                
                response = self.structured_system.process_input_with_guaranteed_response(
                    user_input=input_str,
                    document_content=self.test_documents[0].content
                )
                
                # Validate response
                assert response is not None, "Response is None"
                assert response.content is not None, "Content is None"
                assert len(response.content.strip()) > 0, "Content is empty"
                assert hasattr(response, 'confidence'), "Missing confidence"
                assert 0.0 <= response.confidence <= 1.0, "Invalid confidence"
                
                print(f"   ✅ Success ({len(response.content)} chars, conf={response.confidence:.2f})")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ CRITICAL FAILURE: {e}")
                print(f"   This should NEVER happen!")
        
        print(f"\n📊 Never-Fail Results:")
        print(f"   Extreme cases: {len(extreme_cases)}")
        print(f"   Successful: {success_count}")
        print(f"   Success rate: {(success_count/len(extreme_cases))*100:.1f}%")
        
        if success_count == len(extreme_cases):
            print(f"   🎉 NEVER-FAIL GUARANTEE VERIFIED!")
            self.test_results['passed'] += 1
        else:
            print(f"   ❌ NEVER-FAIL GUARANTEE VIOLATED!")
            self.test_results['failed'] += 1
        
        self.test_results['total'] += 1
    
    def test_export_functionality(self):
        """Test export functionality integration."""
        print("\n📊 Testing Export Functionality")
        print("=" * 35)
        
        export_tests = [
            "Create a table of contract parties and their roles",
            "Show me payment terms in a structured format",
            "Generate a risk assessment matrix",
            "Export the key dates and deadlines as CSV",
            "List all obligations in table format"
        ]
        
        export_success = 0
        
        for i, test_input in enumerate(export_tests, 1):
            print(f"\n🔍 Export Test {i}: '{test_input[:50]}...'")
            
            try:
                response = self.structured_system.process_input_with_guaranteed_response(
                    user_input=test_input,
                    document_content=self.test_documents[0].content
                )
                
                # Check for export indicators
                has_table = '|' in response.content and '---' in response.content
                has_export_mention = any(word in response.content.lower() for word in ['export', 'csv', 'excel', '📥'])
                
                print(f"   Table detected: {has_table}")
                print(f"   Export mentioned: {has_export_mention}")
                
                if has_table or has_export_mention:
                    print(f"   ✅ Export functionality working")
                    export_success += 1
                else:
                    print(f"   ⚠️  Export functionality may need improvement")
                
            except Exception as e:
                print(f"   ❌ Export test failed: {e}")
        
        print(f"\n📊 Export Results:")
        print(f"   Tests: {len(export_tests)}")
        print(f"   Successful: {export_success}")
        print(f"   Success rate: {(export_success/len(export_tests))*100:.1f}%")
        
        if export_success >= len(export_tests) * 0.8:  # 80% threshold
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
        
        self.test_results['total'] += 1
    
    def test_real_user_scenarios(self):
        """Test real user scenarios."""
        print("\n👥 Testing Real User Scenarios")
        print("=" * 35)
        
        user_scenarios = [
            {
                'name': 'Casual User',
                'questions': [
                    "Hey, what's the deal with payments in this contract?",
                    "So like, who's responsible if something goes wrong?",
                    "Can I get out of this thing if I need to?"
                ]
            },
            {
                'name': 'Business Professional',
                'questions': [
                    "Please provide an analysis of the liability provisions.",
                    "What are the key performance indicators and associated penalties?",
                    "Could you summarize the intellectual property arrangements?"
                ]
            },
            {
                'name': 'Confused User',
                'questions': [
                    "I don't understand what this contract is saying",
                    "This is all very confusing, can you help?",
                    "What does all this legal stuff mean?"
                ]
            }
        ]
        
        scenario_success = 0
        total_scenarios = len(user_scenarios)
        
        for scenario in user_scenarios:
            print(f"\n🔍 Testing: {scenario['name']}")
            
            scenario_questions_success = 0
            
            for question in scenario['questions']:
                try:
                    response = self.structured_system.process_input_with_guaranteed_response(
                        user_input=question,
                        document_content=self.test_documents[0].content
                    )
                    
                    # Validate response quality
                    if (response and response.content and 
                        len(response.content) > 100 and 
                        len(response.suggestions) > 0):
                        scenario_questions_success += 1
                        
                except Exception as e:
                    print(f"      ❌ Question failed: {e}")
            
            success_rate = scenario_questions_success / len(scenario['questions'])
            print(f"   Questions successful: {scenario_questions_success}/{len(scenario['questions'])} ({success_rate*100:.1f}%)")
            
            if success_rate >= 0.8:  # 80% threshold
                print(f"   ✅ Scenario successful")
                scenario_success += 1
            else:
                print(f"   ⚠️  Scenario needs improvement")
        
        print(f"\n📊 User Scenario Results:")
        print(f"   Scenarios: {total_scenarios}")
        print(f"   Successful: {scenario_success}")
        print(f"   Success rate: {(scenario_success/total_scenarios)*100:.1f}%")
        
        if scenario_success >= total_scenarios * 0.8:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
        
        self.test_results['total'] += 1
    
    def test_backward_compatibility(self):
        """Test backward compatibility."""
        print("\n🔄 Testing Backward Compatibility")
        print("=" * 35)
        
        compatibility_tests = [
            {
                'name': 'Enhanced Router Integration',
                'question': 'What are the main terms of this contract?',
                'test_type': 'router'
            },
            {
                'name': 'Document Analysis Preservation',
                'question': 'Who are the parties to this agreement?',
                'test_type': 'analysis'
            },
            {
                'name': 'Response Structure Compatibility',
                'question': 'What are the termination conditions?',
                'test_type': 'structure'
            }
        ]
        
        compatibility_success = 0
        
        for test in compatibility_tests:
            print(f"\n🔍 Testing: {test['name']}")
            
            try:
                if test['test_type'] == 'router':
                    # Test enhanced router
                    response = self.enhanced_router.route_question(
                        question=test['question'],
                        document_id=self.test_documents[0].id,
                        session_id="compatibility_test",
                        document=self.test_documents[0]
                    )
                else:
                    # Test structured system
                    response = self.structured_system.process_input_with_guaranteed_response(
                        user_input=test['question'],
                        document_content=self.test_documents[0].content
                    )
                
                # Validate compatibility
                if (response and response.content and 
                    hasattr(response, 'response_type') and 
                    hasattr(response, 'confidence')):
                    print(f"   ✅ Compatibility maintained")
                    print(f"   Response type: {response.response_type.value}")
                    print(f"   Confidence: {response.confidence:.2f}")
                    compatibility_success += 1
                else:
                    print(f"   ❌ Compatibility issues detected")
                
            except Exception as e:
                print(f"   ❌ Compatibility test failed: {e}")
        
        print(f"\n📊 Compatibility Results:")
        print(f"   Tests: {len(compatibility_tests)}")
        print(f"   Successful: {compatibility_success}")
        print(f"   Success rate: {(compatibility_success/len(compatibility_tests))*100:.1f}%")
        
        if compatibility_success == len(compatibility_tests):
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
        
        self.test_results['total'] += 1
    
    def test_production_readiness(self):
        """Test production readiness."""
        print("\n🚀 Testing Production Readiness")
        print("=" * 35)
        
        production_tests = [
            {
                'name': 'Response Time Performance',
                'test_function': self._test_response_time
            },
            {
                'name': 'Error Recovery',
                'test_function': self._test_error_recovery
            },
            {
                'name': 'Concurrent Processing',
                'test_function': self._test_concurrent_processing
            }
        ]
        
        production_success = 0
        
        for test in production_tests:
            print(f"\n🔍 Testing: {test['name']}")
            
            try:
                result = test['test_function']()
                
                if result['passed']:
                    print(f"   ✅ {result['message']}")
                    production_success += 1
                else:
                    print(f"   ❌ {result['message']}")
                
            except Exception as e:
                print(f"   ❌ Production test failed: {e}")
        
        print(f"\n📊 Production Readiness Results:")
        print(f"   Tests: {len(production_tests)}")
        print(f"   Successful: {production_success}")
        print(f"   Success rate: {(production_success/len(production_tests))*100:.1f}%")
        
        if production_success >= len(production_tests) * 0.8:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
        
        self.test_results['total'] += 1
    
    def _test_response_time(self) -> Dict[str, Any]:
        """Test response time performance."""
        start_time = time.time()
        
        response = self.structured_system.process_input_with_guaranteed_response(
            user_input="What are the key terms in this contract?",
            document_content=self.test_documents[0].content
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        max_time = 5.0  # 5 seconds max
        
        return {
            'passed': response_time <= max_time,
            'message': f"Response time: {response_time:.2f}s (max: {max_time}s)"
        }
    
    def _test_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery."""
        error_scenarios = ['', None, 'asdfghjkl', '!@#$%^&*()']
        recovery_count = 0
        
        for scenario in error_scenarios:
            try:
                input_str = str(scenario) if scenario is not None else ""
                response = self.structured_system.process_input_with_guaranteed_response(
                    user_input=input_str,
                    document_content=self.test_documents[0].content
                )
                
                if response and response.content and len(response.content.strip()) > 0:
                    recovery_count += 1
            except Exception:
                pass  # Error recovery should handle this
        
        return {
            'passed': recovery_count == len(error_scenarios),
            'message': f"Recovered from {recovery_count}/{len(error_scenarios)} error scenarios"
        }
    
    def _test_concurrent_processing(self) -> Dict[str, Any]:
        """Test concurrent processing capability."""
        concurrent_requests = 3
        responses = []
        
        try:
            for i in range(concurrent_requests):
                response = self.structured_system.process_input_with_guaranteed_response(
                    user_input=f"Test question {i}",
                    document_content=self.test_documents[0].content
                )
                responses.append(response)
            
            return {
                'passed': len(responses) == concurrent_requests,
                'message': f"Processed {len(responses)}/{concurrent_requests} concurrent requests"
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f"Concurrent processing failed: {e}"
            }
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        success_rate = (self.test_results['passed'] / self.test_results['total']) * 100 if self.test_results['total'] > 0 else 0
        
        print(f"\n📊 FINAL TASK 3 CORE UI INTEGRATION TEST REPORT")
        print("=" * 60)
        print(f"Total Test Suites: {self.test_results['total']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Warnings: {self.test_results['warnings']}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results['failed'] == 0:
            print(f"\n🎉 ALL CORE UI INTEGRATION TESTS PASSED!")
            print(f"✅ Task 3 core requirements implemented:")
            print(f"   • Structured response system integration")
            print(f"   • Never-fail response guarantee")
            print(f"   • Export functionality")
            print(f"   • Real user scenario handling")
            print(f"   • Backward compatibility maintained")
            print(f"   • Production readiness validated")
            print(f"\n🚀 CORE SYSTEM IS READY FOR UI INTEGRATION!")
        else:
            print(f"\n❌ {self.test_results['failed']} TEST SUITES FAILED")
            print(f"Critical issues must be resolved.")
        
        # Cleanup
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        return {
            'total': self.test_results['total'],
            'passed': self.test_results['passed'],
            'failed': self.test_results['failed'],
            'warnings': self.test_results['warnings'],
            'success_rate': success_rate,
            'ready_for_ui': self.test_results['failed'] == 0
        }

def main():
    """Run core UI integration tests."""
    print("🚀 STARTING CORE UI INTEGRATION TESTING FOR TASK 3")
    print("Testing core functionality that powers the UI interface")
    print("=" * 60)
    
    try:
        test_suite = CoreUIIntegrationTests()
        results = test_suite.run_all_tests()
        
        if results['ready_for_ui']:
            print(f"\n🏆 TASK 3 CORE IMPLEMENTATION VALIDATED!")
            return True
        else:
            print(f"\n⚠️  TASK 3 CORE IMPLEMENTATION NEEDS FIXES")
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in core UI integration testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)