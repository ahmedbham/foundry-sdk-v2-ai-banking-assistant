from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient

TRANSACTION_AGENT_INSTRUCTIONS = """You are a banking transaction assistant. You help users with:
- Viewing their full transaction history
- Searching transactions by recipient name
- Searching transactions by category (e.g., Groceries, Utilities, Income, Dining, Transfer)

Always use the provided tools to fetch real data. Never make up transaction information.
When calling tools, use the user_id provided in the conversation context.
Present transaction data in a clear, organized format with dates and amounts."""


def create_transaction_agent(client: AzureOpenAIChatClient, config: dict) -> Agent:
    mcp_tool = MCPStreamableHTTPTool(
        name="banking-mcp",
        url=config["mcp_server_url"],
    )

    return Agent(
        client=client,
        instructions=TRANSACTION_AGENT_INSTRUCTIONS,
        name="TransactionAgent",
        tools=[mcp_tool],
    )
