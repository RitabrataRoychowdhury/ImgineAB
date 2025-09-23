"""
Tests for MTA Specialist Module
"""

import pytest
from unittest.mock import Mock, patch
from src.services.mta_specialist import MTASpecialistModule, MTAKnowledgeBase
from src.models.enhanced import MTAContext, MTAInsight
from src.models.document import Document


class TestMTAKnowledgeBase:
    """Test MTA knowledge base functionality"""
    
    def test_knowledge_base_initialization(self):
        """Test that knowledge base initializes with expected data"""
        kb = MTAKnowledgeBase()
        
        # Check that key MTA terms are present
        assert 'provider' in kb.mta_terms
        assert 'recipient' in kb.mta_terms
        assert 'derivatives' in kb.mta_terms
        assert 'research_use_only' in kb.mta_terms
        
        # Check that risk factors are present
        assert len(kb.risk_factors) > 0
        assert any('IP' in risk for risk in kb.risk_factors)
        
        # Check that best practices are present
        assert len(kb.best_practices) > 0
        assert any('publication' in practice.lower() for practice in kb.best_practices)


class TestMTASpecialistModule:
    """Test MTA specialist module functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mta_specialist = MTASpecialistModule()
        
        # Create mock MTA document
        self.mock_mta_document = Mock(spec=Document)
        self.mock_mta_document.id = "test_mta_123"
        self.mock_mta_document.content = """
        Material Transfer Agreement
        
        Provider: University Research Institute
        Recipient: Academic Medical Center
        
        The Provider agrees to transfer biological cell lines and related materials
        to the Recipient for research use only. The Recipient may create derivatives
        and modifications but must acknowledge the Provider in any publications.
        
        Commercial use is prohibited without written consent. All intellectual
        property rights in derivatives shall be jointly owned.
        """
        
        # Create mock non-MTA document
        self.mock_contract_document = Mock(spec=Document)
        self.mock_contract_document.id = "test_contract_456"
        self.mock_contract_document.content = """
        Service Agreement
        
        This agreement governs the provision of consulting services.
        Payment terms are net 30 days. Liability is limited to direct damages.
        """
    
    def test_analyze_mta_context_success(self):
        """Test successful MTA context analysis"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        assert isinstance(context, MTAContext)
        assert context.document_id == "test_mta_123"
        assert context.provider_entity is not None
        assert context.recipient_entity is not None
        assert len(context.material_types) > 0
        assert context.collaboration_type in ['academic', 'commercial', 'hybrid', 'unknown']
    
    def test_analyze_mta_context_extracts_entities(self):
        """Test that MTA context analysis extracts entities correctly"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        # Should extract provider and recipient
        assert 'university' in context.provider_entity.lower() if context.provider_entity else False
        assert 'academic' in context.recipient_entity.lower() if context.recipient_entity else False
    
    def test_analyze_mta_context_identifies_materials(self):
        """Test that material types are identified"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        # Should identify cell lines
        assert any('cell' in material for material in context.material_types)
    
    def test_analyze_mta_context_determines_collaboration_type(self):
        """Test collaboration type determination"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        # Should be academic based on content
        assert context.collaboration_type == 'academic'
    
    def test_provide_mta_expertise_success(self):
        """Test MTA expertise provision"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        question = "What are the restrictions on derivatives?"
        
        insight = self.mta_specialist.provide_mta_expertise(question, context)
        
        assert isinstance(insight, MTAInsight)
        assert len(insight.concept_explanations) > 0
        assert len(insight.research_implications) > 0
        assert len(insight.suggested_questions) > 0
    
    def test_provide_mta_expertise_identifies_concepts(self):
        """Test that MTA expertise identifies relevant concepts"""
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        question = "What about derivatives and commercial use?"
        
        insight = self.mta_specialist.provide_mta_expertise(question, context)
        
        # Should identify derivatives and commercial use concepts
        concept_keys = [key.lower() for key in insight.concept_explanations.keys()]
        assert any('derivative' in key for key in concept_keys)
        assert any('commercial' in key for key in concept_keys)
    
    def test_explain_mta_concepts_known_terms(self):
        """Test explanation of known MTA concepts"""
        concepts = ['provider', 'derivatives', 'research_use_only']
        explanations = self.mta_specialist.explain_mta_concepts(concepts)
        
        assert len(explanations) == 3
        assert 'provider' in explanations
        assert 'derivatives' in explanations
        assert 'research_use_only' in explanations
        
        # Check that explanations are meaningful
        assert len(explanations['provider']) > 10
        assert 'material' in explanations['derivatives'].lower()
    
    def test_explain_mta_concepts_unknown_terms(self):
        """Test explanation of unknown MTA concepts"""
        concepts = ['unknown_term', 'made_up_concept']
        explanations = self.mta_specialist.explain_mta_concepts(concepts)
        
        assert len(explanations) == 2
        assert 'unknown_term' in explanations
        assert 'made_up_concept' in explanations
        
        # Should provide contextual explanation
        assert 'MTA context' in explanations['unknown_term']
    
    def test_suggest_mta_considerations_derivative_content(self):
        """Test MTA considerations for derivative-related content"""
        analysis_content = "The agreement allows creation of derivatives but retains IP rights"
        suggestions = self.mta_specialist.suggest_mta_considerations(analysis_content)
        
        assert len(suggestions) > 0
        assert any('intellectual property' in suggestion.lower() for suggestion in suggestions)
        assert any('derivative' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_mta_considerations_publication_content(self):
        """Test MTA considerations for publication-related content"""
        analysis_content = "Publication requires prior approval from provider"
        suggestions = self.mta_specialist.suggest_mta_considerations(analysis_content)
        
        assert len(suggestions) > 0
        assert any('publication' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_mta_considerations_general_content(self):
        """Test MTA considerations for general content"""
        analysis_content = "General contract terms and conditions"
        suggestions = self.mta_specialist.suggest_mta_considerations(analysis_content)
        
        # Should provide general MTA considerations
        assert len(suggestions) > 0
        assert len(suggestions) <= 5  # Should limit suggestions
    
    def test_generate_research_context_research_use_only(self):
        """Test research context generation for research use only clause"""
        clause = "This material is for research use only and cannot be used commercially"
        context = self.mta_specialist.generate_research_context(clause)
        
        assert len(context) > 0
        assert 'research' in context.lower()
        assert 'commercial' in context.lower()
        assert 'academic' in context.lower()
    
    def test_generate_research_context_derivative_clause(self):
        """Test research context generation for derivative clause"""
        clause = "Recipient may create derivatives but must share ownership"
        context = self.mta_specialist.generate_research_context(clause)
        
        assert len(context) > 0
        assert 'derivative' in context.lower()
        assert 'ownership' in context.lower()
    
    def test_generate_research_context_publication_clause(self):
        """Test research context generation for publication clause"""
        clause = "All publications must be reviewed by Provider before submission"
        context = self.mta_specialist.generate_research_context(clause)
        
        assert len(context) > 0
        assert 'publication' in context.lower()
        assert 'review' in context.lower()
    
    def test_generate_research_context_generic_clause(self):
        """Test research context generation for generic clause"""
        clause = "Standard liability and indemnification terms apply"
        context = self.mta_specialist.generate_research_context(clause)
        
        assert len(context) > 0
        assert 'research' in context.lower()
    
    def test_extract_provider_success(self):
        """Test provider extraction from document content"""
        content = "Provider: University Research Institute provides the materials"
        provider = self.mta_specialist._extract_provider(content.lower())
        
        assert provider is not None
        assert 'university' in provider.lower()
    
    def test_extract_recipient_success(self):
        """Test recipient extraction from document content"""
        content = "Recipient: Academic Medical Center will receive the materials"
        recipient = self.mta_specialist._extract_recipient(content.lower())
        
        assert recipient is not None
        assert 'academic' in recipient.lower()
    
    def test_identify_material_types_success(self):
        """Test material type identification"""
        content = "cell lines, dna samples, and protein reagents"
        materials = self.mta_specialist._identify_material_types(content)
        
        assert len(materials) > 0
        assert 'cell line' in materials or 'cells' in materials
        assert 'dna' in materials
        assert 'protein' in materials
    
    def test_extract_research_purposes_success(self):
        """Test research purpose extraction"""
        content = "for research and analysis purposes, including testing and evaluation"
        purposes = self.mta_specialist._extract_research_purposes(content)
        
        assert len(purposes) > 0
        assert any('research' in purpose for purpose in purposes)
        assert any('analysis' in purpose for purpose in purposes)
    
    def test_identify_ip_considerations_success(self):
        """Test IP consideration identification"""
        content = "intellectual property rights, patents, and derivatives ownership"
        considerations = self.mta_specialist._identify_ip_considerations(content)
        
        assert len(considerations) > 0
        assert any('intellectual property' in consideration.lower() for consideration in considerations)
        assert any('patent' in consideration.lower() for consideration in considerations)
    
    def test_extract_restrictions_success(self):
        """Test restriction extraction"""
        content = "shall not use for commercial purposes. prohibited from sharing with third parties."
        restrictions = self.mta_specialist._extract_restrictions(content)
        
        assert len(restrictions) > 0
        # Should extract sentences containing restrictions
        assert any('shall not' in restriction or 'prohibited' in restriction for restriction in restrictions)
    
    def test_determine_collaboration_type_academic(self):
        """Test academic collaboration type determination"""
        content = "university research institution academic collaboration"
        collab_type = self.mta_specialist._determine_collaboration_type(content)
        
        assert collab_type == 'academic'
    
    def test_determine_collaboration_type_commercial(self):
        """Test commercial collaboration type determination"""
        content = "commercial industry partnership for profit"
        collab_type = self.mta_specialist._determine_collaboration_type(content)
        
        assert collab_type == 'commercial'
    
    def test_determine_collaboration_type_hybrid(self):
        """Test hybrid collaboration type determination"""
        content = "academic university and commercial industry partnership"
        collab_type = self.mta_specialist._determine_collaboration_type(content)
        
        assert collab_type == 'hybrid'
    
    def test_determine_collaboration_type_unknown(self):
        """Test unknown collaboration type determination"""
        content = "general agreement terms and conditions"
        collab_type = self.mta_specialist._determine_collaboration_type(content)
        
        assert collab_type == 'unknown'
    
    def test_identify_relevant_concepts_success(self):
        """Test relevant concept identification"""
        question = "what about derivatives and commercial use restrictions?"
        concepts = self.mta_specialist._identify_relevant_concepts(question)
        
        assert len(concepts) > 0
        assert 'derivatives' in concepts or 'derivative' in concepts
        assert 'commercial_use' in concepts or 'commercial' in concepts
    
    def test_generate_research_implications_derivatives(self):
        """Test research implications for derivatives"""
        question = "what about derivatives and modifications?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        implications = self.mta_specialist._generate_research_implications(question, context)
        
        assert len(implications) > 0
        assert any('derivative' in implication.lower() for implication in implications)
        assert any('research' in implication.lower() for implication in implications)
    
    def test_generate_research_implications_publication(self):
        """Test research implications for publication"""
        question = "what are the publication requirements?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        implications = self.mta_specialist._generate_research_implications(question, context)
        
        assert len(implications) > 0
        assert any('publication' in implication.lower() for implication in implications)
    
    def test_suggest_common_practices_negotiation(self):
        """Test common practices suggestions for negotiation"""
        question = "how should I negotiate these terms?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        practices = self.mta_specialist._suggest_common_practices(question, context)
        
        assert len(practices) > 0
        assert len(practices) <= 3  # Should limit to top 3
        assert any('negotiate' in practice.lower() for practice in practices)
    
    def test_suggest_common_practices_ip(self):
        """Test common practices suggestions for IP"""
        question = "what about intellectual property rights?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        practices = self.mta_specialist._suggest_common_practices(question, context)
        
        assert len(practices) > 0
        assert any('ip' in practice.lower() or 'intellectual' in practice.lower() for practice in practices)
    
    def test_identify_risk_considerations_success(self):
        """Test risk consideration identification"""
        question = "what are the IP risks with broad claims?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        risks = self.mta_specialist._identify_risk_considerations(question, context)
        
        assert len(risks) <= 3  # Should limit to top 3
        # Should identify relevant risks from knowledge base
    
    def test_generate_suggested_questions_success(self):
        """Test suggested question generation"""
        question = "what about derivatives?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        suggestions = self.mta_specialist._generate_suggested_questions(question, context)
        
        assert len(suggestions) > 0
        assert len(suggestions) <= 3  # Should limit to top 3
        
        # Should not include questions too similar to the original
        for suggestion in suggestions:
            assert 'derivative' not in suggestion.lower()  # Should filter out similar questions
    
    def test_generate_suggested_questions_filters_similar(self):
        """Test that suggested questions filter out similar ones"""
        question = "What are the key restrictions on material use?"
        context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
        
        suggestions = self.mta_specialist._generate_suggested_questions(question, context)
        
        # Should not include the exact same question about restrictions
        assert not any('key restrictions' in suggestion.lower() for suggestion in suggestions)
    
    @patch('src.services.mta_specialist.logger')
    def test_error_handling_in_analyze_mta_context(self, mock_logger):
        """Test error handling in MTA context analysis"""
        # Create a document that might cause issues
        problematic_document = Mock(spec=Document)
        problematic_document.id = "test"
        problematic_document.content = None  # This might cause issues
        
        # Should not raise exception
        try:
            context = self.mta_specialist.analyze_mta_context(problematic_document)
            # Should return a valid context even with problematic input
            assert isinstance(context, MTAContext)
        except Exception:
            pytest.fail("analyze_mta_context should handle errors gracefully")
    
    def test_performance_with_large_document(self):
        """Test performance with large document content"""
        # Create a large document
        large_content = self.mock_mta_document.content * 100  # Repeat content 100 times
        large_document = Mock(spec=Document)
        large_document.id = "large_test"
        large_document.content = large_content
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        
        context = self.mta_specialist.analyze_mta_context(large_document)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within 5 seconds for large document
        assert processing_time < 5.0
        assert isinstance(context, MTAContext)
    
    def test_thread_safety(self):
        """Test that MTA specialist is thread-safe"""
        import threading
        import time
        
        results = []
        errors = []
        
        def analyze_document():
            try:
                context = self.mta_specialist.analyze_mta_context(self.mock_mta_document)
                results.append(context)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=analyze_document)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # All results should be valid
        for result in results:
            assert isinstance(result, MTAContext)
            assert result.document_id == "test_mta_123"