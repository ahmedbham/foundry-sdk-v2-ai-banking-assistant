import os

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Banking MCP Server")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


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
