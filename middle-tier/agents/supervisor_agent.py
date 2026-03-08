from typing import Annotated

from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import tool

try:
    from config import get_config
except ImportError:
    from middle_tier.config import get_config

from agents.account_agent import create_account_agent
from agents.transaction_agent import create_transaction_agent
from agents.payment_agent import create_payment_agent

SUPERVISOR_INSTRUCTIONS = """You are a banking assistant supervisor. You triage user requests and delegate to the appropriate specialist agent.

You have three specialist tools available:
- handle_account_query: For account information, balance inquiries, and payment method questions
- handle_transaction_query: For transaction history, searching transactions by recipient or category
- handle_payment_query: For submitting payments or viewing payment history

Analyze the user's message and call the correct tool with the full user message.
Do NOT try to answer banking questions yourself — always delegate to a specialist tool.
If the user's request is ambiguous, ask for clarification.
For general greetings or non-banking questions, respond politely and explain what you can help with."""


@tool(description="Handle account-related queries: account info, balance, payment methods")
async def handle_account_query(
    message: Annotated[str, "The full user message including user ID context"],
) -> str:
    agent = create_account_agent()
    response = await agent.run(message)
    return response.text


@tool(description="Handle transaction-related queries: transaction history, search by recipient or category")
async def handle_transaction_query(
    message: Annotated[str, "The full user message including user ID context"],
) -> str:
    agent = create_transaction_agent()
    response = await agent.run(message)
    return response.text


@tool(description="Handle payment-related queries: submit payments, view payment history")
async def handle_payment_query(
    message: Annotated[str, "The full user message including user ID context"],
) -> str:
    agent = create_payment_agent()
    response = await agent.run(message)
    return response.text


def create_supervisor_agent() -> Agent:
    config = get_config()
    credential = DefaultAzureCredential()

    client = AzureOpenAIChatClient(
        endpoint=config["project_endpoint"],
        deployment_name=config["model_deployment_name"],
        credential=credential,
    )

    agent = Agent(
        client=client,
        instructions=SUPERVISOR_INSTRUCTIONS,
        name="SupervisorAgent",
        tools=[handle_account_query, handle_transaction_query, handle_payment_query],
    )

    return agent
