"""
MTA Specialist Module for Enhanced Contract Assistant

Provides specialized knowledge and context for Material Transfer Agreement analysis.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re
from src.models.enhanced import MTAContext, MTAInsight, CollaborationType
from src.models.document import Document


@dataclass
class MTAKnowledgeBase:
    """Knowledge base for MTA-specific concepts and terminology"""
    
    # Common MTA terminology and concepts
    mta_terms = {
        'provider': 'The institution or entity providing the original material',
        'recipient': 'The institution or entity receiving the material for research',
        'original_material': 'The material being transferred as specified in the agreement',
        'derivatives': 'Materials created by the recipient that incorporate or are derived from the original material',
        'modifications': 'Any changes, improvements, or alterations made to the original material',
        'progeny': 'Unmodified descendants of the original material (e.g., cell lines, offspring)',
        'research_use_only': 'Restriction limiting use to non-commercial research purposes',
        'commercial_use': 'Use for profit-making activities or product development',
        'publication_rights': 'Rights and restrictions regarding publishing research results',
        'ip_rights': 'Intellectual property rights related to the material and derivatives',
        'confidentiality': 'Obligations to keep certain information confidential',
        'liability': 'Responsibility for damages or issues arising from material use',
        'indemnification': 'Protection from legal claims related to material use'
    }
    
    # Common MTA risk factors
    risk_factors = [
        'Broad IP claims on derivatives',
        'Restrictive publication requirements',
        'Unlimited liability exposure',
        'Vague material description',
        'Unclear termination conditions',
        'Excessive confidentiality obligations',
        'Commercial use restrictions affecting future research',
        'Third-party rights complications'
    ]
    
    # Research collaboration best practices
    best_practices = [
        'Clearly define the scope of permitted research',
        'Negotiate reasonable publication timelines',
        'Limit liability to direct damages when possible',
        'Specify ownership of improvements and derivatives',
        'Include termination and return provisions',
        'Address third-party collaborator rights',
        'Consider future commercial applications',
        'Establish clear communication protocols'
    ]


class MTASpecialistModule:
    """Specialized module for MTA analysis and expertise"""
    
    def __init__(self):
        self.knowledge_base = MTAKnowledgeBase()
        
    def analyze_mta_context(self, document: Document) -> MTAContext:
        """Analyze document to extract MTA-specific context"""
        content = document.content.lower()
        
        # Extract entities
        provider = self._extract_provider(content)
        recipient = self._extract_recipient(content)
        
        # Identify material types
        material_types = self._identify_material_types(content)
        
        # Extract research purposes
        research_purposes = self._extract_research_purposes(content)
        
        # Identify IP considerations
        ip_considerations = self._identify_ip_considerations(content)
        
        # Extract key restrictions
        key_restrictions = self._extract_restrictions(content)
        
        # Determine collaboration type
        collaboration_type = self._determine_collaboration_type(content)
        
        return MTAContext(
            document_id=document.id,
            provider_entity=provider,
            recipient_entity=recipient,
            material_types=material_types,
            research_purposes=research_purposes,
            ip_considerations=ip_considerations,
            key_restrictions=key_restrictions,
            collaboration_type=collaboration_type
        )
    
    def provide_mta_expertise(self, question: str, context: MTAContext) -> MTAInsight:
        """Provide MTA-specific expertise for a question"""
        question_lower = question.lower()
        
        # Identify relevant concepts in the question
        relevant_concepts = self._identify_relevant_concepts(question_lower)
        
        # Generate concept explanations
        concept_explanations = {
            concept: self.knowledge_base.mta_terms.get(concept, f"MTA concept: {concept}")
            for concept in relevant_concepts
        }
        
        # Generate research implications
        research_implications = self._generate_research_implications(question_lower, context)
        
        # Suggest common practices
        common_practices = self._suggest_common_practices(question_lower, context)
        
        # Identify risk considerations
        risk_considerations = self._identify_risk_considerations(question_lower, context)
        
        # Generate suggested questions
        suggested_questions = self._generate_suggested_questions(question_lower, context)
        
        return MTAInsight(
            concept_explanations=concept_explanations,
            research_implications=research_implications,
            common_practices=common_practices,
            risk_considerations=risk_considerations,
            suggested_questions=suggested_questions
        )
    
    def explain_mta_concepts(self, concepts: List[str]) -> Dict[str, str]:
        """Explain MTA-specific concepts"""
        explanations = {}
        for concept in concepts:
            concept_key = concept.lower().replace(' ', '_')
            if concept_key in self.knowledge_base.mta_terms:
                explanations[concept] = self.knowledge_base.mta_terms[concept_key]
            else:
                # Generate contextual explanation for unknown concepts
                explanations[concept] = f"In MTA context: {concept} refers to a specific aspect of material transfer agreements that should be carefully reviewed."
        
        return explanations
    
    def suggest_mta_considerations(self, analysis_content: str) -> List[str]:
        """Suggest MTA-specific considerations based on analysis"""
        content_lower = analysis_content.lower()
        suggestions = []
        
        # Check for common MTA issues and suggest considerations
        if 'derivative' in content_lower or 'modification' in content_lower:
            suggestions.append("Consider who owns intellectual property rights to derivatives and modifications")
        
        if 'publication' in content_lower:
            suggestions.append("Review publication timeline requirements and approval processes")
        
        if 'commercial' in content_lower:
            suggestions.append("Clarify restrictions on commercial use and future licensing opportunities")
        
        if 'liability' in content_lower:
            suggestions.append("Assess liability limitations and indemnification provisions")
        
        if 'confidential' in content_lower:
            suggestions.append("Evaluate confidentiality obligations and their impact on research collaboration")
        
        if 'termination' in content_lower:
            suggestions.append("Understand material return or destruction requirements upon termination")
        
        # Add general MTA considerations if none specific found
        if not suggestions:
            suggestions.extend([
                "Verify the scope of permitted research activities",
                "Check for any restrictions on sharing with collaborators",
                "Review intellectual property ownership provisions"
            ])
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def generate_research_context(self, clause: str) -> str:
        """Generate research context explanation for a clause"""
        clause_lower = clause.lower()
        
        if 'research use only' in clause_lower:
            return "This clause restricts use to non-commercial research, which is common in academic MTAs to protect the provider's commercial interests while enabling scientific advancement."
        
        if 'derivative' in clause_lower:
            return "Derivative provisions are crucial in research settings as they determine ownership of improvements, modifications, or new discoveries made using the original material."
        
        if 'publication' in clause_lower:
            return "Publication clauses balance the academic need to share research findings with the provider's need to protect proprietary information and review results before disclosure."
        
        if 'collaboration' in clause_lower:
            return "Collaboration terms define how the material can be shared with other researchers, which is essential for multi-institutional research projects."
        
        return "This provision should be evaluated in the context of your research goals and institutional policies for material transfer agreements."
    
    def _extract_provider(self, content: str) -> Optional[str]:
        """Extract provider entity from document content"""
        # Look for common provider patterns
        provider_patterns = [
            r'provider[:\s]+([^,\n]+)',
            r'providing institution[:\s]+([^,\n]+)',
            r'material provided by[:\s]+([^,\n]+)'
        ]
        
        for pattern in provider_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_recipient(self, content: str) -> Optional[str]:
        """Extract recipient entity from document content"""
        # Look for common recipient patterns
        recipient_patterns = [
            r'recipient[:\s]+([^,\n]+)',
            r'receiving institution[:\s]+([^,\n]+)',
            r'material received by[:\s]+([^,\n]+)'
        ]
        
        for pattern in recipient_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _identify_material_types(self, content: str) -> List[str]:
        """Identify types of materials mentioned in the document"""
        material_keywords = [
            'cell line', 'cells', 'tissue', 'dna', 'rna', 'protein', 'antibody',
            'plasmid', 'vector', 'bacteria', 'virus', 'sample', 'specimen',
            'chemical', 'compound', 'reagent', 'mouse', 'animal model'
        ]
        
        found_materials = []
        for keyword in material_keywords:
            if keyword in content:
                found_materials.append(keyword)
        
        return found_materials
    
    def _extract_research_purposes(self, content: str) -> List[str]:
        """Extract research purposes from document content"""
        purpose_keywords = [
            'research', 'study', 'investigation', 'analysis', 'testing',
            'experiment', 'evaluation', 'characterization', 'screening'
        ]
        
        purposes = []
        for keyword in purpose_keywords:
            if keyword in content:
                purposes.append(f"{keyword} activities")
        
        return list(set(purposes))  # Remove duplicates
    
    def _identify_ip_considerations(self, content: str) -> List[str]:
        """Identify IP-related considerations in the document"""
        ip_keywords = [
            'intellectual property', 'patent', 'copyright', 'trademark',
            'derivative', 'modification', 'improvement', 'invention'
        ]
        
        considerations = []
        for keyword in ip_keywords:
            if keyword in content:
                considerations.append(f"{keyword.title()} rights and ownership")
        
        return considerations
    
    def _extract_restrictions(self, content: str) -> List[str]:
        """Extract key restrictions from the document"""
        restriction_patterns = [
            'shall not', 'prohibited', 'restricted', 'limited to',
            'only for', 'except', 'without permission', 'not permitted'
        ]
        
        restrictions = []
        for pattern in restriction_patterns:
            if pattern in content:
                # Find the sentence containing the restriction
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence:
                        restrictions.append(sentence.strip())
                        break
        
        return restrictions[:3]  # Limit to top 3 restrictions
    
    def _determine_collaboration_type(self, content: str) -> CollaborationType:
        """Determine the type of collaboration based on document content"""
        if 'commercial' in content and 'academic' in content:
            return CollaborationType.HYBRID
        elif 'commercial' in content or 'industry' in content:
            return CollaborationType.COMMERCIAL
        elif 'academic' in content or 'university' in content or 'research institution' in content:
            return CollaborationType.ACADEMIC
        else:
            return CollaborationType.ACADEMIC  # Default to academic
    
    def _identify_relevant_concepts(self, question: str) -> List[str]:
        """Identify MTA concepts relevant to the question"""
        relevant_concepts = []
        
        for concept in self.knowledge_base.mta_terms.keys():
            if concept.replace('_', ' ') in question or concept in question:
                relevant_concepts.append(concept)
        
        return relevant_concepts
    
    def _generate_research_implications(self, question: str, context: MTAContext) -> List[str]:
        """Generate research implications based on question and context"""
        implications = []
        
        if 'derivative' in question or 'modification' in question:
            implications.append("Research derivatives may be subject to provider's IP claims")
            implications.append("Consider impact on future research and commercialization")
        
        if 'publication' in question:
            implications.append("Publication delays may affect research timelines and career advancement")
            implications.append("Review requirements may limit academic freedom")
        
        if 'collaboration' in question:
            implications.append("Sharing restrictions may limit multi-institutional research opportunities")
            implications.append("Third-party access may require additional approvals")
        
        return implications
    
    def _suggest_common_practices(self, question: str, context: MTAContext) -> List[str]:
        """Suggest common practices relevant to the question"""
        practices = []
        
        if 'negotiation' in question or 'terms' in question:
            practices.extend([
                "Negotiate reasonable publication review periods (30-60 days)",
                "Seek to limit liability to direct damages only",
                "Clarify ownership of improvements and derivatives"
            ])
        
        if 'ip' in question or 'intellectual property' in question:
            practices.extend([
                "Retain rights to independently developed improvements",
                "Negotiate joint ownership for collaborative developments",
                "Include background IP protection clauses"
            ])
        
        return practices[:3]  # Limit to top 3 practices
    
    def _identify_risk_considerations(self, question: str, context: MTAContext) -> List[str]:
        """Identify risk considerations relevant to the question"""
        risks = []
        
        for risk in self.knowledge_base.risk_factors:
            risk_keywords = risk.lower().split()
            if any(keyword in question for keyword in risk_keywords):
                risks.append(risk)
        
        return risks[:3]  # Limit to top 3 risks
    
    def _generate_suggested_questions(self, question: str, context: MTAContext) -> List[str]:
        """Generate suggested follow-up questions"""
        suggestions = [
            "What are the key restrictions on material use?",
            "Who owns intellectual property rights to derivatives?",
            "What are the publication review requirements?",
            "Are there limitations on sharing with collaborators?",
            "What happens to the material upon agreement termination?"
        ]
        
        # Filter out questions similar to the current one
        filtered_suggestions = []
        question_words = set(question.lower().split())
        
        for suggestion in suggestions:
            suggestion_words = set(suggestion.lower().split())
            # If less than 50% word overlap, include the suggestion
            overlap = len(question_words.intersection(suggestion_words))
            if overlap / len(suggestion_words) < 0.5:
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions[:3]  # Limit to top 3 suggestions