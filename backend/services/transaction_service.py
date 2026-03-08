from fastapi import APIRouter, HTTPException

from .mock_data import MOCK_TRANSACTIONS

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/{user_id}")
def get_transactions(user_id: str):
    transactions = MOCK_TRANSACTIONS.get(user_id)
    if transactions is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "transactions": transactions}


@router.get("/{user_id}/search")
def search_transactions(user_id: str, recipient: str | None = None, category: str | None = None):
    transactions = MOCK_TRANSACTIONS.get(user_id)
    if transactions is None:
        raise HTTPException(status_code=404, detail="User not found")
    results = transactions
    if recipient:
        results = [t for t in results if t.get("recipient") and recipient.lower() in t["recipient"].lower()]
    if category:
        results = [t for t in results if category.lower() in t["category"].lower()]
    return {"user_id": user_id, "transactions": results}
