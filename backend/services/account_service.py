from fastapi import APIRouter, HTTPException

from .mock_data import MOCK_ACCOUNTS

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{user_id}")
def get_account_info(user_id: str):
    account = MOCK_ACCOUNTS.get(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "user_id": account["user_id"],
        "name": account["name"],
        "account_number": account["account_number"],
        "account_type": account["account_type"],
    }


@router.get("/{user_id}/balance")
def get_balance(user_id: str):
    account = MOCK_ACCOUNTS.get(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "user_id": account["user_id"],
        "balance": account["balance"],
        "currency": account["currency"],
    }


@router.get("/{user_id}/payment-methods")
def get_payment_methods(user_id: str):
    account = MOCK_ACCOUNTS.get(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "user_id": account["user_id"],
        "payment_methods": account["payment_methods"],
    }
