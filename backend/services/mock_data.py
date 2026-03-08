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
