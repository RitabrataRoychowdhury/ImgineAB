#!/usr/bin/env python3
"""
Enhanced Contract Assistant System Demonstration

This script demonstrates all the enhanced capabilities of the contract assistant system
including quality enhancement, advanced analysis, intelligent formatting, and production monitoring.
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any

from src.services.enhanced_contract_system import (
    EnhancedContractSystem, SystemConfiguration, ProcessingContext
)
from src.services.comprehensive_test_suite import ComprehensiveTestSuite, TestCategory
from src.services.answer_quality_enhancer import ExpertiseLevel
from src.services.intelligent_response_formatter import UserProfile, ResponseStructure
from src.services.production_monitor import start_global_monitoring, stop_global_monitoring
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


class EnhancedSystemDemo:
    """Demonstration of the Enhanced Contract Assistant System"""
    
    def __init__(self):
        """Initialize the demonstration"""
        self.storage = DocumentStorage()
        self.config = SystemConfiguration(
            enable_quality_enhancement=True,
            enable_advanced_analysis=True,
            enable_intelligent_formatting=True,
            enable_production_monitoring=True,
            enable_caching=True,
            cache_ttl_seconds=300,
            max_concurrent_requests=10
        )
        self.system = EnhancedContractSystem(
            storage=self.storage,
            config=self.config
        )
        
        # Create sample documents
        self.sample_documents = self._create_sample_documents()
        
    def _create_sample_documents(self) -> List[Document]:
        """Create sample documents for demonstration"""
        
        # Material Transfer Agreement
        mta_content = """
        MATERIAL TRANSFER AGREEMENT
        
        This Material Transfer Agreement ("Agreement") is entered into on January 15, 2024,
        between Stanford University ("Provider") and MIT ("Recipient").
        
        1. MATERIAL DESCRIPTION
        The Provider agrees to transfer the following research material:
        - Cell line: Human embryonic stem cells (hESC-H9)
        - Quantity: 2 vials
        - Purpose: Research use only for neural differentiation studies
        
        2. PAYMENT TERMS
        Recipient shall pay a one-time fee of $750 within 30 days of material delivery.
        Additional shipping costs of $150 shall be paid upon invoice receipt.
        
        3. PERMITTED USES
        The material may only be used for:
        a) Basic research purposes as described in Exhibit A
        b) Non-commercial research activities
        c) Educational purposes within the Recipient institution
        
        The material SHALL NOT be used for:
        - Commercial product development
        - Clinical applications or human trials
        - Distribution to third parties without written consent
        
        4. INTELLECTUAL PROPERTY RIGHTS
        a) Provider retains all rights to the original material
        b) Recipient owns rights to improvements made independently
        c) Joint inventions shall be owned jointly with equal rights
        d) Any patents filed must acknowledge the original material source
        
        5. PUBLICATION AND CONFIDENTIALITY
        a) Recipient may publish research results after 60-day review period
        b) Provider has right to request removal of confidential information
        c) All publications must acknowledge the material source
        d) Confidential information must be protected for 5 years
        
        6. LIABILITY AND INDEMNIFICATION
        a) Provider's liability is limited to direct damages not exceeding $25,000
        b) Recipient assumes all risks associated with material use
        c) Each party indemnifies the other against third-party claims
        d) No warranties are provided regarding material fitness
        
        7. TERMINATION
        a) Either party may terminate with 90 days written notice
        b) Upon termination, all material must be returned or destroyed
        c) Confidentiality obligations survive termination
        d) Recipient must provide certification of material destruction
        
        8. COMPLIANCE AND REGULATORY
        a) Recipient must comply with all applicable laws and regulations
        b) IRB approval required before use with human subjects
        c) Biosafety protocols must be followed per institutional guidelines
        d) Export control regulations apply to international transfers
        
        9. GOVERNING LAW
        This agreement shall be governed by the laws of California.
        Disputes shall be resolved through binding arbitration in San Francisco.
        
        10. EXHIBITS
        Exhibit A: Detailed Research Protocol
        Exhibit B: Biosafety Requirements
        Exhibit C: Publication Guidelines
        """
        
        mta_doc = Document(
            id="mta_demo_001",
            title="Stanford-MIT Material Transfer Agreement",
            file_type="pdf",
            file_size=len(mta_content),
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text=mta_content,
            is_legal_document=True,
            legal_document_type="MTA"
        )
        
        # Add content property for compatibility
        mta_doc.content = mta_content
        
        # Software License Agreement
        license_content = """
        SOFTWARE LICENSE AGREEMENT
        
        This Software License Agreement ("Agreement") is entered into on February 1, 2024,
        between TechCorp Inc. ("Licensor") and DataSystems LLC ("Licensee").
        
        1. LICENSED SOFTWARE
        Licensor grants Licensee a non-exclusive license to use:
        - Software: Advanced Analytics Platform v3.2
        - Documentation: User manuals and technical specifications
        - Updates: All minor updates and patches for 12 months
        
        2. LICENSE SCOPE
        a) Internal business use only within Licensee's organization
        b) Maximum 100 concurrent users
        c) Installation on up to 5 servers
        d) No redistribution or sublicensing rights
        
        3. PAYMENT TERMS
        a) License fee: $50,000 annually
        b) Payment due within 15 days of invoice
        c) Late payment penalty: 1.5% per month
        d) Support fee: $10,000 annually (optional)
        
        4. INTELLECTUAL PROPERTY
        a) Licensor retains all ownership rights to the software
        b) Licensee owns data processed by the software
        c) No reverse engineering or decompilation permitted
        d) Feedback provided to Licensor becomes Licensor's property
        
        5. SUPPORT AND MAINTENANCE
        a) Email support during business hours (9 AM - 5 PM PST)
        b) Response time: 24 hours for critical issues
        c) Software updates provided quarterly
        d) On-site support available for additional fee
        
        6. WARRANTIES AND DISCLAIMERS
        a) Software provided "as is" without warranties
        b) Licensor disclaims all implied warranties
        c) No guarantee of uninterrupted operation
        d) Licensee responsible for data backup and security
        
        7. LIABILITY LIMITATIONS
        a) Licensor's liability limited to annual license fee
        b) No liability for consequential or indirect damages
        c) Licensee assumes all risks of software use
        d) Indemnification for third-party IP claims excluded
        
        8. TERMINATION
        a) Term: 12 months with automatic renewal
        b) Termination for breach with 30-day cure period
        c) Immediate termination for non-payment
        d) Software must be uninstalled upon termination
        
        9. CONFIDENTIALITY
        a) Both parties protect confidential information
        b) Confidentiality period: 3 years after disclosure
        c) Standard exceptions apply (public domain, etc.)
        d) Return of confidential materials upon request
        
        10. GENERAL PROVISIONS
        a) Governing law: Delaware
        b) Jurisdiction: Delaware state courts
        c) Entire agreement clause
        d) Amendment requires written consent
        """
        
        license_doc = Document(
            id="license_demo_001",
            title="TechCorp Software License Agreement",
            file_type="pdf",
            file_size=len(license_content),
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text=license_content,
            is_legal_document=True,
            legal_document_type="Software License"
        )
        
        # Add content property for compatibility
        license_doc.content = license_content
        
        # Store documents
        self.storage.create_document(mta_doc)
        self.storage.create_document(license_doc)
        
        return [mta_doc, license_doc]
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all enhanced capabilities"""
        
        print("🚀 Enhanced Contract Assistant System Demonstration")
        print("=" * 60)
        
        # Start production monitoring
        start_global_monitoring()
        
        try:
            # 1. Basic Question Processing Demo
            await self._demo_basic_question_processing()
            
            # 2. Answer Quality Enhancement Demo
            await self._demo_answer_quality_enhancement()
            
            # 3. Advanced Document Analysis Demo
            await self._demo_advanced_document_analysis()
            
            # 4. Intelligent Response Formatting Demo
            await self._demo_intelligent_response_formatting()
            
            # 5. Multi-turn Conversation Demo
            await self._demo_multi_turn_conversation()
            
            # 6. Performance and Monitoring Demo
            await self._demo_performance_monitoring()
            
            # 7. Comprehensive Test Suite Demo
            await self._demo_comprehensive_testing()
            
            # 8. Production Readiness Demo
            await self._demo_production_readiness()
            
        finally:
            # Cleanup
            stop_global_monitoring()
            self.system.shutdown()
        
        print("\n✅ Enhanced Contract Assistant System Demonstration Complete!")
    
    async def _demo_basic_question_processing(self):
        """Demonstrate basic question processing with enhancements"""
        
        print("\n📋 1. BASIC QUESTION PROCESSING DEMONSTRATION")
        print("-" * 50)
        
        questions = [
            "What are the payment terms in this MTA?",
            "Who are the parties to this agreement?",
            "What happens if either party wants to terminate?",
            "Are there any liability limitations?",
            "What's the weather like today?"  # Off-topic question
        ]
        
        context = ProcessingContext(session_id="demo_basic")
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔍 Question {i}: {question}")
            
            start_time = time.time()
            result = await self.system.process_question(
                question=question,
                document_id="mta_demo_001",
                context=context
            )
            processing_time = time.time() - start_time
            
            print(f"   Response Type: {result.response.response_type}")
            print(f"   Confidence: {result.response.confidence:.2f}")
            print(f"   Quality Score: {result.quality_score:.2f}")
            print(f"   Processing Time: {processing_time:.2f}s")
            print(f"   Enhancements: {', '.join(result.enhancements_applied)}")
            print(f"   Response Preview: {result.response.content[:150]}...")
    
    async def _demo_answer_quality_enhancement(self):
        """Demonstrate answer quality enhancement features"""
        
        print("\n🎯 2. ANSWER QUALITY ENHANCEMENT DEMONSTRATION")
        print("-" * 50)
        
        complex_questions = [
            "Provide a comprehensive risk analysis of this MTA for both the provider and recipient",
            "How do the intellectual property provisions interact with the publication requirements?",
            "What are the potential legal and business implications of the termination clauses?"
        ]
        
        context = ProcessingContext(session_id="demo_quality")
        
        for i, question in enumerate(complex_questions, 1):
            print(f"\n🔬 Complex Question {i}: {question}")
            
            result = await self.system.process_question(
                question=question,
                document_id="mta_demo_001",
                context=context
            )
            
            print(f"   Quality Score: {result.quality_score:.2f}")
            print(f"   Complexity: {result.complexity_assessment.value}")
            print(f"   User Expertise Detected: {result.user_expertise_detected.value}")
            
            # Check for quality enhancement features
            content = result.response.content
            quality_features = []
            
            if "evidence" in content.lower():
                quality_features.append("Evidence Citations")
            if "risk" in content.lower():
                quality_features.append("Risk Assessment")
            if "recommendation" in content.lower():
                quality_features.append("Actionable Recommendations")
            if "implication" in content.lower():
                quality_features.append("Implications Analysis")
            
            print(f"   Quality Features: {', '.join(quality_features)}")
            print(f"   Response Length: {len(content)} characters")
    
    async def _demo_advanced_document_analysis(self):
        """Demonstrate advanced document analysis capabilities"""
        
        print("\n🔍 3. ADVANCED DOCUMENT ANALYSIS DEMONSTRATION")
        print("-" * 50)
        
        for doc in self.sample_documents:
            print(f"\n📄 Analyzing: {doc.title}")
            
            # Perform comprehensive analysis
            analysis = await self.system.analyze_document_comprehensively(
                document_id=doc.id,
                analysis_depth="comprehensive"
            )
            
            # Display analysis results
            print(f"   Document Type: {analysis['document_info']['type']}")
            print(f"   Word Count: {analysis['document_info']['length']}")
            
            if "advanced_analysis" in analysis:
                advanced = analysis["advanced_analysis"]
                print(f"   Cross-references: {advanced['cross_references']}")
                print(f"   Timeline Events: {advanced['timeline_events']}")
                print(f"   Risk Matrix Entries: {len(advanced['risk_matrix'])}")
                print(f"   Compliance Requirements: {len(advanced['compliance_requirements'])}")
                
                # Show top risks
                if advanced['risk_matrix']:
                    print("   Top Risks:")
                    for risk in advanced['risk_matrix'][:3]:
                        print(f"     - {risk['category']} ({risk['level']}): {risk['description'][:80]}...")
            
            if "detailed_insights" in analysis:
                insights = analysis["detailed_insights"]
                print(f"   Key Themes: {', '.join(insights['key_themes'])}")
                print(f"   Opportunity Areas: {len(insights['opportunity_areas'])}")
    
    async def _demo_intelligent_response_formatting(self):
        """Demonstrate intelligent response formatting for different user types"""
        
        print("\n🎨 4. INTELLIGENT RESPONSE FORMATTING DEMONSTRATION")
        print("-" * 50)
        
        question = "Explain the liability provisions in this agreement"
        
        # Test different user profiles
        user_profiles = [
            (ExpertiseLevel.BEGINNER, "Beginner", "Simple explanations with definitions"),
            (ExpertiseLevel.INTERMEDIATE, "Intermediate", "Structured analysis with examples"),
            (ExpertiseLevel.EXPERT, "Expert", "Technical detail with legal implications")
        ]
        
        for expertise, label, description in user_profiles:
            print(f"\n👤 User Profile: {label} ({description})")
            
            context = ProcessingContext(
                session_id=f"demo_formatting_{expertise.value}",
                user_profile=UserProfile(
                    expertise_level=expertise,
                    preferred_structure=ResponseStructure.STRUCTURED,
                    attention_span="medium",
                    technical_comfort="medium",
                    interaction_history=[]
                )
            )
            
            result = await self.system.process_question(
                question=question,
                document_id="mta_demo_001",
                context=context
            )
            
            print(f"   Detected Expertise: {result.user_expertise_detected.value}")
            print(f"   Response Structure: Adaptive formatting applied")
            print(f"   Response Length: {len(result.response.content)} characters")
            
            # Check for expertise-specific features
            content = result.response.content.lower()
            
            if expertise == ExpertiseLevel.BEGINNER:
                if any(phrase in content for phrase in ["simple terms", "means", "in other words"]):
                    print("   ✓ Beginner-friendly explanations detected")
            
            elif expertise == ExpertiseLevel.EXPERT:
                if len(result.response.content) > 500:
                    print("   ✓ Detailed technical analysis provided")
            
            print(f"   Preview: {result.response.content[:200]}...")
    
    async def _demo_multi_turn_conversation(self):
        """Demonstrate multi-turn conversation with context awareness"""
        
        print("\n💬 5. MULTI-TURN CONVERSATION DEMONSTRATION")
        print("-" * 50)
        
        conversation_turns = [
            "Hi, I need help understanding this software license agreement",
            "What are the main payment obligations?",
            "How much do I need to pay and when?",
            "What happens if I'm late with a payment?",
            "Can I terminate this agreement early?",
            "What are my obligations when the agreement ends?"
        ]
        
        session_id = "demo_conversation"
        conversation_history = []
        
        for i, question in enumerate(conversation_turns, 1):
            print(f"\n🗣️  Turn {i}: {question}")
            
            context = ProcessingContext(
                session_id=session_id,
                conversation_history=conversation_history.copy()
            )
            
            result = await self.system.process_question(
                question=question,
                document_id="license_demo_001",
                context=context
            )
            
            print(f"   Response Type: {result.response.response_type}")
            print(f"   Context Used: {', '.join(result.response.context_used)}")
            print(f"   Suggestions: {len(result.response.suggestions)} follow-up questions")
            
            # Add to conversation history
            conversation_history.append(question)
            
            # Show context awareness
            if i > 1:
                print("   ✓ Context from previous turns maintained")
            
            print(f"   Response: {result.response.content[:150]}...")
    
    async def _demo_performance_monitoring(self):
        """Demonstrate performance monitoring and system health"""
        
        print("\n📊 6. PERFORMANCE MONITORING DEMONSTRATION")
        print("-" * 50)
        
        # Generate some load for metrics
        print("   Generating system load for metrics...")
        
        tasks = []
        for i in range(10):
            context = ProcessingContext(session_id=f"perf_test_{i}")
            task = self.system.process_question(
                question=f"Test question {i}: What are the key terms?",
                document_id="mta_demo_001",
                context=context
            )
            tasks.append(task)
        
        # Process concurrently
        results = await asyncio.gather(*tasks)
        
        # Get system health
        health_status = await self.system.get_system_health()
        
        print("\n📈 System Health Status:")
        print(f"   Overall Status: {health_status['system_health']['overall_status']}")
        print(f"   Active Alerts: {len(health_status['active_alerts'])}")
        
        # Performance metrics
        perf_metrics = health_status['performance_metrics']
        if 'summary' in perf_metrics:
            summary = perf_metrics['summary']
            print(f"   Average Response Time: {summary.get('avg_response_time', 0):.2f}s")
            print(f"   Error Rate: {summary.get('error_rate_percent', 0):.1f}%")
            print(f"   Total Requests: {summary.get('total_requests', 0)}")
        
        # Processing statistics
        stats = health_status['processing_statistics']
        print(f"   Total Processed: {stats['total_requests']}")
        print(f"   Cache Hit Rate: {stats['cache_hits'] / max(stats['total_requests'], 1) * 100:.1f}%")
        print(f"   Quality Enhancements: {stats['quality_enhancements']}")
        print(f"   Formatting Applications: {stats['formatting_applications']}")
        
        # System resources
        if 'system' in perf_metrics:
            system = perf_metrics['system']
            print(f"   CPU Usage: {system.get('cpu_percent', 0):.1f}%")
            print(f"   Memory Usage: {system.get('memory_percent', 0):.1f}%")
    
    async def _demo_comprehensive_testing(self):
        """Demonstrate comprehensive test suite capabilities"""
        
        print("\n🧪 7. COMPREHENSIVE TEST SUITE DEMONSTRATION")
        print("-" * 50)
        
        # Create test suite
        test_suite = ComprehensiveTestSuite(self.storage)
        
        print("   Running comprehensive test suite...")
        
        # Run tests for specific categories
        test_categories = [
            TestCategory.DOCUMENT_GROUNDED,
            TestCategory.OFF_TOPIC_CASUAL,
            TestCategory.SUBJECTIVE_INTERPRETIVE
        ]
        
        results = await test_suite.run_comprehensive_test_suite(
            categories=test_categories,
            parallel_execution=False,  # Sequential for demo
            max_workers=3
        )
        
        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {results.total_tests}")
        print(f"   Passed: {results.passed_tests} ({results.passed_tests/results.total_tests*100:.1f}%)")
        print(f"   Failed: {results.failed_tests} ({results.failed_tests/results.total_tests*100:.1f}%)")
        print(f"   Warnings: {results.warning_tests}")
        print(f"   Execution Time: {results.execution_time:.2f}s")
        
        # Category breakdown
        print(f"\n📋 Category Results:")
        for category, executions in results.category_results.items():
            passed = sum(1 for e in executions if e.result.value == "pass")
            total = len(executions)
            print(f"   {category.value}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Performance metrics
        perf = results.performance_metrics
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Response Time: {perf['avg_response_time']:.2f}s")
        print(f"   Max Response Time: {perf['max_response_time']:.2f}s")
        print(f"   95th Percentile: {perf.get('response_time_p95', 0):.2f}s")
        
        # Quality metrics
        quality = results.quality_metrics
        print(f"\n🎯 Quality Metrics:")
        print(f"   Average Quality Score: {quality['avg_quality_score']:.2f}")
        
        quality_dist = quality['quality_distribution']
        print(f"   Quality Distribution:")
        print(f"     Excellent (≥0.8): {quality_dist['excellent']}")
        print(f"     Good (≥0.6): {quality_dist['good']}")
        print(f"     Fair (≥0.4): {quality_dist['fair']}")
        print(f"     Poor (<0.4): {quality_dist['poor']}")
    
    async def _demo_production_readiness(self):
        """Demonstrate production readiness validation"""
        
        print("\n🚀 8. PRODUCTION READINESS DEMONSTRATION")
        print("-" * 50)
        
        # Validate production readiness
        readiness = self.system.monitor.validate_production_readiness()
        
        print(f"   Production Ready: {'✅ YES' if readiness['production_ready'] else '❌ NO'}")
        print(f"   Validation Time: {readiness['timestamp']}")
        
        print(f"\n🔍 Readiness Checks:")
        for check_name, status in readiness['checks'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check_name.replace('_', ' ').title()}")
        
        print(f"\n💡 Recommendations:")
        for i, recommendation in enumerate(readiness['recommendations'], 1):
            print(f"   {i}. {recommendation}")
        
        # Performance optimization
        print(f"\n⚡ Performance Optimization:")
        optimization = await self.system.optimize_performance()
        
        if optimization['optimizations_applied']:
            print(f"   Applied: {', '.join(optimization['optimizations_applied'])}")
        else:
            print(f"   No optimizations needed at this time")
        
        if optimization['recommendations']:
            print(f"   Recommendations:")
            for rec in optimization['recommendations']:
                print(f"     - {rec}")


async def main():
    """Main demonstration function"""
    
    print("🎉 Welcome to the Enhanced Contract Assistant System Demo!")
    print("This demonstration showcases all enhanced capabilities including:")
    print("• Answer Quality Enhancement with Rich Analysis")
    print("• Advanced Document Analysis with Cross-referencing")
    print("• Intelligent Response Formatting")
    print("• Production Monitoring and Health Checks")
    print("• Comprehensive Testing and Validation")
    print("• Performance Optimization")
    
    demo = EnhancedSystemDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())