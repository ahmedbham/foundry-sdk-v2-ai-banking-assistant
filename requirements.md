Objective
A banking personal assistant AI chat application to allow users to interact with their bank account information, transaction history, and payment functionalities. Utilizing the power of generative AI within a multi-agent architecture, this assistant aims to provide a seamless, conversational interface through which users can effortlessly access and manage their financial data.

Functional Architecture
Backend Tier
Backend Banking Services
Account Service: Support following functionality: banking account information, credit balance, and registered payment methods.

Transactions Service: Enables searching transactions and retrieving transactions by recipient.
Payments Service: to submit payments
Middle Tier
An AI chat API that allow frontend chat application to prompt using natural language and invoke appropriate backend banking services based on user intent
Frontend Tier
A chat UI that allow users to users to interact with their bank account information, transaction history, and payment functionalities.

Technical Architecture
Backend Tier
Mock REST APIs that expose appropriate operations/methods
Exposed as MCP endpoints using FastMCP to be consumed by AI agents
Middle Tier
A FastAPI app
Using Microsoft Foundry SDK v2 for agent runtime, orchestration and management
Account Agent that uses Account Services MCP tool
Transaction Agent that uses Transaction Services MCP tool
Payments Agent that uses Services Services MCP tool
Supervisor Agent: to triage the user request, and use the appropriate agent to handle the request, and also to handle the conversation flow
Frontend Tier
A react-based chat UI that allows users to ask banking questions and receive response from the backend

## General Technical Requirements
1. "incremental delivery pattern" to ensure individual components can be tested locally and in the Azure cloud.
2. If needed to use Microsoft Agent Framework:
   - To install the SDK in Python, use pip install agent-framework --pre.
   - Use the following code sample to create and run a simple agent:
```python
client = AzureAIAgentClient(
      project_endpoint=config["project_endpoint"],
      model_deployment_name=config["model_deployment_name"],
      credential=credential,
  )
  ```
3. use following code sampple to create Foundry Account using bicep:
```bicep
resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {...}
```
4. use following code sample to create GPT-4.1 deployment in the existing Foundry project using bicep:
```bicep    
@description('Existing Foundry account. The project will be created as a child resource of this account.')
resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' existing  = {
name: existingFoundryName

resource project 'projects' = {
  ...
  }
}
```
5. use following code sample to create GPT-4.1 deployment in the existing Foundry project using bicep
```bicep
  resource model 'deployments' = {
    name: 'agent-model'
    sku: {
      capacity: 1
      name: 'GlobalStandard' // Production readiness, use provisioned deployments with automatic spillover https://learn.microsoft.com/azure/ai-services/openai/how-to/spillover-traffic-management.
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: 'gpt-4.1'
        version: '2025-04-14'  // Use a model version available in your region.
      }
       raiPolicyName: 'Microsoft.DefaultV2'  // If this isn't strict enough for your use case, create a custom RAI policy.
    }
  }
}
```
6. Azure Container Apps (ACA) for compute hosting in Azure.
7. Azure Developer CLI (azd) for provioning and deployment. 
8. Github Actions workflows using azd for provisioning and deployment. 
9. docker compose for local testing. 