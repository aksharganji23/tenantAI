from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.seed.seed_data import run_seed

router = APIRouter(prefix="/demo", tags=["Demo Support"])


@router.get("/accounts")
def get_demo_accounts():
    """Returns demo accounts and suggested questions for the hackathon jury."""
    return {
        "accounts": [
            {
                "company": "TechNova Solutions",
                "slug": "technova",
                "role": "Tenant Administrator",
                "email": "admin@technova.com",
                "password": "DemoPass123!",
                "badge": "Company A (IT & Hardware)",
                "sample_document": "TechNova UltraBook Pro Manual",
                "recommended_prompts": [
                    "What is the warranty coverage for the UltraBook Pro battery?",
                    "How do I perform a BIOS password reset?",
                    "What is the maximum supported RAM configuration?"
                ],
                "cross_tenant_test": "Ask about GreenLeaf's 30-day refund policy (should be denied/refused)"
            },
            {
                "company": "GreenLeaf Retail",
                "slug": "greenleaf",
                "role": "Tenant Administrator",
                "email": "admin@greenleaf.com",
                "password": "DemoPass123!",
                "badge": "Company B (Retail E-Commerce)",
                "sample_document": "GreenLeaf Retail Refund & Return Policy",
                "recommended_prompts": [
                    "What is the return window for general purchases?",
                    "Can perishable goods or open cosmetics be refunded?",
                    "Is there a restocking fee for opened consumer electronics?"
                ],
                "cross_tenant_test": "Ask about TechNova UltraBook BIOS reset (should be denied/refused)"
            },
            {
                "company": "System Administrator",
                "slug": "superadmin",
                "role": "Global SuperAdmin",
                "email": "admin@tenantai.com",
                "password": "SuperAdmin123!",
                "badge": "Platform Operator",
                "sample_document": "Global System Overview",
                "recommended_prompts": [
                    "View platform-wide usage metrics, tenant quotas, and audit logs"
                ],
                "cross_tenant_test": "Inspect cross-tenant audit alerts in Admin Panel"
            }
        ]
    }


@router.post("/reset-seed")
def reset_seed_data(db: Session = Depends(get_db)):
    """Reset database and re-seed with clean hackathon demo data."""
    run_seed(db)
    return {"message": "Database successfully reseeded with fresh demo tenants and documents"}
