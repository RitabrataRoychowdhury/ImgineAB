"""
Comprehensive test to identify and fix question routing issues.
"""

import sys
sys.path.append('.')

from unittest.mock import Mock
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.question_classifier import QuestionClassifier
from src.models.document import Document
from src.models.enhanced import IntentType, ResponseType
from src.storage.document_storage import DocumentStorage


def create_mock_mta_document():
    """Create a mock MTA document for testing."""
    doc = Mock(spec=Document)
    doc.id = "mta_doc_1"
    doc.title = "Material Transfer Agreement - ImaginAb to MNRI"
    doc.content = """
    MATERIAL TRANSFER AGREEMENT
    
    This Material Transfer Agreement ("Agreement") is entered into between ImaginAb, Inc. ("Provider") 
    and Molecular Nuclear Research Institute ("MNRI", "Recipient") for the transfer of research materials.
    
    1. MATERIALS: Provider will transfer antibody materials for research use only.
    
    2. AUTHORIZED LOCATION: Materials must be stored at MNRI facilities at 123 Research Drive.
    
    3. RESEARCH PLAN: MNRI will conduct imaging studies using the transferred materials.
    
    4. PUBLICATION: Any publication must acknowledge Provider and follow IP protection guidelines.
    
    5. INTELLECTUAL PROPERTY: Provider retains ownership of original materials. 
       Any derivatives or improvements developed by MNRI shall be jointly owned.
    
    6. CONFIDENTIALITY: All information shall remain confidential for 5 years after termination.
    
    7. TERMINATION: Agreement expires October 31, 2024. Unused materials must be returned.
    
    8. LIABILITY: Provider disclaims all warranties. MNRI assumes all risks.
    
    Signed by:
    Dr. Jane Smith, CEO, ImaginAb
    Dr. Robert Johnson, Director, MNRI
    """
    doc.original_text = doc.content
    doc.is_legal_document = True
    doc.legal_document_type = "MTA"
    return doc


def test_question_classification():
    """Test question classification accuracy."""
    
    print("🔍 Testing Question Classification")
    print("=" * 50)
    
    classifier = QuestionClassifier()
    
    test_cases = [
        # Document-related questions
        ("Who are the parties in this agreement?", IntentType.DOCUMENT_RELATED),
        ("What are the termination conditions?", IntentType.DOCUMENT_RELATED),
        ("When does the agreement expire?", IntentType.DOCUMENT_RELATED),
        
        # General knowledge questions  
        ("What is a liability clause?", IntentType.CONTRACT_GENERAL),
        ("What does intellectual property mean?", IntentType.CONTRACT_GENERAL),
        ("Explain what an MTA is", IntentType.CONTRACT_GENERAL),
        
        # Casual questions
        ("Hi there! How are you?", IntentType.CASUAL),
        ("Thanks, that was helpful!", IntentType.CASUAL),
        ("Hello!", IntentType.CASUAL),
        
        # Off-topic questions
        ("What's the weather like?", IntentType.OFF_TOPIC),
        ("Can you tell me a joke?", IntentType.OFF_TOPIC),
        ("What should I have for dinner?", IntentType.OFF_TOPIC),
        ("Can you explain this agreement in the style of a cooking recipe?", IntentType.OFF_TOPIC),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for question, expected_intent in test_cases:
        intent = classifier.classify_intent(question)
        
        is_correct = intent.primary_intent == expected_intent
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{question[:50]}...'")
        print(f"   Expected: {expected_intent.value}, Got: {intent.primary_intent.value}")
        print(f"   Confidence: {intent.confidence:.2f}, Casualness: {intent.casualness_level:.2f}")
        print()
    
    accuracy = (correct / total) * 100
    print(f"Classification Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    return accuracy > 80  # Expect at least 80% accuracy


def test_enhanced_router():
    """Test enhanced router with different question types."""
    
    print("\n🚀 Testing Enhanced Response Router")
    print("=" * 50)
    
    # Create mock document and router
    mock_doc = create_mock_mta_document()
    storage = Mock(spec=DocumentStorage)
    storage.get_document_with_embeddings.return_value = mock_doc
    
    router = EnhancedResponseRouter(storage, "test_key")
    router.contract_engine.analyze_question = Mock(return_value={
        'response': 'Test contract analysis response',
        'direct_evidence': 'Test evidence from document',
        'plain_explanation': 'Test plain explanation',
        'sources': ['Document Section 1'],
        'confidence': 0.8
    })
    
    # Test categories with expected response types
    test_categories = {
        "📑 Document-Grounded": {
            "questions": [
                "Who are the parties involved in this agreement?",
                "When does the agreement start and when does it expire?",
                "What is the authorized location for the materials?",
                "What must MNRI do with unused materials at the end of the agreement?",
                "How long do confidentiality obligations last after termination?"
            ],
            "expected_type": ResponseType.DOCUMENT_ANALYSIS
        },
        "🔄 Multi-Section / Cross-Exhibit": {
            "questions": [
                "What are the deliverables MNRI must provide, and when?",
                "What publication restrictions exist, and how do they connect to IP protection?",
                "If MNRI invented a new method of imaging using the materials, who owns the rights and why?"
            ],
            "expected_type": ResponseType.DOCUMENT_ANALYSIS
        },
        "⚖️ Subjective / Interpretive": {
            "questions": [
                "Who benefits more from this agreement, ImaginAb or MNRI? Why?",
                "What are the biggest risks MNRI faces in this agreement?",
                "Is this agreement more favorable to research freedom or to IP protection?",
                "If you were MNRI's lab manager, what would you be most careful about?"
            ],
            "expected_type": ResponseType.DOCUMENT_ANALYSIS
        },
        "💡 Scenario / What if": {
            "questions": [
                "What happens if MNRI uses the materials in humans?",
                "Suppose MNRI accidentally shares the materials with another lab — what does the agreement require?",
                "If the research goes beyond October 2024, what must MNRI do?",
                "What happens if MNRI wants to combine these materials with another drug?"
            ],
            "expected_type": ResponseType.DOCUMENT_ANALYSIS
        },
        "🧩 Ambiguity / Compound": {
            "questions": [
                "Where are the materials supposed to be stored, who is responsible for them, and what specific materials are included?",
                "What termination rights do both parties have, and what must happen with the materials afterward?",
                "Can you summarize the agreement as if you were explaining it to a PhD student new to MTAs?"
            ],
            "expected_type": ResponseType.DOCUMENT_ANALYSIS
        },
        "🎭 Off-Topic / Casual / Playful": {
            "questions": [
                "Can you explain this agreement in the style of a cooking recipe?",
                "If I were a mouse in this study, what would happen to me?",
                "What's the \"vibe\" of this agreement — collaborative, strict, or neutral?",
                "Tell me a lawyer joke involving antibodies."
            ],
            "expected_type": [ResponseType.CASUAL, ResponseType.FALLBACK]  # Either is acceptable
        }
    }
    
    results = {}
    total_correct = 0
    total_questions = 0
    
    for category, test_data in test_categories.items():
        print(f"\n{category}")
        print("-" * 40)
        
        questions = test_data["questions"]
        expected_type = test_data["expected_type"]
        
        category_correct = 0
        
        for question in questions:
            try:
                response = router.route_question(question, mock_doc.id, "test_session", mock_doc)
                
                # Check if response type matches expected
                if isinstance(expected_type, list):
                    is_correct = response.response_type in expected_type
                else:
                    is_correct = response.response_type == expected_type
                
                if is_correct:
                    category_correct += 1
                    total_correct += 1
                    status = "✅"
                else:
                    status = "❌"
                
                total_questions += 1
                
                print(f"{status} {question[:60]}...")
                print(f"   Type: {response.response_type.value}, Confidence: {response.confidence:.2f}")
                print(f"   Has Content: {len(response.content) > 0}, Has Suggestions: {len(response.suggestions) > 0}")
                
            except Exception as e:
                print(f"❌ {question[:60]}...")
                print(f"   ERROR: {str(e)}")
                total_questions += 1
        
        category_accuracy = (category_correct / len(questions)) * 100
        print(f"Category Accuracy: {category_correct}/{len(questions)} ({category_accuracy:.1f}%)")
        
        results[category] = {
            'correct': category_correct,
            'total': len(questions),
            'accuracy': category_accuracy
        }
    
    overall_accuracy = (total_correct / total_questions) * 100
    print(f"\n📊 Overall Results")
    print(f"Total Accuracy: {total_correct}/{total_questions} ({overall_accuracy:.1f}%)")
    
    return results, overall_accuracy


def identify_issues_and_fixes():
    """Identify specific issues and propose fixes."""
    
    print("\n🔧 Issue Analysis and Fixes")
    print("=" * 50)
    
    # Test classification accuracy
    classification_ok = test_question_classification()
    
    # Test router accuracy
    router_results, router_accuracy = test_enhanced_router()
    
    issues = []
    fixes = []
    
    if not classification_ok:
        issues.append("Question classification accuracy is below 80%")
        fixes.append("Improve question classifier patterns and scoring")
    
    if router_accuracy < 70:
        issues.append(f"Router accuracy is {router_accuracy:.1f}%, below acceptable threshold")
        fixes.append("Fix response routing logic and strategy determination")
    
    # Check specific category issues
    for category, results in router_results.items():
        if results['accuracy'] < 60:
            issues.append(f"{category} category has low accuracy: {results['accuracy']:.1f}%")
            
            if "Off-Topic" in category:
                fixes.append("Improve off-topic and casual question detection")
            elif "Document" in category:
                fixes.append("Fix document-related question routing")
            elif "Subjective" in category:
                fixes.append("Improve subjective question handling")
    
    print("\n🚨 Issues Identified:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    print("\n🛠️ Proposed Fixes:")
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix}")
    
    return issues, fixes


if __name__ == "__main__":
    print("🧪 Comprehensive Question Handling Analysis")
    print("=" * 60)
    
    issues, fixes = identify_issues_and_fixes()
    
    if not issues:
        print("\n✅ All tests passed! The system is working correctly.")
    else:
        print(f"\n⚠️ Found {len(issues)} issues that need to be addressed.")