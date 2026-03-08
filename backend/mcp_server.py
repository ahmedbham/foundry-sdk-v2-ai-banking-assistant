import httpx
from fastmcp import FastMCP

mcp = FastMCP("Banking MCP Server")

BACKEND_URL = "http://localhost:8000"


@mcp.tool()
def get_account_info(user_id: str) -> dict:
    """Get banking account information for a user, including name, account number, and account type."""
    response = httpx.get(f"{BACKEND_URL}/accounts/{user_id}")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_credit_balance(user_id: str) -> dict:
    """Get the current account balance and currency for a user."""
    response = httpx.get(f"{BACKEND_URL}/accounts/{user_id}/balance")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_payment_methods(user_id: str) -> dict:
    """Get registered payment methods for a user, such as debit cards, credit cards, and bank transfers."""
    response = httpx.get(f"{BACKEND_URL}/accounts/{user_id}/payment-methods")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8002)
