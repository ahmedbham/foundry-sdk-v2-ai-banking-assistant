MOCK_ACCOUNTS = {
    "user1": {
        "user_id": "user1",
        "name": "Alice Johnson",
        "account_number": "1234567890",
        "account_type": "Checking",
        "balance": 5420.75,
        "currency": "USD",
        "payment_methods": [
            {"type": "debit_card", "last_four": "4532", "brand": "Visa"},
            {"type": "bank_transfer", "bank_name": "Chase", "routing_number": "***6789"},
        ],
    },
    "user2": {
        "user_id": "user2",
        "name": "Bob Smith",
        "account_number": "0987654321",
        "account_type": "Savings",
        "balance": 12350.00,
        "currency": "USD",
        "payment_methods": [
            {"type": "credit_card", "last_four": "8821", "brand": "Mastercard"},
        ],
    },
}

MOCK_TRANSACTIONS = {
    "user1": [
        {"transaction_id": "txn001", "date": "2026-03-01", "description": "Grocery Store", "amount": -85.50, "currency": "USD", "category": "Groceries", "recipient": "Whole Foods"},
        {"transaction_id": "txn002", "date": "2026-03-02", "description": "Direct Deposit", "amount": 3200.00, "currency": "USD", "category": "Income", "recipient": None},
        {"transaction_id": "txn003", "date": "2026-03-03", "description": "Electric Bill", "amount": -142.30, "currency": "USD", "category": "Utilities", "recipient": "City Power Co"},
        {"transaction_id": "txn004", "date": "2026-03-05", "description": "Coffee Shop", "amount": -6.75, "currency": "USD", "category": "Dining", "recipient": "Starbucks"},
        {"transaction_id": "txn005", "date": "2026-03-07", "description": "Transfer to Bob", "amount": -500.00, "currency": "USD", "category": "Transfer", "recipient": "Bob Smith"},
    ],
    "user2": [
        {"transaction_id": "txn101", "date": "2026-03-01", "description": "Rent Payment", "amount": -1800.00, "currency": "USD", "category": "Housing", "recipient": "Landlord LLC"},
        {"transaction_id": "txn102", "date": "2026-03-03", "description": "Freelance Payment", "amount": 4500.00, "currency": "USD", "category": "Income", "recipient": None},
        {"transaction_id": "txn103", "date": "2026-03-06", "description": "Transfer from Alice", "amount": 500.00, "currency": "USD", "category": "Transfer", "recipient": None},
    ],
}

# Mutable list to track submitted payments
MOCK_PAYMENTS = []
