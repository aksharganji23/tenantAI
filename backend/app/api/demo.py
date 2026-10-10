from fastapi import APIRouter, Depends

router = APIRouter(prefix="/demo", tags=["Demo Support"])


@router.get("/accounts")
def get_demo_accounts():
    """No demo accounts are exposed in production or clean local installs."""
    return {"accounts": []}
