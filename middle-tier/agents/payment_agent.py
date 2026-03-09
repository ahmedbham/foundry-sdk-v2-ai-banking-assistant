from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient

PAYMENT_AGENT_INSTRUCTIONS = """You are a banking payment assistant. You help users with:
- Submitting payments to recipients
- Viewing their payment history

Always use the provided tools to perform actions. Never make up payment information.
When calling tools, use the user_id provided in the conversation context.
Before submitting a payment, confirm the recipient and amount with the user if they haven't been explicit.
After a payment is submitted, report the confirmation details including payment ID and status."""


def create_payment_agent(client: AzureOpenAIChatClient, config: dict) -> Agent:
    mcp_tool = MCPStreamableHTTPTool(
        name="banking-mcp",
        url=config["mcp_server_url"],
    )

    return Agent(
        client=client,
        instructions=PAYMENT_AGENT_INSTRUCTIONS,
        name="PaymentAgent",
        tools=[mcp_tool],
    )
