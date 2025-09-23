"""
Enhanced Contract Assistant System Integration

This module integrates all enhanced components into a comprehensive system
with quality enhancement, advanced analysis, intelligent formatting, and production monitoring.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.models.enhanced import EnhancedResponse, QuestionIntent, ResponseType, ToneType
from src.models.document import Document
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.answer_quality_enhancer import (
    AnswerQualityEnhancer, QuestionComplexity, ExpertiseLevel
)
from src.services.advanced_document_analyzer import AdvancedDocumentAnalyzer
from src.services.intelligent_response_formatter import (
    IntelligentResponseFormatter, UserProfile
)
from src.services.production_monitor import (
    ProductionMonitor, PerformanceTimer, get_global_monitor
)
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SystemConfiguration:
    """Configuration for the enhanced contract system"""
    enable_quality_enhancement: bool = True
    enable_advanced_analysis: bool = True
    enable_intelligent_formatting: bool = True
    enable_production_monitoring: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_concurrent_requests: int = 10
    response_timeout_seconds: int = 30
    quality_enhancement_threshold: float = 0.7


@dataclass
class ProcessingContext:
    """Context for processing a user request"""
    session_id: str
    user_profile: Optional[UserProfile] = None
    document_context: Optional[Document] = None
    conversation_history: List[str] = None
    processing_preferences: Dict[str, Any] = None


@dataclass
class EnhancedProcessingResult:
    """Result of enhanced processing"""
    response: EnhancedResponse
    processing_time: float
    quality_score: float
    complexity_assessment: QuestionComplexity
    user_expertise_detected: ExpertiseLevel
    enhancements_applied: List[str]
    performance_metrics: Dict[str, Any]
    cache_hit: bool = False


class EnhancedContractSystem:
    """
    Comprehensive enhanced contract assistant system that integrates:
    - Enhanced response routing and generation
    - Answer quality enhancement with rich analysis
    - Advanced document analysis with cross-referencing
    - Intelligent response formatting with adaptive UI
    - Production monitoring and performance tracking
    - Caching and optimization for scalability
    """
    
    def __init__(self, 
                 storage: Optional[DocumentStorage] = None,
                 config: Optional[SystemConfiguration] = None,
                 monitor: Optional[ProductionMonitor] = None):
        """Initialize the enhanced contract system"""
        
        self.config = config or SystemConfiguration()
        self.storage = storage or DocumentStorage()
        self.monitor = monitor or get_global_monitor()
        
        # Initialize core components
        self.response_router = EnhancedResponseRouter(self.storage)
        
        # Initialize enhancement components
        if self.config.enable_quality_enhancement:
            self.quality_enhancer = AnswerQualityEnhancer()
        
        if self.config.enable_advanced_analysis:
            self.document_analyzer = AdvancedDocumentAnalyzer()
        
        if self.config.enable_intelligent_formatting:
            self.response_formatter = IntelligentResponseFormatter()
        
        # Initialize caching
        if self.config.enable_caching:
            self.response_cache: Dict[str, Tuple[EnhancedProcessingResult, datetime]] = {}
        
        # Thread pool for concurrent processing
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_concurrent_requests)
        
        # Processing statistics
        self.processing_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'average_processing_time': 0.0,
            'quality_enhancements': 0,
            'formatting_applications': 0
        }
        
        logger.info("Enhanced Contract System initialized")
    
    async def process_question(
        self,
        question: str,
        document_id: str,
        context: ProcessingContext
    ) -> EnhancedProcessingResult:
        """
        Process a question with full enhancement pipeline
        
        Args:
            question: User's question
            document_id: ID of the document to analyze
            context: Processing context with session and user information
            
        Returns:
            Enhanced processing result with comprehensive analysis
        """
        
        start_time = time.time()
        
        with PerformanceTimer(self.monitor, "question_processing", {"document_id": document_id}):
            try:
                # Check cache first
                if self.config.enable_caching:
                    cached_result = self._check_cache(question, document_id, context)
                    if cached_result:
                        self.processing_stats['cache_hits'] += 1
                        self.monitor.record_metric("cache_hit", 1)
                        return cached_result
                
                # Get document
                document = await self._get_document(document_id)
                if not document:
                    return self._create_error_result("Document not found", start_time)
                
                # Assess question complexity
                complexity = self._assess_question_complexity(question)
                
                # Detect user expertise
                user_expertise = self._detect_user_expertise(question, context)
                
                # Generate base response
                base_response = await self._generate_base_response(
                    question, document, context
                )
                
                # Apply enhancements
                enhanced_response, enhancements_applied = await self._apply_enhancements(
                    base_response, question, document, complexity, user_expertise, context
                )
                
                # Calculate quality score
                quality_score = await self._calculate_quality_score(
                    enhanced_response, question, document
                )
                
                # Create result
                processing_time = time.time() - start_time
                result = EnhancedProcessingResult(
                    response=enhanced_response,
                    processing_time=processing_time,
                    quality_score=quality_score,
                    complexity_assessment=complexity,
                    user_expertise_detected=user_expertise,
                    enhancements_applied=enhancements_applied,
                    performance_metrics=self._get_performance_metrics(),
                    cache_hit=False
                )
                
                # Cache result
                if self.config.enable_caching:
                    self._cache_result(question, document_id, context, result)
                
                # Update statistics
                self._update_processing_stats(result)
                
                # Record metrics
                self.monitor.record_response_time(processing_time, "question_processing")
                self.monitor.record_metric("quality_score", quality_score)
                self.monitor.record_metric("complexity_level", complexity.value)
                
                logger.info(f"Question processed successfully in {processing_time:.2f}s with quality score {quality_score:.2f}")
                
                return result
                
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"Error processing question: {e}")
                
                self.monitor.record_error("question_processing", str(e), {
                    "question": question[:100],
                    "document_id": document_id,
                    "processing_time": processing_time
                })
                
                return self._create_error_result(str(e), start_time)
    
    async def analyze_document_comprehensively(
        self,
        document_id: str,
        analysis_depth: str = "standard"  # standard, detailed, comprehensive
    ) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis
        
        Args:
            document_id: ID of document to analyze
            analysis_depth: Depth of analysis to perform
            
        Returns:
            Comprehensive analysis results
        """
        
        with PerformanceTimer(self.monitor, "document_analysis", {"document_id": document_id}):
            try:
                # Get document
                document = await self._get_document(document_id)
                if not document:
                    raise ValueError("Document not found")
                
                analysis_results = {}
                
                # Basic document information
                analysis_results['document_info'] = {
                    'id': document.id,
                    'title': document.title,
                    'type': document.legal_document_type,
                    'length': len(document.content),
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
                # Advanced document analysis
                if self.config.enable_advanced_analysis:
                    advanced_analysis = self.document_analyzer.perform_advanced_analysis(document)
                    
                    analysis_results['advanced_analysis'] = {
                        'cross_references': len(advanced_analysis.cross_references),
                        'exhibit_references': len(advanced_analysis.exhibit_references),
                        'timeline_events': len(advanced_analysis.timeline_events),
                        'party_obligations': {
                            party: len(obligations) 
                            for party, obligations in advanced_analysis.party_obligations.items()
                        },
                        'risk_matrix': [
                            {
                                'risk_id': risk.risk_id,
                                'category': risk.risk_category,
                                'level': risk.overall_risk.value,
                                'description': risk.description
                            }
                            for risk in advanced_analysis.risk_matrix
                        ],
                        'compliance_requirements': [
                            {
                                'framework': req.regulatory_framework,
                                'description': req.description,
                                'deadline': req.compliance_deadline
                            }
                            for req in advanced_analysis.compliance_requirements
                        ]
                    }
                
                # Detailed analysis for higher depths
                if analysis_depth in ["detailed", "comprehensive"]:
                    analysis_results['detailed_insights'] = await self._generate_detailed_insights(
                        document, advanced_analysis if self.config.enable_advanced_analysis else None
                    )
                
                # Comprehensive analysis includes predictive insights
                if analysis_depth == "comprehensive":
                    analysis_results['predictive_insights'] = await self._generate_predictive_insights(
                        document, analysis_results
                    )
                
                logger.info(f"Document analysis completed for {document_id} with depth {analysis_depth}")
                
                return analysis_results
                
            except Exception as e:
                logger.error(f"Error in document analysis: {e}")
                self.monitor.record_error("document_analysis", str(e), {"document_id": document_id})
                raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        health_status = self.monitor.get_health_status()
        performance_metrics = self.monitor.get_performance_metrics()
        active_alerts = self.monitor.get_active_alerts()
        
        return {
            "system_health": health_status,
            "performance_metrics": performance_metrics,
            "active_alerts": active_alerts,
            "processing_statistics": self.processing_stats,
            "configuration": {
                "quality_enhancement_enabled": self.config.enable_quality_enhancement,
                "advanced_analysis_enabled": self.config.enable_advanced_analysis,
                "intelligent_formatting_enabled": self.config.enable_intelligent_formatting,
                "caching_enabled": self.config.enable_caching,
                "monitoring_enabled": self.config.enable_production_monitoring
            },
            "cache_statistics": self._get_cache_statistics() if self.config.enable_caching else None
        }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize system performance based on current metrics"""
        
        optimization_results = {
            "optimizations_applied": [],
            "performance_improvement": {},
            "recommendations": []
        }
        
        # Cache optimization
        if self.config.enable_caching:
            cache_stats = self._get_cache_statistics()
            if cache_stats['hit_rate'] < 0.3:  # Low hit rate
                self._optimize_cache()
                optimization_results["optimizations_applied"].append("cache_optimization")
        
        # Memory optimization
        if self._should_optimize_memory():
            self._optimize_memory_usage()
            optimization_results["optimizations_applied"].append("memory_optimization")
        
        # Performance recommendations
        performance_metrics = self.monitor.get_performance_metrics()
        if performance_metrics["summary"]["avg_response_time"] > 5.0:
            optimization_results["recommendations"].append(
                "Consider increasing system resources or optimizing query processing"
            )
        
        if performance_metrics["summary"]["error_rate_percent"] > 2.0:
            optimization_results["recommendations"].append(
                "Investigate and fix sources of errors to improve reliability"
            )
        
        return optimization_results
    
    def shutdown(self) -> None:
        """Gracefully shutdown the system"""
        logger.info("Shutting down Enhanced Contract System")
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)
        
        # Clear cache
        if self.config.enable_caching:
            self.response_cache.clear()
        
        # Stop monitoring if we own it
        if self.config.enable_production_monitoring:
            self.monitor.stop_monitoring()
        
        logger.info("Enhanced Contract System shutdown complete")
    
    # Private methods
    
    async def _get_document(self, document_id: str) -> Optional[Document]:
        """Get document from storage"""
        try:
            return self.storage.get_document(document_id)
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
    
    def _assess_question_complexity(self, question: str) -> QuestionComplexity:
        """Assess the complexity of a question"""
        if not self.config.enable_quality_enhancement:
            return QuestionComplexity.MODERATE
        
        return self.quality_enhancer._assess_question_complexity(question)
    
    def _detect_user_expertise(
        self, 
        question: str, 
        context: ProcessingContext
    ) -> ExpertiseLevel:
        """Detect user expertise level"""
        if not self.config.enable_intelligent_formatting:
            return ExpertiseLevel.INTERMEDIATE
        
        return self.response_formatter._detect_expertise_level(
            question, 
            context.conversation_history
        )
    
    async def _generate_base_response(
        self,
        question: str,
        document: Document,
        context: ProcessingContext
    ) -> EnhancedResponse:
        """Generate base response using the router"""
        
        return self.response_router.route_question(
            question=question,
            document_id=document.id,
            session_id=context.session_id,
            document=document
        )
    
    async def _apply_enhancements(
        self,
        base_response: EnhancedResponse,
        question: str,
        document: Document,
        complexity: QuestionComplexity,
        user_expertise: ExpertiseLevel,
        context: ProcessingContext
    ) -> Tuple[EnhancedResponse, List[str]]:
        """Apply all configured enhancements to the response"""
        
        enhanced_response = base_response
        enhancements_applied = []
        
        # Quality enhancement
        if (self.config.enable_quality_enhancement and 
            base_response.confidence >= self.config.quality_enhancement_threshold):
            
            enhanced_response = self.quality_enhancer.enhance_response_quality(
                response=enhanced_response,
                document=document,
                question=question,
                user_expertise=user_expertise,
                question_complexity=complexity
            )
            enhancements_applied.append("quality_enhancement")
            self.processing_stats['quality_enhancements'] += 1
        
        # Intelligent formatting
        if self.config.enable_intelligent_formatting:
            user_profile = context.user_profile or UserProfile(
                expertise_level=user_expertise,
                preferred_structure=self.response_formatter._infer_preferred_structure(question),
                attention_span=self.response_formatter._assess_attention_span(question),
                technical_comfort="medium",
                interaction_history=context.conversation_history or []
            )
            
            enhanced_response = self.response_formatter.format_intelligent_response(
                response=enhanced_response,
                question=question,
                question_complexity=complexity,
                user_profile=user_profile,
                context_history=context.conversation_history
            )
            enhancements_applied.append("intelligent_formatting")
            self.processing_stats['formatting_applications'] += 1
        
        return enhanced_response, enhancements_applied
    
    async def _calculate_quality_score(
        self,
        response: EnhancedResponse,
        question: str,
        document: Document
    ) -> float:
        """Calculate overall quality score for the response"""
        
        if not self.config.enable_quality_enhancement:
            return response.confidence
        
        # Use quality enhancer's assessment methods
        completeness = self.quality_enhancer._assess_completeness(response, None)
        clarity = self.quality_enhancer._assess_clarity(response)
        relevance = self.quality_enhancer._assess_relevance(response, None)
        
        # Weighted average
        quality_score = (
            completeness * 0.4 + 
            clarity * 0.3 + 
            relevance * 0.3
        )
        
        return quality_score
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "processing_stats": self.processing_stats.copy(),
            "cache_stats": self._get_cache_statistics() if self.config.enable_caching else None,
            "system_resources": self.monitor._get_system_metrics()
        }
    
    def _check_cache(
        self,
        question: str,
        document_id: str,
        context: ProcessingContext
    ) -> Optional[EnhancedProcessingResult]:
        """Check if response is cached"""
        
        if not self.config.enable_caching:
            return None
        
        cache_key = self._generate_cache_key(question, document_id, context)
        
        if cache_key in self.response_cache:
            cached_result, timestamp = self.response_cache[cache_key]
            
            # Check if cache entry is still valid
            if (datetime.now() - timestamp).seconds < self.config.cache_ttl_seconds:
                # Mark as cache hit
                cached_result.cache_hit = True
                return cached_result
            else:
                # Remove expired entry
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_result(
        self,
        question: str,
        document_id: str,
        context: ProcessingContext,
        result: EnhancedProcessingResult
    ) -> None:
        """Cache processing result"""
        
        if not self.config.enable_caching:
            return
        
        cache_key = self._generate_cache_key(question, document_id, context)
        self.response_cache[cache_key] = (result, datetime.now())
        
        # Clean up old cache entries periodically
        if len(self.response_cache) > 1000:  # Arbitrary limit
            self._cleanup_cache()
    
    def _generate_cache_key(
        self,
        question: str,
        document_id: str,
        context: ProcessingContext
    ) -> str:
        """Generate cache key for request"""
        
        # Simple cache key based on question and document
        # In production, might want to include user context
        return f"{document_id}:{hash(question.lower())}"
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, (result, timestamp) in self.response_cache.items():
            if (current_time - timestamp).seconds >= self.config.cache_ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.response_cache[key]
    
    def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        if not self.config.enable_caching:
            return {}
        
        total_requests = self.processing_stats['total_requests']
        cache_hits = self.processing_stats['cache_hits']
        
        return {
            "cache_size": len(self.response_cache),
            "cache_hits": cache_hits,
            "total_requests": total_requests,
            "hit_rate": cache_hits / total_requests if total_requests > 0 else 0.0,
            "cache_limit": 1000
        }
    
    def _update_processing_stats(self, result: EnhancedProcessingResult) -> None:
        """Update processing statistics"""
        
        self.processing_stats['total_requests'] += 1
        
        # Update average processing time
        current_avg = self.processing_stats['average_processing_time']
        total_requests = self.processing_stats['total_requests']
        
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total_requests - 1) + result.processing_time) / total_requests
        )
    
    def _create_error_result(self, error_message: str, start_time: float) -> EnhancedProcessingResult:
        """Create error result"""
        
        processing_time = time.time() - start_time
        
        error_response = EnhancedResponse(
            content=f"I apologize, but I encountered an error processing your request: {error_message}",
            response_type=ResponseType.FALLBACK,
            confidence=0.0,
            sources=["error_handler"],
            suggestions=["Please try rephrasing your question", "Check if the document is available"],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["error_handling"],
            timestamp=datetime.now()
        )
        
        return EnhancedProcessingResult(
            response=error_response,
            processing_time=processing_time,
            quality_score=0.0,
            complexity_assessment=QuestionComplexity.SIMPLE,
            user_expertise_detected=ExpertiseLevel.INTERMEDIATE,
            enhancements_applied=[],
            performance_metrics={},
            cache_hit=False
        )
    
    async def _generate_detailed_insights(
        self,
        document: Document,
        advanced_analysis: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Generate detailed insights for document analysis"""
        
        insights = {
            "key_themes": self._extract_key_themes(document),
            "risk_summary": self._summarize_risks(advanced_analysis) if advanced_analysis else {},
            "opportunity_areas": self._identify_opportunities(document),
            "complexity_assessment": self._assess_document_complexity(document)
        }
        
        return insights
    
    async def _generate_predictive_insights(
        self,
        document: Document,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate predictive insights based on analysis"""
        
        # This would use ML models or heuristics to predict outcomes
        # For now, return placeholder insights
        return {
            "likely_negotiation_points": ["Payment terms", "Liability limitations", "IP ownership"],
            "potential_issues": ["Unclear termination conditions", "Broad confidentiality scope"],
            "recommended_actions": ["Review with legal counsel", "Negotiate liability caps"],
            "similar_document_patterns": "Standard MTA with typical research restrictions"
        }
    
    def _extract_key_themes(self, document: Document) -> List[str]:
        """Extract key themes from document"""
        # Simple keyword-based theme extraction
        content_lower = document.content.lower()
        
        themes = []
        theme_keywords = {
            "intellectual_property": ["intellectual property", "patent", "copyright", "ip"],
            "liability": ["liability", "damages", "indemnification", "risk"],
            "confidentiality": ["confidential", "proprietary", "non-disclosure"],
            "payment": ["payment", "fee", "cost", "compensation"],
            "termination": ["termination", "expiration", "end", "cancel"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _summarize_risks(self, advanced_analysis: Any) -> Dict[str, Any]:
        """Summarize risks from advanced analysis"""
        if not advanced_analysis or not advanced_analysis.risk_matrix:
            return {}
        
        risk_summary = {
            "total_risks": len(advanced_analysis.risk_matrix),
            "critical_risks": len([r for r in advanced_analysis.risk_matrix if r.overall_risk.value == "critical"]),
            "high_risks": len([r for r in advanced_analysis.risk_matrix if r.overall_risk.value == "high"]),
            "top_risk_categories": []
        }
        
        # Get top risk categories
        category_counts = {}
        for risk in advanced_analysis.risk_matrix:
            category_counts[risk.risk_category] = category_counts.get(risk.risk_category, 0) + 1
        
        risk_summary["top_risk_categories"] = sorted(
            category_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return risk_summary
    
    def _identify_opportunities(self, document: Document) -> List[str]:
        """Identify opportunities in the document"""
        # Simple opportunity identification
        opportunities = []
        content_lower = document.content.lower()
        
        if "research" in content_lower and "collaboration" in content_lower:
            opportunities.append("Research collaboration potential")
        
        if "license" in content_lower or "licensing" in content_lower:
            opportunities.append("Licensing revenue opportunities")
        
        if "improvement" in content_lower or "derivative" in content_lower:
            opportunities.append("Innovation and improvement rights")
        
        return opportunities
    
    def _assess_document_complexity(self, document: Document) -> Dict[str, Any]:
        """Assess document complexity"""
        content = document.content
        
        complexity_metrics = {
            "word_count": len(content.split()),
            "sentence_count": content.count('.') + content.count('!') + content.count('?'),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "legal_terms_count": len([term for term in [
                "liability", "indemnification", "intellectual property", "confidentiality",
                "termination", "breach", "warranty", "governing law"
            ] if term in content.lower()]),
            "complexity_score": "medium"  # Would calculate based on above metrics
        }
        
        # Simple complexity assessment
        if complexity_metrics["word_count"] > 5000 or complexity_metrics["legal_terms_count"] > 10:
            complexity_metrics["complexity_score"] = "high"
        elif complexity_metrics["word_count"] < 1000 and complexity_metrics["legal_terms_count"] < 3:
            complexity_metrics["complexity_score"] = "low"
        
        return complexity_metrics
    
    def _optimize_cache(self) -> None:
        """Optimize cache performance"""
        # Remove least recently used entries if cache is too large
        if len(self.response_cache) > 500:
            # Sort by timestamp and remove oldest 25%
            sorted_items = sorted(
                self.response_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            
            items_to_remove = len(sorted_items) // 4
            for i in range(items_to_remove):
                key = sorted_items[i][0]
                del self.response_cache[key]
    
    def _should_optimize_memory(self) -> bool:
        """Check if memory optimization is needed"""
        system_metrics = self.monitor._get_system_metrics()
        return system_metrics.get("memory_percent", 0) > 80
    
    def _optimize_memory_usage(self) -> None:
        """Optimize memory usage"""
        # Clear cache if memory usage is high
        if self.config.enable_caching:
            cache_size_before = len(self.response_cache)
            self.response_cache.clear()
            logger.info(f"Cleared cache to optimize memory usage (removed {cache_size_before} entries)")
        
        # Could also implement other memory optimizations here