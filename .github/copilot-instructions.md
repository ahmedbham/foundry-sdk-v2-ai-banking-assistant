# Technical Implementation Guide

This file contains code samples, import patterns, and specific technical constraints for the Banking Assistant project. See `docs/requirements.md` for high-level requirements and architecture.

---

## 1. Agent Framework SDK

- Install: `pip install agent-framework[azure] --pre`
- Azure client: `from agent_framework.azure import AzureOpenAIChatClient`
- HandoffBuilder: `from agent_framework.orchestrations import HandoffBuilder`
- Async credential: `from azure.identity.aio import DefaultAzureCredential`

### Creating an Agent with MCP tools

```python
from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient

credential = DefaultAzureCredential()
client = AzureOpenAIChatClient(
    endpoint=config["project_endpoint"],       # e.g. "https://cog-xxx.cognitiveservices.azure.com/"
    deployment_name=config["model_deployment_name"],  # e.g. "agent-model"
    credential=credential,
)
mcp_tool = MCPStreamableHTTPTool(
    name="banking-mcp",
    url=config["mcp_server_url"],              # e.g. "http://localhost:8000/mcp/mcp"
)
agent = Agent(
    client=client,
    instructions="...",
    name="AccountAgent",
    tools=[mcp_tool],
)
response = await agent.run("What is my balance?")
print(response.text)
```

### HandoffBuilder Workflow Pattern

# Build handoff workflow
workflow = (
    HandoffBuilder(name="banking-assistant")
    .participants([triage_agent, account_agent, transaction_agent, payment_agent])
    .add_handoff(source=triage_agent, targets=[account_agent, transaction_agent, payment_agent])
    .add_handoff(source=account_agent, targets=[triage_agent])
    .add_handoff(source=transaction_agent, targets=[triage_agent])
    .add_handoff(source=payment_agent, targets=[triage_agent])
    .with_start_agent(triage_agent)
    .with_autonomous_mode(
        agents=[triage_agent, account_agent, transaction_agent, payment_agent],
        turn_limits={"TriageAgent": 10, "AccountAgent": 10, "TransactionAgent": 10, "PaymentAgent": 10}
    )
    .build()
)

## 2. FastMCP Embedded in FastAPI

- FastMCP is embedded in the FastAPI backend, NOT run as a separate process.


## 10. Foundry & Model Deployment — Bicep

```bicep
resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
    name: foundryAccountName
    location: location
    kind: 'AIServices'
    identity: { type: 'SystemAssigned' }
    sku: { name: 'S0' }
    properties: {
        customSubDomainName: foundryAccountName
        publicNetworkAccess: 'Enabled'
        allowProjectManagement: true
    }

    resource project 'projects' = {
        name: foundryProjectName
        location: location
        identity: { type: 'SystemAssigned' }
        properties: {}
    }

    resource model 'deployments' = {
        name: 'agent-model'
        sku: {
            capacity: 10
            name: 'GlobalStandard'
        }
        properties: {
            model: {
                format: 'OpenAI'
                name: 'gpt-4.1'
                version: '2025-04-14'
            }
            raiPolicyName: 'Microsoft.DefaultV2'
        }
    }
}

output projectEndpoint string = foundry.properties.endpoint
```
## 11. Azure Developer CLI (azd)

- Use `remoteBuild: true` for all services — ACR builds the Docker images remotely (no need for local Docker).

---


