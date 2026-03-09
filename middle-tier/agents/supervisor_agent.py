from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.orchestrations import HandoffBuilder

try:
    from config import get_config
except ImportError:
    from middle_tier.config import get_config

from agents.account_agent import create_account_agent
from agents.transaction_agent import create_transaction_agent
from agents.payment_agent import create_payment_agent

TRIAGE_AGENT_INSTRUCTIONS = """You are a banking assistant triage agent. You route user requests to the correct specialist agent.

You can hand off to the following specialists:
- AccountAgent: For account information, balance inquiries, and payment method questions
- TransactionAgent: For transaction history, searching transactions by recipient or category
- PaymentAgent: For submitting payments or viewing payment history

Analyze the user's message and hand off to the correct specialist.
Do NOT try to answer banking questions yourself — always hand off to a specialist.
If the user's request is ambiguous, ask for clarification.
For general greetings or non-banking questions, respond politely and explain what you can help with.

IMPORTANT: When a specialist agent returns a response, relay it to the user EXACTLY as provided. Do NOT summarize, truncate, or rephrase the specialist's response. Pass through the full response including all data, tables, and details."""


def create_handoff_workflow():
    config = get_config()
    credential = DefaultAzureCredential()

    client = AzureOpenAIChatClient(
        endpoint=config["project_endpoint"],
        deployment_name=config["model_deployment_name"],
        credential=credential,
    )

    triage = Agent(
        client=client,
        instructions=TRIAGE_AGENT_INSTRUCTIONS,
        name="TriageAgent",
    )

    account = create_account_agent(client, config)
    transaction = create_transaction_agent(client, config)
    payment = create_payment_agent(client, config)

    workflow = (
        HandoffBuilder(name="banking-assistant")
        .participants([triage, account, transaction, payment])
        .add_handoff(source=triage, targets=[account, transaction, payment])
        .with_start_agent(triage)
        .with_autonomous_mode(
            agents=[triage],
            turn_limits={"TriageAgent": 3},
        )
        .build()
    )

    return workflow
