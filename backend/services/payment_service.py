import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .mock_data import MOCK_ACCOUNTS, MOCK_PAYMENTS

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentRequest(BaseModel):
    recipient: str
    amount: float
    currency: str = "USD"
    description: str = ""


@router.post("/{user_id}")
def submit_payment(user_id: str, payment: PaymentRequest):
    account = MOCK_ACCOUNTS.get(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if payment.amount > account["balance"]:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    payment_record = {
        "payment_id": f"pay-{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "recipient": payment.recipient,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "status": "completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    MOCK_PAYMENTS.append(payment_record)
    account["balance"] -= payment.amount
    return payment_record


@router.get("/{user_id}/history")
def get_payment_history(user_id: str):
    account = MOCK_ACCOUNTS.get(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    user_payments = [p for p in MOCK_PAYMENTS if p["user_id"] == user_id]
    return {"user_id": user_id, "payments": user_payments}
