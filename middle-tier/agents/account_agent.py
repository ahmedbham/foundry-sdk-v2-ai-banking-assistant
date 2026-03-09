from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient

ACCOUNT_AGENT_INSTRUCTIONS = """You are a banking account assistant. You help users with:
- Viewing their account information (name, account number, account type)
- Checking their account balance
- Viewing their registered payment methods

Always use the provided tools to fetch real data. Never make up account information.
When calling tools, use the user_id provided in the conversation context.
Present financial information clearly and concisely."""


def create_account_agent(client: AzureOpenAIChatClient, config: dict) -> Agent:
    mcp_tool = MCPStreamableHTTPTool(
        name="banking-mcp",
        url=config["mcp_server_url"],
    )

    return Agent(
        client=client,
        instructions=ACCOUNT_AGENT_INSTRUCTIONS,
        name="AccountAgent",
        tools=[mcp_tool],
    )
