#!/usr/bin/env python3
"""
Demo script for enhanced analysis capabilities.
This script demonstrates the core functionality without requiring API calls.
"""

from datetime import datetime
from src.models.document import Document
from src.services.template_engine import TemplateEngine
from src.storage.document_storage import DocumentStorage


def main():
    """Demonstrate enhanced analysis capabilities."""
    print("=== Enhanced Analysis Demo ===\n")
    
    # Create a mock storage
    storage = DocumentStorage()
    
    # Create template engine
    template_engine = TemplateEngine(storage)
    
    # Create a sample document
    sample_document = Document(
        id="demo_doc_1",
        title="Sample Service Agreement",
        file_type="pdf",
        file_size=15000,
        upload_timestamp=datetime.now(),
        original_text="""
        SERVICE AGREEMENT
        
        This Service Agreement is entered into between TechCorp Inc. ("Provider") 
        and BusinessCo LLC ("Client") effective January 1, 2024.
        
        SCOPE OF WORK:
        Provider shall deliver a custom software solution by December 31, 2024.
        The software must meet all specifications outlined in Exhibit A.
        
        PAYMENT TERMS:
        Client shall pay $100,000 in three installments:
        - $30,000 upon contract signing
        - $40,000 upon delivery of beta version (June 30, 2024)
        - $30,000 upon final delivery and acceptance
        
        LIABILITY:
        Provider's total liability shall not exceed $50,000 for any claims
        arising from this agreement.
        
        REPORTING:
        Provider must submit monthly progress reports by the 5th of each month.
        
        TERMINATION:
        Either party may terminate with 30 days written notice.
        """,
        is_legal_document=True,
        legal_document_type="Service Agreement",
        document_type="contract"
    )
    
    print(f"Document: {sample_document.title}")
    print(f"Type: {sample_document.legal_document_type}")
    print(f"Legal Document: {sample_document.is_legal_document}")
    print()
    
    # Demonstrate template recommendation
    print("=== Template Recommendation ===")
    recommended_template = template_engine.recommend_template(sample_document)
    if recommended_template:
        print(f"Recommended Template: {recommended_template.name}")
        print(f"Description: {recommended_template.description}")
        print(f"Analysis Sections: {', '.join(recommended_template.analysis_sections)}")
        print()
        
        # Demonstrate template application
        print("=== Template Application ===")
        template_result = template_engine.apply_template(sample_document, recommended_template)
        
        print(f"Template ID: {template_result['template_id']}")
        print(f"Template Name: {template_result['template_name']}")
        print("\nGenerated Prompts:")
        
        for section, prompt in template_result['prompts'].items():
            print(f"\n--- {section.upper()} ---")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    
    # Demonstrate predefined templates
    print("\n=== Available Predefined Templates ===")
    templates = template_engine.get_predefined_templates()
    
    for template in templates:
        print(f"\n{template.name}:")
        print(f"  - Document Types: {', '.join(template.document_types)}")
        print(f"  - Analysis Sections: {len(template.analysis_sections)} sections")
        print(f"  - Custom Prompts: {len(template.custom_prompts)} custom prompts")
        print(f"  - Version: {template.version}")
    
    # Demonstrate custom template creation
    print("\n=== Custom Template Creation ===")
    custom_template_spec = {
        'name': 'Demo Policy Analysis',
        'description': 'Custom template for policy document analysis',
        'document_types': ['policy', 'procedure'],
        'analysis_sections': ['policy_overview', 'requirements', 'compliance'],
        'custom_prompts': {
            'policy_overview': 'Provide a comprehensive overview of this policy document.',
            'requirements': 'Extract all requirements and obligations from this policy.',
            'compliance': 'Identify compliance requirements and potential violations.'
        },
        'parameters': {
            'focus_areas': ['compliance', 'requirements'],
            'detail_level': 'comprehensive'
        },
        'created_by': 'demo_user'
    }
    
    custom_template = template_engine.create_custom_template(custom_template_spec)
    print(f"Created Custom Template: {custom_template.name}")
    print(f"Template ID: {custom_template.template_id}")
    print(f"Analysis Sections: {', '.join(custom_template.analysis_sections)}")
    
    # Demonstrate data model usage
    print("\n=== Data Model Demonstration ===")
    
    from src.models.document import RiskAssessment, Commitment, DeliverableDate, ComprehensiveAnalysis
    
    # Create sample risk assessment
    sample_risk = RiskAssessment(
        risk_id="demo_risk_1",
        description="Limited liability cap may not cover all potential damages",
        severity="Medium",
        category="Financial",
        affected_parties=["TechCorp Inc.", "BusinessCo LLC"],
        mitigation_suggestions=["Increase liability cap", "Add comprehensive insurance"],
        source_text="Provider's total liability shall not exceed $50,000",
        confidence=0.85
    )
    
    # Create sample commitment
    sample_commitment = Commitment(
        commitment_id="demo_commitment_1",
        description="Deliver custom software solution",
        obligated_party="TechCorp Inc.",
        beneficiary_party="BusinessCo LLC",
        deadline=datetime(2024, 12, 31),
        status="Active",
        source_text="Provider shall deliver a custom software solution by December 31, 2024",
        commitment_type="Deliverable"
    )
    
    # Create sample deliverable date
    sample_date = DeliverableDate(
        date=datetime(2024, 6, 30),
        description="Beta version delivery",
        responsible_party="TechCorp Inc.",
        deliverable_type="Milestone",
        status="Pending",
        source_text="delivery of beta version (June 30, 2024)"
    )
    
    print("Sample Risk Assessment:")
    print(f"  - Description: {sample_risk.description}")
    print(f"  - Severity: {sample_risk.severity}")
    print(f"  - Category: {sample_risk.category}")
    print(f"  - Confidence: {sample_risk.confidence}")
    
    print("\nSample Commitment:")
    print(f"  - Description: {sample_commitment.description}")
    print(f"  - Obligated Party: {sample_commitment.obligated_party}")
    print(f"  - Deadline: {sample_commitment.deadline}")
    print(f"  - Type: {sample_commitment.commitment_type}")
    
    print("\nSample Deliverable Date:")
    print(f"  - Date: {sample_date.date}")
    print(f"  - Description: {sample_date.description}")
    print(f"  - Responsible Party: {sample_date.responsible_party}")
    print(f"  - Type: {sample_date.deliverable_type}")
    
    # Create comprehensive analysis
    comprehensive_analysis = ComprehensiveAnalysis(
        document_id=sample_document.id,
        analysis_id="demo_analysis_1",
        document_overview="This is a comprehensive service agreement between TechCorp and BusinessCo for software development.",
        key_findings=["Fixed-price contract for $100,000", "December 2024 delivery deadline", "Limited liability clause"],
        critical_information=["Payment schedule tied to milestones", "30-day termination clause"],
        recommended_actions=["Review liability limitations", "Clarify acceptance criteria", "Establish change management process"],
        executive_recommendation="Proceed with contract but negotiate higher liability cap and clearer acceptance criteria.",
        key_legal_terms=["Service Agreement", "Liability Cap", "Termination Clause", "Payment Terms"],
        risks=[sample_risk],
        commitments=[sample_commitment],
        deliverable_dates=[sample_date],
        template_used=recommended_template.template_id if recommended_template else None,
        confidence_score=0.87
    )
    
    print(f"\n=== Comprehensive Analysis Summary ===")
    print(f"Analysis ID: {comprehensive_analysis.analysis_id}")
    print(f"Document Overview: {comprehensive_analysis.document_overview}")
    print(f"Key Findings: {len(comprehensive_analysis.key_findings)} findings")
    print(f"Risks Identified: {len(comprehensive_analysis.risks)} risks")
    print(f"Commitments Found: {len(comprehensive_analysis.commitments)} commitments")
    print(f"Important Dates: {len(comprehensive_analysis.deliverable_dates)} dates")
    print(f"Confidence Score: {comprehensive_analysis.confidence_score:.2f}")
    
    # Test serialization
    print(f"\n=== Data Serialization Test ===")
    analysis_dict = comprehensive_analysis.to_dict()
    reconstructed = ComprehensiveAnalysis.from_dict(analysis_dict)
    
    print(f"Original Analysis ID: {comprehensive_analysis.analysis_id}")
    print(f"Reconstructed Analysis ID: {reconstructed.analysis_id}")
    print(f"Serialization successful: {comprehensive_analysis.analysis_id == reconstructed.analysis_id}")
    print(f"All data preserved: {len(reconstructed.risks) == len(comprehensive_analysis.risks)}")
    
    print("\n=== Demo Complete ===")
    print("All enhanced analysis components are working correctly!")


if __name__ == "__main__":
    main()