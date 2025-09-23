"""
Comprehensive Test Suite for Enhanced Contract Assistant

This module provides comprehensive testing for all question categories,
quality validation, performance monitoring, and end-to-end workflow testing.
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import json
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.models.enhanced import EnhancedResponse, QuestionIntent, ResponseType
from src.models.document import Document
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.answer_quality_enhancer import AnswerQualityEnhancer, QuestionComplexity, ExpertiseLevel
from src.services.advanced_document_analyzer import AdvancedDocumentAnalyzer
from src.services.intelligent_response_formatter import IntelligentResponseFormatter
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class TestCategory(Enum):
    """Test categories for comprehensive coverage"""
    DOCUMENT_GROUNDED = "document_grounded"
    MULTI_SECTION = "multi_section"
    SUBJECTIVE_INTERPRETIVE = "subjective_interpretive"
    SCENARIO_BASED = "scenario_based"
    COMPOUND_QUESTIONS = "compound_questions"
    OFF_TOPIC_CASUAL = "off_topic_casual"
    EDGE_CASES = "edge_cases"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"


class TestResult(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class TestCase:
    """Individual test case"""
    test_id: str
    category: TestCategory
    question: str
    expected_response_type: ResponseType
    expected_confidence_min: float
    document_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    validation_criteria: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    description: str = ""


@dataclass
class TestExecution:
    """Test execution result"""
    test_case: TestCase
    result: TestResult
    response: Optional[EnhancedResponse] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, bool] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestSuiteResults:
    """Complete test suite results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    skipped_tests: int
    execution_time: float
    category_results: Dict[TestCategory, List[TestExecution]]
    performance_metrics: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    coverage_report: Dict[str, Any]


class ComprehensiveTestSuite:
    """
    Comprehensive test suite that provides:
    - Complete question type coverage testing
    - Answer quality validation and metrics
    - Performance and scalability testing
    - End-to-end workflow validation
    - Integration testing across all components
    - Real-world usage scenario simulation
    """
    
    def __init__(self, storage: Optional[DocumentStorage] = None):
        """Initialize the comprehensive test suite"""
        self.storage = storage or DocumentStorage()
        self.router = EnhancedResponseRouter(self.storage)
        self.quality_enhancer = AnswerQualityEnhancer()
        self.document_analyzer = AdvancedDocumentAnalyzer()
        self.response_formatter = IntelligentResponseFormatter()
        
        self.test_cases = self._initialize_test_cases()
        self.quality_validators = self._initialize_quality_validators()
        self.performance_benchmarks = self._initialize_performance_benchmarks()
        
    async def run_comprehensive_test_suite(
        self,
        categories: Optional[List[TestCategory]] = None,
        parallel_execution: bool = True,
        max_workers: int = 5
    ) -> TestSuiteResults:
        """
        Run the comprehensive test suite
        
        Args:
            categories: Specific categories to test (None for all)
            parallel_execution: Whether to run tests in parallel
            max_workers: Maximum number of parallel workers
            
        Returns:
            Complete test suite results
        """
        start_time = time.time()
        logger.info("Starting comprehensive test suite execution")
        
        # Filter test cases by category if specified
        test_cases_to_run = self._filter_test_cases(categories)
        
        # Execute tests
        if parallel_execution:
            executions = await self._run_tests_parallel(test_cases_to_run, max_workers)
        else:
            executions = await self._run_tests_sequential(test_cases_to_run)
        
        # Analyze results
        results = self._analyze_test_results(executions, time.time() - start_time)
        
        # Generate reports
        await self._generate_test_reports(results)
        
        logger.info(f"Test suite completed: {results.passed_tests}/{results.total_tests} passed")
        return results
    
    async def validate_question_type_coverage(self) -> Dict[TestCategory, float]:
        """Validate coverage across all question types"""
        coverage_results = {}
        
        for category in TestCategory:
            category_tests = [tc for tc in self.test_cases if tc.category == category]
            if not category_tests:
                coverage_results[category] = 0.0
                continue
            
            # Run category tests
            executions = await self._run_tests_sequential(category_tests)
            
            # Calculate success rate
            passed = sum(1 for e in executions if e.result == TestResult.PASS)
            coverage_results[category] = passed / len(executions) if executions else 0.0
        
        return coverage_results
    
    async def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks and scalability tests"""
        benchmarks = {}
        
        # Response time benchmarks
        benchmarks['response_times'] = await self._benchmark_response_times()
        
        # Concurrent user simulation
        benchmarks['concurrent_users'] = await self._benchmark_concurrent_users()
        
        # Memory usage monitoring
        benchmarks['memory_usage'] = await self._benchmark_memory_usage()
        
        # Throughput testing
        benchmarks['throughput'] = await self._benchmark_throughput()
        
        return benchmarks
    
    async def validate_answer_quality(self, sample_size: int = 50) -> Dict[str, Any]:
        """Validate answer quality across different question types"""
        quality_metrics = {
            'overall_quality': 0.0,
            'category_quality': {},
            'quality_dimensions': {
                'accuracy': 0.0,
                'completeness': 0.0,
                'clarity': 0.0,
                'relevance': 0.0,
                'helpfulness': 0.0
            },
            'improvement_areas': []
        }
        
        # Sample test cases from each category
        sampled_tests = self._sample_test_cases(sample_size)
        
        # Execute and evaluate quality
        for test_case in sampled_tests:
            execution = await self._execute_single_test(test_case)
            if execution.response:
                quality_score = await self._evaluate_response_quality(
                    execution.response, test_case
                )
                
                # Update metrics
                category = test_case.category
                if category not in quality_metrics['category_quality']:
                    quality_metrics['category_quality'][category] = []
                
                quality_metrics['category_quality'][category].append(quality_score)
        
        # Calculate overall metrics
        all_scores = []
        for category_scores in quality_metrics['category_quality'].values():
            all_scores.extend(category_scores)
        
        if all_scores:
            quality_metrics['overall_quality'] = statistics.mean(all_scores)
        
        return quality_metrics
    
    async def run_end_to_end_workflow_tests(self) -> Dict[str, Any]:
        """Run end-to-end workflow tests simulating real user journeys"""
        workflow_results = {
            'document_upload_to_analysis': await self._test_document_upload_workflow(),
            'multi_turn_conversation': await self._test_multi_turn_conversation(),
            'complex_analysis_workflow': await self._test_complex_analysis_workflow(),
            'error_recovery_workflow': await self._test_error_recovery_workflow(),
            'user_journey_simulation': await self._test_user_journey_simulation()
        }
        
        return workflow_results
    
    def _initialize_test_cases(self) -> List[TestCase]:
        """Initialize comprehensive test cases covering all scenarios"""
        test_cases = []
        
        # Document-grounded questions (straight lookup)
        test_cases.extend([
            TestCase(
                test_id="DOC_001",
                category=TestCategory.DOCUMENT_GROUNDED,
                question="What are the payment terms in this agreement?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.8,
                validation_criteria=["contains_payment_info", "cites_document_section"],
                description="Direct lookup of payment terms"
            ),
            TestCase(
                test_id="DOC_002",
                category=TestCategory.DOCUMENT_GROUNDED,
                question="What is the termination notice period?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.8,
                validation_criteria=["contains_termination_info", "specifies_notice_period"],
                description="Direct lookup of termination clause"
            ),
            TestCase(
                test_id="DOC_003",
                category=TestCategory.DOCUMENT_GROUNDED,
                question="Who are the parties to this agreement?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.9,
                validation_criteria=["identifies_parties", "cites_document_section"],
                description="Direct lookup of contracting parties"
            )
        ])
        
        # Multi-section cross-exhibit analysis
        test_cases.extend([
            TestCase(
                test_id="MULTI_001",
                category=TestCategory.MULTI_SECTION,
                question="How do the liability provisions in Section 5 relate to the indemnification terms in Section 8?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.7,
                validation_criteria=["cross_references_sections", "explains_relationship"],
                description="Cross-section analysis of related provisions"
            ),
            TestCase(
                test_id="MULTI_002",
                category=TestCategory.MULTI_SECTION,
                question="What is the relationship between the confidentiality obligations and the publication restrictions?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.7,
                validation_criteria=["identifies_multiple_sections", "explains_interaction"],
                description="Analysis of interrelated obligations"
            )
        ])
        
        # Subjective interpretive questions
        test_cases.extend([
            TestCase(
                test_id="SUBJ_001",
                category=TestCategory.SUBJECTIVE_INTERPRETIVE,
                question="Is this agreement favorable to the recipient?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.6,
                validation_criteria=["provides_balanced_analysis", "identifies_pros_cons"],
                description="Subjective assessment of agreement favorability"
            ),
            TestCase(
                test_id="SUBJ_002",
                category=TestCategory.SUBJECTIVE_INTERPRETIVE,
                question="What are the main risks for the provider in this agreement?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.7,
                validation_criteria=["identifies_risks", "explains_implications"],
                description="Risk assessment from provider perspective"
            )
        ])
        
        # Scenario-based "what if" questions
        test_cases.extend([
            TestCase(
                test_id="SCEN_001",
                category=TestCategory.SCENARIO_BASED,
                question="What happens if the recipient wants to use the materials for commercial purposes?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.7,
                validation_criteria=["addresses_scenario", "cites_relevant_clauses"],
                description="Commercial use scenario analysis"
            ),
            TestCase(
                test_id="SCEN_002",
                category=TestCategory.SCENARIO_BASED,
                question="What if the provider breaches the delivery timeline?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.7,
                validation_criteria=["addresses_breach_scenario", "identifies_remedies"],
                description="Breach scenario analysis"
            )
        ])
        
        # Compound questions
        test_cases.extend([
            TestCase(
                test_id="COMP_001",
                category=TestCategory.COMPOUND_QUESTIONS,
                question="What are the payment terms, and how do they relate to the delivery schedule, and what happens if payments are late?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.6,
                validation_criteria=["addresses_all_parts", "maintains_coherence"],
                description="Multi-part compound question"
            ),
            TestCase(
                test_id="COMP_002",
                category=TestCategory.COMPOUND_QUESTIONS,
                question="Who owns the intellectual property, what are the licensing terms, and can the recipient sublicense?",
                expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                expected_confidence_min=0.6,
                validation_criteria=["addresses_ip_ownership", "covers_licensing", "addresses_sublicensing"],
                description="IP-focused compound question"
            )
        ])
        
        # Off-topic casual playful questions
        test_cases.extend([
            TestCase(
                test_id="OFF_001",
                category=TestCategory.OFF_TOPIC_CASUAL,
                question="What's the weather like today?",
                expected_response_type=ResponseType.FALLBACK,
                expected_confidence_min=0.8,
                validation_criteria=["graceful_redirect", "maintains_professionalism"],
                description="Weather question - off-topic"
            ),
            TestCase(
                test_id="OFF_002",
                category=TestCategory.OFF_TOPIC_CASUAL,
                question="Can you write this contract in the style of Shakespeare?",
                expected_response_type=ResponseType.CASUAL,
                expected_confidence_min=0.8,
                validation_criteria=["acknowledges_playfulness", "redirects_appropriately"],
                description="Playful style request"
            ),
            TestCase(
                test_id="OFF_003",
                category=TestCategory.OFF_TOPIC_CASUAL,
                question="Tell me a joke about lawyers",
                expected_response_type=ResponseType.CASUAL,
                expected_confidence_min=0.8,
                validation_criteria=["handles_humor_appropriately", "maintains_professionalism"],
                description="Humor request"
            )
        ])
        
        # Edge cases
        test_cases.extend([
            TestCase(
                test_id="EDGE_001",
                category=TestCategory.EDGE_CASES,
                question="",
                expected_response_type=ResponseType.FALLBACK,
                expected_confidence_min=0.5,
                validation_criteria=["handles_empty_question"],
                description="Empty question"
            ),
            TestCase(
                test_id="EDGE_002",
                category=TestCategory.EDGE_CASES,
                question="a" * 1000,  # Very long question
                expected_response_type=ResponseType.FALLBACK,
                expected_confidence_min=0.5,
                validation_criteria=["handles_long_question"],
                description="Extremely long question"
            ),
            TestCase(
                test_id="EDGE_003",
                category=TestCategory.EDGE_CASES,
                question="What about the thing in the place with the stuff?",
                expected_response_type=ResponseType.FALLBACK,
                expected_confidence_min=0.5,
                validation_criteria=["handles_vague_question"],
                description="Vague/ambiguous question"
            )
        ])
        
        return test_cases
    
    def _initialize_quality_validators(self) -> Dict[str, Callable]:
        """Initialize quality validation functions"""
        return {
            'contains_payment_info': lambda response: 'payment' in response.content.lower(),
            'cites_document_section': lambda response: any(
                phrase in response.content.lower() 
                for phrase in ['section', 'clause', 'paragraph', 'article']
            ),
            'contains_termination_info': lambda response: 'termination' in response.content.lower(),
            'specifies_notice_period': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['days', 'notice', 'period', 'advance']
            ),
            'identifies_parties': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['party', 'parties', 'provider', 'recipient']
            ),
            'cross_references_sections': lambda response: response.content.lower().count('section') >= 2,
            'explains_relationship': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['relate', 'connection', 'interaction', 'together']
            ),
            'identifies_multiple_sections': lambda response: response.content.lower().count('section') >= 2,
            'explains_interaction': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['interact', 'work together', 'combined', 'relationship']
            ),
            'provides_balanced_analysis': lambda response: (
                'advantage' in response.content.lower() or 'benefit' in response.content.lower()
            ) and (
                'disadvantage' in response.content.lower() or 'risk' in response.content.lower()
            ),
            'identifies_pros_cons': lambda response: (
                'pro' in response.content.lower() or 'benefit' in response.content.lower()
            ) and (
                'con' in response.content.lower() or 'drawback' in response.content.lower()
            ),
            'identifies_risks': lambda response: 'risk' in response.content.lower(),
            'explains_implications': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['implication', 'means', 'result', 'consequence']
            ),
            'addresses_scenario': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['if', 'scenario', 'case', 'situation']
            ),
            'cites_relevant_clauses': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['clause', 'section', 'provision', 'term']
            ),
            'addresses_breach_scenario': lambda response: 'breach' in response.content.lower(),
            'identifies_remedies': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['remedy', 'solution', 'recourse', 'action']
            ),
            'addresses_all_parts': lambda response: len(response.content.split('.')) >= 3,
            'maintains_coherence': lambda response: len(response.content) > 100,
            'addresses_ip_ownership': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['ownership', 'owns', 'intellectual property', 'ip']
            ),
            'covers_licensing': lambda response: 'licens' in response.content.lower(),
            'addresses_sublicensing': lambda response: 'sublicens' in response.content.lower(),
            'graceful_redirect': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['help', 'contract', 'document', 'agreement']
            ),
            'maintains_professionalism': lambda response: not any(
                phrase in response.content.lower()
                for phrase in ['stupid', 'dumb', 'ridiculous']
            ),
            'acknowledges_playfulness': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['understand', 'appreciate', 'interesting']
            ),
            'redirects_appropriately': lambda response: 'contract' in response.content.lower(),
            'handles_humor_appropriately': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['appreciate', 'understand', 'focus']
            ),
            'handles_empty_question': lambda response: len(response.content) > 0,
            'handles_long_question': lambda response: len(response.content) > 0,
            'handles_vague_question': lambda response: any(
                phrase in response.content.lower()
                for phrase in ['clarify', 'specific', 'more information']
            )
        }
    
    def _initialize_performance_benchmarks(self) -> Dict[str, Any]:
        """Initialize performance benchmarks and thresholds"""
        return {
            'response_time_targets': {
                'simple_questions': 2.0,  # seconds
                'moderate_questions': 5.0,
                'complex_questions': 10.0,
                'expert_questions': 15.0
            },
            'concurrent_user_targets': {
                'light_load': 10,
                'medium_load': 50,
                'heavy_load': 100
            },
            'memory_usage_limits': {
                'per_request_mb': 50,
                'total_system_mb': 1000
            },
            'throughput_targets': {
                'requests_per_minute': 60,
                'questions_per_hour': 1000
            }
        }
    
    def _filter_test_cases(self, categories: Optional[List[TestCategory]]) -> List[TestCase]:
        """Filter test cases by categories"""
        if not categories:
            return self.test_cases
        
        return [tc for tc in self.test_cases if tc.category in categories]
    
    async def _run_tests_parallel(
        self, 
        test_cases: List[TestCase], 
        max_workers: int
    ) -> List[TestExecution]:
        """Run tests in parallel"""
        executions = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test cases
            future_to_test = {
                executor.submit(self._execute_single_test_sync, test_case): test_case
                for test_case in test_cases
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    execution = future.result()
                    executions.append(execution)
                except Exception as e:
                    logger.error(f"Test {test_case.test_id} failed with exception: {e}")
                    executions.append(TestExecution(
                        test_case=test_case,
                        result=TestResult.FAIL,
                        error_message=str(e)
                    ))
        
        return executions
    
    async def _run_tests_sequential(self, test_cases: List[TestCase]) -> List[TestExecution]:
        """Run tests sequentially"""
        executions = []
        
        for test_case in test_cases:
            execution = await self._execute_single_test(test_case)
            executions.append(execution)
        
        return executions
    
    def _execute_single_test_sync(self, test_case: TestCase) -> TestExecution:
        """Synchronous wrapper for single test execution"""
        return asyncio.run(self._execute_single_test(test_case))
    
    async def _execute_single_test(self, test_case: TestCase) -> TestExecution:
        """Execute a single test case"""
        start_time = time.time()
        
        try:
            # Create a test document if needed
            document = None
            if test_case.document_id:
                document = await self._get_or_create_test_document(test_case.document_id)
            else:
                document = await self._create_default_test_document()
            
            # Execute the question
            response = self.router.route_question(
                question=test_case.question,
                document_id=document.id if document else "test_doc",
                session_id=f"test_session_{test_case.test_id}",
                document=document
            )
            
            execution_time = time.time() - start_time
            
            # Validate response
            validation_results = self._validate_response(response, test_case)
            
            # Determine test result
            result = self._determine_test_result(response, test_case, validation_results)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(response, test_case)
            
            return TestExecution(
                test_case=test_case,
                result=result,
                response=response,
                execution_time=execution_time,
                validation_results=validation_results,
                quality_metrics=quality_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Test {test_case.test_id} failed: {e}")
            
            return TestExecution(
                test_case=test_case,
                result=TestResult.FAIL,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _validate_response(
        self, 
        response: EnhancedResponse, 
        test_case: TestCase
    ) -> Dict[str, bool]:
        """Validate response against test case criteria"""
        validation_results = {}
        
        for criterion in test_case.validation_criteria:
            validator = self.quality_validators.get(criterion)
            if validator:
                try:
                    validation_results[criterion] = validator(response)
                except Exception as e:
                    logger.warning(f"Validation {criterion} failed: {e}")
                    validation_results[criterion] = False
            else:
                logger.warning(f"Unknown validation criterion: {criterion}")
                validation_results[criterion] = False
        
        return validation_results
    
    def _determine_test_result(
        self,
        response: EnhancedResponse,
        test_case: TestCase,
        validation_results: Dict[str, bool]
    ) -> TestResult:
        """Determine overall test result"""
        
        # Check basic requirements
        if not response:
            return TestResult.FAIL
        
        if response.response_type != test_case.expected_response_type:
            return TestResult.FAIL
        
        if response.confidence < test_case.expected_confidence_min:
            return TestResult.WARNING
        
        # Check validation criteria
        failed_validations = [k for k, v in validation_results.items() if not v]
        
        if len(failed_validations) == 0:
            return TestResult.PASS
        elif len(failed_validations) <= len(validation_results) // 2:
            return TestResult.WARNING
        else:
            return TestResult.FAIL
    
    async def _calculate_quality_metrics(
        self,
        response: EnhancedResponse,
        test_case: TestCase
    ) -> Dict[str, Any]:
        """Calculate quality metrics for response"""
        metrics = {
            'response_length': len(response.content),
            'confidence_score': response.confidence,
            'has_suggestions': len(response.suggestions) > 0,
            'has_sources': len(response.sources) > 0,
            'response_completeness': self._assess_completeness(response, test_case),
            'response_clarity': self._assess_clarity(response),
            'response_relevance': self._assess_relevance(response, test_case)
        }
        
        return metrics
    
    def _assess_completeness(self, response: EnhancedResponse, test_case: TestCase) -> float:
        """Assess response completeness"""
        # Simple heuristic based on response length and content
        base_score = min(len(response.content) / 200, 1.0)  # Normalize to 200 chars
        
        # Bonus for structured format
        if response.structured_format:
            base_score += 0.2
        
        # Bonus for suggestions
        if response.suggestions:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _assess_clarity(self, response: EnhancedResponse) -> float:
        """Assess response clarity"""
        content = response.content.lower()
        
        # Positive indicators
        clarity_score = 0.5  # Base score
        
        if any(phrase in content for phrase in ['in simple terms', 'this means', 'in other words']):
            clarity_score += 0.2
        
        if any(phrase in content for phrase in ['for example', 'such as', 'like']):
            clarity_score += 0.1
        
        # Negative indicators
        if content.count('however') > 2:
            clarity_score -= 0.1
        
        if len(content.split('.')) > 20:  # Too many sentences
            clarity_score -= 0.1
        
        return max(0.0, min(clarity_score, 1.0))
    
    def _assess_relevance(self, response: EnhancedResponse, test_case: TestCase) -> float:
        """Assess response relevance to question"""
        question_words = set(test_case.question.lower().split())
        response_words = set(response.content.lower().split())
        
        # Calculate word overlap
        overlap = len(question_words.intersection(response_words))
        relevance_score = overlap / len(question_words) if question_words else 0.0
        
        # Bonus for addressing question type
        if test_case.category == TestCategory.DOCUMENT_GROUNDED:
            if any(phrase in response.content.lower() for phrase in ['section', 'clause', 'document']):
                relevance_score += 0.2
        
        return min(relevance_score, 1.0)
    
    def _analyze_test_results(
        self, 
        executions: List[TestExecution], 
        total_time: float
    ) -> TestSuiteResults:
        """Analyze test execution results"""
        
        # Count results by status
        passed = sum(1 for e in executions if e.result == TestResult.PASS)
        failed = sum(1 for e in executions if e.result == TestResult.FAIL)
        warnings = sum(1 for e in executions if e.result == TestResult.WARNING)
        skipped = sum(1 for e in executions if e.result == TestResult.SKIP)
        
        # Group by category
        category_results = {}
        for execution in executions:
            category = execution.test_case.category
            if category not in category_results:
                category_results[category] = []
            category_results[category].append(execution)
        
        # Calculate performance metrics
        execution_times = [e.execution_time for e in executions if e.execution_time > 0]
        performance_metrics = {
            'avg_response_time': statistics.mean(execution_times) if execution_times else 0.0,
            'max_response_time': max(execution_times) if execution_times else 0.0,
            'min_response_time': min(execution_times) if execution_times else 0.0,
            'response_time_p95': statistics.quantiles(execution_times, n=20)[18] if len(execution_times) > 20 else 0.0
        }
        
        # Calculate quality metrics
        quality_scores = []
        for execution in executions:
            if execution.quality_metrics:
                completeness = execution.quality_metrics.get('response_completeness', 0.0)
                clarity = execution.quality_metrics.get('response_clarity', 0.0)
                relevance = execution.quality_metrics.get('response_relevance', 0.0)
                quality_scores.append((completeness + clarity + relevance) / 3)
        
        quality_metrics = {
            'avg_quality_score': statistics.mean(quality_scores) if quality_scores else 0.0,
            'quality_distribution': self._calculate_quality_distribution(quality_scores)
        }
        
        # Calculate coverage report
        coverage_report = {
            'category_coverage': {
                category.value: len(results) for category, results in category_results.items()
            },
            'success_rate_by_category': {
                category.value: sum(1 for e in results if e.result == TestResult.PASS) / len(results)
                for category, results in category_results.items()
            }
        }
        
        return TestSuiteResults(
            total_tests=len(executions),
            passed_tests=passed,
            failed_tests=failed,
            warning_tests=warnings,
            skipped_tests=skipped,
            execution_time=total_time,
            category_results=category_results,
            performance_metrics=performance_metrics,
            quality_metrics=quality_metrics,
            coverage_report=coverage_report
        )
    
    def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of quality scores"""
        if not quality_scores:
            return {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for score in quality_scores:
            if score >= 0.8:
                distribution['excellent'] += 1
            elif score >= 0.6:
                distribution['good'] += 1
            elif score >= 0.4:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    async def _generate_test_reports(self, results: TestSuiteResults) -> None:
        """Generate comprehensive test reports"""
        
        # Console summary
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE TEST SUITE RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {results.total_tests}")
        logger.info(f"Passed: {results.passed_tests} ({results.passed_tests/results.total_tests*100:.1f}%)")
        logger.info(f"Failed: {results.failed_tests} ({results.failed_tests/results.total_tests*100:.1f}%)")
        logger.info(f"Warnings: {results.warning_tests} ({results.warning_tests/results.total_tests*100:.1f}%)")
        logger.info(f"Execution Time: {results.execution_time:.2f} seconds")
        logger.info(f"Average Response Time: {results.performance_metrics['avg_response_time']:.2f} seconds")
        logger.info(f"Average Quality Score: {results.quality_metrics['avg_quality_score']:.2f}")
        
        # Category breakdown
        logger.info("\nCATEGORY BREAKDOWN:")
        for category, executions in results.category_results.items():
            passed = sum(1 for e in executions if e.result == TestResult.PASS)
            total = len(executions)
            logger.info(f"  {category.value}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Failed tests details
        failed_tests = []
        for executions in results.category_results.values():
            failed_tests.extend([e for e in executions if e.result == TestResult.FAIL])
        
        if failed_tests:
            logger.info(f"\nFAILED TESTS ({len(failed_tests)}):")
            for execution in failed_tests[:10]:  # Show first 10
                logger.info(f"  {execution.test_case.test_id}: {execution.error_message or 'Validation failed'}")
    
    async def _get_or_create_test_document(self, document_id: str) -> Document:
        """Get or create a test document"""
        try:
            return self.storage.get_document(document_id)
        except:
            return await self._create_test_document(document_id)
    
    async def _create_default_test_document(self) -> Document:
        """Create a default test document"""
        return await self._create_test_document("default_test_doc")
    
    async def _create_test_document(self, document_id: str) -> Document:
        """Create a test document with sample contract content"""
        sample_content = """
        MATERIAL TRANSFER AGREEMENT
        
        This Material Transfer Agreement ("Agreement") is entered into between Provider University ("Provider") 
        and Recipient Institution ("Recipient").
        
        1. MATERIAL
        The Provider agrees to transfer the following material: Cell line ABC-123 for research purposes only.
        
        2. PAYMENT TERMS
        Payment of $500 shall be made within 30 days of material delivery.
        
        3. TERMINATION
        Either party may terminate this agreement with 60 days written notice.
        
        4. LIABILITY
        Provider's liability is limited to direct damages not exceeding $10,000.
        
        5. INTELLECTUAL PROPERTY
        Recipient retains rights to improvements made independently. Provider retains rights to original material.
        
        6. CONFIDENTIALITY
        Both parties agree to maintain confidentiality of proprietary information for 5 years.
        
        7. INDEMNIFICATION
        Each party shall indemnify the other against claims arising from their negligent acts.
        
        8. GOVERNING LAW
        This agreement shall be governed by the laws of California.
        """
        
        document = Document(
            id=document_id,
            title="Test Material Transfer Agreement",
            content=sample_content,
            original_text=sample_content,
            is_legal_document=True,
            legal_document_type="MTA"
        )
        
        # Store document
        self.storage.store_document(document)
        
        return document
    
    async def _benchmark_response_times(self) -> Dict[str, float]:
        """Benchmark response times for different question complexities"""
        benchmarks = {}
        
        complexity_questions = {
            QuestionComplexity.SIMPLE: "What are the parties?",
            QuestionComplexity.MODERATE: "What are the payment terms and conditions?",
            QuestionComplexity.COMPLEX: "How do the liability and indemnification provisions interact?",
            QuestionComplexity.EXPERT: "Analyze the risk allocation framework and its implications for derivative IP ownership."
        }
        
        document = await self._create_default_test_document()
        
        for complexity, question in complexity_questions.items():
            times = []
            
            # Run multiple iterations
            for _ in range(10):
                start_time = time.time()
                
                response = self.router.route_question(
                    question=question,
                    document_id=document.id,
                    session_id="benchmark_session",
                    document=document
                )
                
                execution_time = time.time() - start_time
                times.append(execution_time)
            
            benchmarks[complexity.value] = {
                'avg_time': statistics.mean(times),
                'max_time': max(times),
                'min_time': min(times)
            }
        
        return benchmarks
    
    async def _benchmark_concurrent_users(self) -> Dict[str, Any]:
        """Benchmark concurrent user performance"""
        document = await self._create_default_test_document()
        question = "What are the payment terms?"
        
        concurrent_results = {}
        
        for user_count in [5, 10, 25, 50]:
            start_time = time.time()
            
            # Create concurrent requests
            tasks = []
            for i in range(user_count):
                task = asyncio.create_task(self._simulate_user_request(
                    question, document, f"concurrent_user_{i}"
                ))
                tasks.append(task)
            
            # Wait for all requests to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            successful_requests = sum(1 for r in results if not isinstance(r, Exception))
            
            concurrent_results[f"{user_count}_users"] = {
                'total_time': total_time,
                'successful_requests': successful_requests,
                'success_rate': successful_requests / user_count,
                'avg_time_per_request': total_time / user_count
            }
        
        return concurrent_results
    
    async def _simulate_user_request(
        self, 
        question: str, 
        document: Document, 
        session_id: str
    ) -> EnhancedResponse:
        """Simulate a single user request"""
        return self.router.route_question(
            question=question,
            document_id=document.id,
            session_id=session_id,
            document=document
        )
    
    async def _benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage patterns"""
        # This would require memory profiling tools in a real implementation
        # For now, return placeholder metrics
        return {
            'baseline_memory_mb': 100,
            'peak_memory_mb': 150,
            'memory_per_request_mb': 5,
            'memory_growth_rate': 0.1
        }
    
    async def _benchmark_throughput(self) -> Dict[str, Any]:
        """Benchmark system throughput"""
        document = await self._create_default_test_document()
        question = "What are the key terms?"
        
        # Test throughput over 1 minute
        start_time = time.time()
        end_time = start_time + 60  # 1 minute
        
        request_count = 0
        successful_requests = 0
        
        while time.time() < end_time:
            try:
                response = self.router.route_question(
                    question=question,
                    document_id=document.id,
                    session_id=f"throughput_session_{request_count}",
                    document=document
                )
                successful_requests += 1
            except Exception as e:
                logger.warning(f"Throughput test request failed: {e}")
            
            request_count += 1
        
        actual_duration = time.time() - start_time
        
        return {
            'total_requests': request_count,
            'successful_requests': successful_requests,
            'requests_per_second': request_count / actual_duration,
            'success_rate': successful_requests / request_count if request_count > 0 else 0.0
        }
    
    def _sample_test_cases(self, sample_size: int) -> List[TestCase]:
        """Sample test cases for quality validation"""
        # Ensure we sample from each category
        samples_per_category = max(1, sample_size // len(TestCategory))
        sampled_cases = []
        
        for category in TestCategory:
            category_cases = [tc for tc in self.test_cases if tc.category == category]
            sample_count = min(samples_per_category, len(category_cases))
            sampled_cases.extend(category_cases[:sample_count])
        
        return sampled_cases[:sample_size]
    
    async def _evaluate_response_quality(
        self, 
        response: EnhancedResponse, 
        test_case: TestCase
    ) -> float:
        """Evaluate overall response quality"""
        completeness = self._assess_completeness(response, test_case)
        clarity = self._assess_clarity(response)
        relevance = self._assess_relevance(response, test_case)
        
        # Weighted average
        quality_score = (completeness * 0.4 + clarity * 0.3 + relevance * 0.3)
        
        return quality_score
    
    async def _test_document_upload_workflow(self) -> Dict[str, Any]:
        """Test complete document upload to analysis workflow"""
        try:
            # Simulate document upload
            document = await self._create_test_document("workflow_test_doc")
            
            # Test document analysis
            analysis_result = self.document_analyzer.perform_advanced_analysis(document)
            
            # Test question processing
            response = self.router.route_question(
                question="What are the key risks in this agreement?",
                document_id=document.id,
                session_id="workflow_test_session",
                document=document
            )
            
            return {
                'status': 'success',
                'document_processed': True,
                'analysis_completed': len(analysis_result.risk_matrix) > 0,
                'question_answered': response is not None,
                'response_quality': await self._evaluate_response_quality(response, TestCase(
                    test_id="workflow_test",
                    category=TestCategory.INTEGRATION,
                    question="What are the key risks in this agreement?",
                    expected_response_type=ResponseType.DOCUMENT_ANALYSIS,
                    expected_confidence_min=0.7
                ))
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_multi_turn_conversation(self) -> Dict[str, Any]:
        """Test multi-turn conversation workflow"""
        try:
            document = await self._create_default_test_document()
            session_id = "multi_turn_test_session"
            
            # Simulate conversation turns
            questions = [
                "What are the payment terms?",
                "How does that relate to the delivery schedule?",
                "What happens if payments are late?",
                "Are there any penalties mentioned?"
            ]
            
            responses = []
            for question in questions:
                response = self.router.route_question(
                    question=question,
                    document_id=document.id,
                    session_id=session_id,
                    document=document
                )
                responses.append(response)
            
            # Evaluate conversation quality
            context_maintained = all(r.context_used for r in responses[1:])
            responses_coherent = all(len(r.content) > 50 for r in responses)
            
            return {
                'status': 'success',
                'turns_completed': len(responses),
                'context_maintained': context_maintained,
                'responses_coherent': responses_coherent,
                'avg_confidence': statistics.mean([r.confidence for r in responses])
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_complex_analysis_workflow(self) -> Dict[str, Any]:
        """Test complex analysis workflow with all enhancements"""
        try:
            document = await self._create_default_test_document()
            
            # Test advanced document analysis
            advanced_analysis = self.document_analyzer.perform_advanced_analysis(document)
            
            # Test enhanced response generation
            response = self.router.route_question(
                question="Provide a comprehensive risk analysis of this agreement",
                document_id=document.id,
                session_id="complex_analysis_session",
                document=document
            )
            
            # Test quality enhancement
            enhanced_response = self.quality_enhancer.enhance_response_quality(
                response=response,
                document=document,
                question="Provide a comprehensive risk analysis of this agreement",
                user_expertise=ExpertiseLevel.ADVANCED
            )
            
            # Test intelligent formatting
            formatted_response = self.response_formatter.format_intelligent_response(
                response=enhanced_response,
                question="Provide a comprehensive risk analysis of this agreement",
                question_complexity=QuestionComplexity.COMPLEX
            )
            
            return {
                'status': 'success',
                'advanced_analysis_completed': len(advanced_analysis.risk_matrix) > 0,
                'response_generated': response is not None,
                'quality_enhanced': hasattr(enhanced_response, 'quality_metrics'),
                'formatting_applied': hasattr(formatted_response, 'formatting_metadata'),
                'final_response_length': len(formatted_response.content)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_error_recovery_workflow(self) -> Dict[str, Any]:
        """Test error recovery and graceful degradation"""
        try:
            # Test with invalid document
            response1 = self.router.route_question(
                question="What are the terms?",
                document_id="nonexistent_doc",
                session_id="error_recovery_session",
                document=None
            )
            
            # Test with empty question
            response2 = self.router.route_question(
                question="",
                document_id="test_doc",
                session_id="error_recovery_session",
                document=await self._create_default_test_document()
            )
            
            # Test with malformed question
            response3 = self.router.route_question(
                question="??!@#$%^&*()",
                document_id="test_doc",
                session_id="error_recovery_session",
                document=await self._create_default_test_document()
            )
            
            return {
                'status': 'success',
                'invalid_document_handled': response1 is not None,
                'empty_question_handled': response2 is not None,
                'malformed_question_handled': response3 is not None,
                'graceful_degradation': all(r.response_type == ResponseType.FALLBACK 
                                          for r in [response1, response2, response3])
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _test_user_journey_simulation(self) -> Dict[str, Any]:
        """Test realistic user journey simulation"""
        try:
            document = await self._create_default_test_document()
            session_id = "user_journey_session"
            
            # Simulate realistic user journey
            journey_steps = [
                ("Hello, I need help with this contract", ResponseType.CASUAL),
                ("What are the main terms I should know about?", ResponseType.DOCUMENT_ANALYSIS),
                ("Are there any risks I should be concerned about?", ResponseType.DOCUMENT_ANALYSIS),
                ("What about the payment terms specifically?", ResponseType.DOCUMENT_ANALYSIS),
                ("This is confusing, can you explain it more simply?", ResponseType.DOCUMENT_ANALYSIS),
                ("Thanks, that's helpful!", ResponseType.CASUAL)
            ]
            
            journey_results = []
            for question, expected_type in journey_steps:
                response = self.router.route_question(
                    question=question,
                    document_id=document.id,
                    session_id=session_id,
                    document=document
                )
                
                journey_results.append({
                    'question': question,
                    'expected_type': expected_type,
                    'actual_type': response.response_type,
                    'confidence': response.confidence,
                    'response_length': len(response.content)
                })
            
            # Evaluate journey success
            type_matches = sum(1 for r in journey_results 
                             if r['actual_type'] == r['expected_type'])
            avg_confidence = statistics.mean([r['confidence'] for r in journey_results])
            
            return {
                'status': 'success',
                'journey_steps_completed': len(journey_results),
                'response_type_accuracy': type_matches / len(journey_results),
                'average_confidence': avg_confidence,
                'journey_coherence': avg_confidence > 0.6
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }