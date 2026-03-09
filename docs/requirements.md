# Banking Assistant — Implementation Requirements

## Objective

A banking personal assistant AI chat application to allow users to interact with their bank account information, transaction history, and payment functionalities. Utilizing the power of generative AI within a multi-agent architecture, this assistant aims to provide a seamless, conversational interface through which users can effortlessly access and manage their financial data.

---

## Functional Architecture

### Backend Tier — Banking Services

- **Account Service**: Account information, credit balance, and registered payment methods.
- **Transaction Service**: Transaction history and search by recipient and/or category.
- **Payment Service**: Submit payments and view payment history.

### Middle Tier — AI Agents

- An AI chat API that allows the frontend to prompt using natural language and invoke appropriate backend banking services based on user intent.
- Uses a **Supervisor Agent** to triage user requests and delegate to the correct specialist agent.

### Frontend Tier — Chat UI

- A React-based chat UI that allows users to interact with their bank account information, transaction history, and payment functionalities.

---

## Technical Architecture

### Backend Tier

- **Framework**: FastAPI
- **Mock REST APIs** with in-memory mock data (no database)
- **MCP Server**: FastMCP embedded in the FastAPI app, exposing banking tools for agents to consume
- **Port**: 8000

### Middle Tier

- **Framework**: FastAPI
- **Agent runtime**: `agent-framework` SDK (Microsoft Agent Framework, pre-release)
- **Agents**:
  - **Account Agent**: uses MCP tools for account info, balance, payment methods
  - **Transaction Agent**: uses MCP tools for transaction history and search
  - **Payment Agent**: uses MCP tools for payment submission and history
  - **Supervisor Agent**: triages user requests using `@tool` decorated async functions that delegate to sub-agents
- **Port**: 8001

### Frontend Tier

- **Framework**: React 19 + Vite + TypeScript
- **Proxy**: nginx reverse proxy from `/api/` to the middle-tier
- **Port**: 80 (nginx) / 3000 (Vite dev server)

---

## Implementation Phases

Follow an incremental delivery pattern. Implement and test each phase before moving to the next.

### Phase 1: Backend REST APIs + MCP Server

1. Create `backend/` with FastAPI app, mock data, and three service routers (account, transaction, payment).
2. Create FastMCP server with tools that call the REST APIs via `httpx`.
3. Mount the MCP server at `/mcp` path inside the FastAPI app.
4. Test: verify all REST endpoints return correct mock data on `http://localhost:8000`.

### Phase 2: Middle Tier — Account Agent (single agent)

1. Create `middle-tier/` with FastAPI app and `/chat` POST endpoint.
2. Create Account Agent using the agent framework with MCP tools.
3. Test: send a chat message asking about account balance and verify the agent returns correct data via MCP → backend.

### Phase 3: Full Multi-Agent Setup

1. Add Transaction Agent and Payment Agent (same pattern as Account Agent).
2. Add Supervisor Agent that routes to the correct sub-agent using `@tool` decorated functions.
3. Update `/chat` to use the Supervisor Agent.
4. Test: verify account, transaction, and payment queries all route correctly.

### Phase 4: Frontend Chat UI

1. Create `frontend/` with React 19 + Vite.
2. Implement chat UI with message list, input field, send button, loading state.
3. Configure Vite dev proxy (`/api` → `http://localhost:8001`).
4. Configure nginx for production (`/api/` → middle-tier).
5. Test: verify chat works end-to-end through the frontend.

### Phase 5: Infrastructure + Azure Deployment

1. Create Bicep modules for Foundry, ACR, and Container Apps.
2. Create `azure.yaml` for azd.
3. Create Dockerfiles for all three services.
4. Deploy with `azd up` and test in Azure.

### Phase 6: CI/CD

1. Create GitHub Actions workflow using azd for provisioning and deployment.

---

## Technical Requirements & Constraints

### 1. Agent Framework SDK

- Install: `pip install agent-framework[azure] --pre`
- The SDK package is `agent-framework`, NOT `agent_framework` or `azure-ai-agent`.
- Import names use underscores: `from agent_framework import Agent, MCPStreamableHTTPTool, tool`
- Azure client: `from agent_framework.azure import AzureOpenAIChatClient`
- Async credential: `from azure.identity.aio import DefaultAzureCredential`

**Creating an Agent with MCP tools:**
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

**Supervisor Agent pattern using `@tool` decorated functions:**
```python
from typing import Annotated
from agent_framework import Agent, tool

@tool(description="Handle account-related queries")
async def handle_account_query(
    message: Annotated[str, "The full user message including user ID context"],
) -> str:
    agent = create_account_agent()
    response = await agent.run(message)
    return response.text

# Same pattern for handle_transaction_query and handle_payment_query

agent = Agent(
    client=client,
    instructions="...",
    name="SupervisorAgent",
    tools=[handle_account_query, handle_transaction_query, handle_payment_query],
)
```

- The supervisor agent does NOT use MCPStreamableHTTPTool directly — only the sub-agents do.
- Each `@tool` function creates a sub-agent, runs it, and returns `response.text`.

### 2. FastMCP Embedded in FastAPI

- FastMCP is embedded in the FastAPI backend, NOT run as a separate process.
- The MCP app is mounted at `/mcp`, making the actual MCP endpoint URL `/mcp/mcp` (FastMCP adds its own `/mcp` path).
- The MCP app requires a lifespan context. Wire it like this:

```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP

mcp = FastMCP("Banking MCP Server")
mcp_app = mcp.http_app(transport="streamable-http")

@asynccontextmanager
async def lifespan(app):
    async with mcp_app.router.lifespan_context(app):
        yield

app = FastAPI(title="Banking Backend Services", lifespan=lifespan)
app.mount("/mcp", mcp_app)
```

- MCP tools call the REST API via `httpx.AsyncClient` using `BACKEND_URL` env var (default: `http://localhost:8000`).
- When running locally, the MCP server calls the same FastAPI process via HTTP loopback.

### 3. Backend Import Pattern

The backend must support being run both as `uvicorn main:app` (from within `backend/`) and `uvicorn backend.main:app` (from workspace root). Use a try/except import pattern:

```python
try:
    from backend.services.account_service import router as account_router
    from backend.mcp_server import mcp
except ImportError:
    from services.account_service import router as account_router
    from mcp_server import mcp
```

The same pattern applies in `mcp_server.py` if it imports from `services/`.

### 4. Middle-Tier Import Pattern

Same try/except for middle-tier config:

```python
try:
    from config import get_config
except ImportError:
    from middle_tier.config import get_config
```

### 5. Middle-Tier Configuration

Use a `config.py` module that reads environment variables:

```python
def get_config() -> dict:
    return {
        "project_endpoint": os.environ.get("PROJECT_ENDPOINT", ""),
        "model_deployment_name": os.environ.get("MODEL_DEPLOYMENT_NAME", "agent-model"),
        "backend_url": os.environ.get("BACKEND_URL", "http://localhost:8000"),
        "mcp_server_url": os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp/mcp"),
    }
```

### 6. Frontend nginx Proxy — Critical Requirements

The nginx config MUST include these directives for Azure Container Apps compatibility:

```nginx
location /api/ {
    proxy_pass http://${MIDDLE_TIER_HOST}/;
    proxy_http_version 1.1;
    proxy_set_header Host ${MIDDLE_TIER_HOST};
    proxy_set_header X-Real-IP $remote_addr;
}
```

**Critical gotchas:**
- **`proxy_http_version 1.1;` is REQUIRED.** Without it, nginx defaults to HTTP/1.0 for upstream connections. Azure Container Apps internal ingress returns HTTP 426 "Upgrade Required" when receiving HTTP/1.0 requests.
- **`Host` header must be set to `${MIDDLE_TIER_HOST}`** (the internal FQDN of the middle-tier container app), NOT `$host` (which would be the frontend's own hostname). Container Apps routing requires the correct Host header.
- The nginx.conf file must be copied to `/etc/nginx/templates/default.conf.template` (not `/etc/nginx/conf.d/default.conf`) so that nginx's built-in `envsubst` mechanism resolves the `${MIDDLE_TIER_HOST}` variable on container startup.
- Set `ENV MIDDLE_TIER_HOST=middle-tier:8001` as default in the Dockerfile (used by docker-compose); Azure overrides this via Container Apps env vars.

### 7. Frontend Vite Dev Proxy

For local development, Vite proxies `/api` to the middle-tier:

```typescript
server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
},
```

The frontend sends requests to `/api/chat`, which is rewritten to `/chat` and forwarded to the middle-tier.

### 8. Dockerfiles

**Backend Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Middle-Tier Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80
ENV MIDDLE_TIER_HOST=middle-tier:8001
CMD ["nginx", "-g", "daemon off;"]
```

- **Frontend nginx.conf MUST be copied to `/etc/nginx/templates/default.conf.template`** — NOT to `/etc/nginx/conf.d/default.conf`. The `nginx:alpine` image has built-in entrypoint support for envsubst on files in `/etc/nginx/templates/`.

### 9. Azure Container Apps — Bicep Configuration

**Middle-tier ingress MUST have:**
```bicep
ingress: {
    external: false
    targetPort: 8001
    allowInsecure: true
    transport: 'http'
}
```

- **`transport: 'http'`** forces HTTP/1.1. Without this, Container Apps defaults to `Auto` which may negotiate HTTP/2 and cause 426 errors from upstream clients (like nginx) that use HTTP/1.1.
- **`allowInsecure: true`** allows HTTP traffic within the Container Apps Environment. Internal apps in the same environment communicate via HTTP, not HTTPS.

**Backend ingress:**
```bicep
ingress: {
    external: false
    targetPort: 8000
}
```

**Frontend ingress:**
```bicep
ingress: {
    external: true
    targetPort: 80
}
```

**Environment variables for middle-tier:**
```bicep
env: [
    { name: 'PROJECT_ENDPOINT', value: projectEndpoint }
    { name: 'MODEL_DEPLOYMENT_NAME', value: 'agent-model' }
    { name: 'BACKEND_URL', value: 'https://${backend.properties.configuration.ingress.fqdn}' }
    { name: 'MCP_SERVER_URL', value: 'https://${backend.properties.configuration.ingress.fqdn}/mcp/mcp' }
]
```

- Backend URL uses `https://` because internal-to-internal Container Apps traffic uses HTTPS by default (TLS is terminated at the ingress).

**Environment variable for frontend:**
```bicep
env: [
    { name: 'MIDDLE_TIER_HOST', value: '${middleTier.properties.configuration.ingress.fqdn}' }
]
```

- Do NOT prefix with `https://` — this is used in nginx `proxy_pass http://${MIDDLE_TIER_HOST}/` since we set `allowInsecure: true` and `transport: 'http'` on the middle-tier.

**Managed Identity for Azure OpenAI access:**
```bicep
identity: {
    type: 'SystemAssigned'
}
```

- The middle-tier container app MUST have a SystemAssigned managed identity.
- Assign the `Cognitive Services OpenAI User` role (GUID: `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd`) on the Foundry account resource:

```bicep
resource middleTierCognitiveServicesRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(middleTier.id, foundryAccount.id, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
    scope: foundryAccount
    properties: {
        principalId: middleTier.identity.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionId: subscriptionResourceId(
            'Microsoft.Authorization/roleDefinitions',
            '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
        )
    }
}
```

### 10. Foundry & Model Deployment — Bicep

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

- **Set model deployment capacity to at least 10.** The supervisor agent pattern makes ~4 LLM calls per user request (supervisor triage + sub-agent tool call + sub-agent response + supervisor final). Capacity of 1 causes 429 rate limit errors.
- The output endpoint is `foundry.properties.endpoint` (NOT the project endpoint — they are the same for this resource structure).

### 11. Azure Developer CLI (azd)

**azure.yaml:**
```yaml
name: foundry-sdk-v2-ai-banking-assistant
metadata:
    template: foundry-sdk-v2-ai-banking-assistant
services:
    backend:
        project: ./backend
        host: containerapp
        language: python
        docker:
            remoteBuild: true
    middle-tier:
        project: ./middle-tier
        host: containerapp
        language: python
        docker:
            remoteBuild: true
    frontend:
        project: ./frontend
        host: containerapp
        language: js
        docker:
            remoteBuild: true
infra:
    provider: bicep
    path: ./infra
```

- Use `remoteBuild: true` for all services — ACR builds the Docker images remotely (no need for local Docker).
- Use placeholder images (e.g., `mcr.microsoft.com/azurelinux/base/nginx:1.25`) in Bicep for initial provisioning. azd replaces them with real images during deploy.

### 12. Docker Compose for Local Testing

```yaml
services:
    backend:
        build: ./backend
        ports:
            - "8000:8000"
    middle-tier:
        build: ./middle-tier
        ports:
            - "8001:8001"
        environment:
            - BACKEND_URL=http://backend:8000
            - MCP_SERVER_URL=http://backend:8000/mcp/mcp
            - PROJECT_ENDPOINT=${PROJECT_ENDPOINT:-}
            - MODEL_DEPLOYMENT_NAME=${MODEL_DEPLOYMENT_NAME:-agent-model}
        depends_on:
            - backend
    frontend:
        build: ./frontend
        ports:
            - "3000:80"
        depends_on:
            - middle-tier
```

### 13. Local Development (without Docker)

Run each tier separately:

```bash
# Terminal 1: Backend (from workspace root)
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Middle-tier (set env vars first)
export PROJECT_ENDPOINT="https://<foundry-account>.cognitiveservices.azure.com/"
export MCP_SERVER_URL="http://localhost:8000/mcp/mcp"
cd middle-tier
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3: Frontend
cd frontend
npm run dev
```

### 14. GitHub Actions CI/CD

```yaml
name: Deploy to Azure
on:
    push:
        branches: [main]
    workflow_dispatch:
permissions:
    id-token: write
    contents: read
jobs:
    deploy:
        runs-on: ubuntu-latest
        env:
            AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
            AZURE_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
            AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
            AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
            AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
        steps:
            - uses: actions/checkout@v4
            - uses: azure/setup-azd@v2
            - name: Log in with Azure (federated credentials)
              run: |
                  azd auth login `
                    --client-id "$Env:AZURE_CLIENT_ID" `
                    --federated-credential-provider "github" `
                    --tenant-id "$Env:AZURE_TENANT_ID"
              shell: pwsh
            - name: Provision and deploy
              run: azd up --no-prompt
              env:
                  AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
                  AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
                  AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

### 15. Python Dependencies

**backend/requirements.txt:**
```
fastapi>=0.115.0
uvicorn>=0.30.0
fastmcp>=2.0.0
httpx>=0.27.0
```

**middle-tier/requirements.txt:**
```
fastapi>=0.115.0
uvicorn>=0.30.0
httpx>=0.27.0
sse-starlette>=2.0.0
agent-framework[azure]>=0.1.0a1
azure-identity[aio]>=1.17.0
```

- `sse-starlette` is required by agent-framework for streaming responses.
- `azure-identity[aio]` is needed for async `DefaultAzureCredential`.

---

## Common Pitfalls to Avoid

1. **MCP endpoint URL is `/mcp/mcp`**, not `/mcp`. FastMCP adds its own `/mcp` path when mounted.
2. **Model capacity must be >= 10.** The multi-agent supervisor pattern makes ~4 LLM calls per user request. Capacity of 1 will cause 429 rate limit errors.
3. **nginx `proxy_http_version 1.1;` is mandatory** in the nginx.conf `/api/` location block. Without it, Azure Container Apps returns 426 "Upgrade Required".
4. **nginx `Host` header must be `${MIDDLE_TIER_HOST}`**, not `$host`. Container Apps requires the correct destination hostname.
5. **nginx.conf goes to `/etc/nginx/templates/default.conf.template`** in the Dockerfile for envsubst to work. NOT `/etc/nginx/conf.d/default.conf`.
6. **Middle-tier needs `SystemAssigned` managed identity** + `Cognitive Services OpenAI User` role on the Foundry account for Azure OpenAI access.
7. **Middle-tier ingress needs `allowInsecure: true` and `transport: 'http'`** to accept HTTP/1.1 traffic from the frontend nginx proxy within the same Container Apps Environment.
8. **Backend URL from middle-tier uses `https://`** (Container Apps internal TLS), but `MIDDLE_TIER_HOST` for frontend uses bare hostname (nginx proxies over HTTP since `allowInsecure: true`).
9. **Use `remoteBuild: true`** in azure.yaml to avoid local Docker build/push issues.
10. **Use placeholder images** in Bicep container definitions (e.g., `mcr.microsoft.com/azurelinux/base/nginx:1.25`). azd replaces them during deploy.