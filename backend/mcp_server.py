import os

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Banking MCP Server")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


# ── Account tools ──

@mcp.tool()
async def get_account_info(user_id: str) -> dict:
    """Get banking account information for a user, including name, account number, and account type."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/accounts/{user_id}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_credit_balance(user_id: str) -> dict:
    """Get the current account balance and currency for a user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/accounts/{user_id}/balance")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_payment_methods(user_id: str) -> dict:
    """Get registered payment methods for a user, such as debit cards, credit cards, and bank transfers."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/accounts/{user_id}/payment-methods")
        response.raise_for_status()
        return response.json()


# ── Transaction tools ──

@mcp.tool()
async def get_transactions(user_id: str) -> dict:
    """Get the full transaction history for a user, including dates, descriptions, amounts, and categories."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/transactions/{user_id}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_transactions(user_id: str, recipient: str = "", category: str = "") -> dict:
    """Search a user's transactions by recipient name, category, or both. Leave a filter empty to skip it."""
    params = {}
    if recipient:
        params["recipient"] = recipient
    if category:
        params["category"] = category
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/transactions/{user_id}/search", params=params)
        response.raise_for_status()
        return response.json()


# ── Payment tools ──

@mcp.tool()
async def submit_payment(user_id: str, recipient: str, amount: float, currency: str = "USD", description: str = "") -> dict:
    """Submit a payment from the user's account to a recipient. Returns the payment confirmation with status."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/payments/{user_id}",
            json={"recipient": recipient, "amount": amount, "currency": currency, "description": description},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_payment_history(user_id: str) -> dict:
    """Get the history of all payments submitted by a user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/payments/{user_id}/history")
        response.raise_for_status()
        return response.json()
