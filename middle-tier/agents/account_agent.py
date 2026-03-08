import asyncio
import os

from azure.identity import DefaultAzureCredential
from agent_framework import AzureAIAgentClient

from config import get_config

ACCOUNT_AGENT_INSTRUCTIONS = """You are a banking account assistant. You help users with:
- Viewing their account information (name, account number, account type)
- Checking their account balance
- Viewing their registered payment methods

Always use the provided tools to fetch real data. Never make up account information.
When calling tools, use the user_id provided in the conversation context.
Present financial information clearly and concisely."""


async def create_account_agent():
    config = get_config()
    credential = DefaultAzureCredential()

    client = AzureAIAgentClient(
        project_endpoint=config["project_endpoint"],
        model_deployment_name=config["model_deployment_name"],
        credential=credential,
    )

    return client


if __name__ == "__main__":
    async def main():
        client = await create_account_agent()
        print(f"Account agent client created: {client}")

    asyncio.run(main())
