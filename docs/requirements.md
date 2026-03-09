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
- Uses **HandoffBuilder** orchestration to route user requests to the correct specialist agent via handoffs (star topology with autonomous mode).

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
  - **Triage Agent + HandoffBuilder Workflow**: routes user requests to specialist agents using MAF `HandoffBuilder` orchestration with autonomous mode. The Triage Agent has no tools — only routing instructions. Specialists hand back to Triage only (star topology).
- **Port**: 8001

### Frontend Tier

- **Framework**: React 19 + Vite + TypeScript
- **Proxy**: nginx reverse proxy from `/api/` to the middle-tier
- **Port**: 80 (nginx) / 3000 (Vite dev server)

---

## Implementation Phases

Follow an incremental delivery pattern. Implement and test each phase before moving to the next.

## Technical Requirements & Constraints

> **Note:** Code samples, import patterns, and detailed technical configurations are in `.github/copilot-instructions.md`. This section provides high-level requirements only.

### 1. Agent Framework SDK

- SDK package: `agent-framework` (install with `pip install agent-framework[azure] --pre`)
- Uses `AzureOpenAIChatClient` with `DefaultAzureCredential` for Azure OpenAI access
- Specialist agents use `MCPStreamableHTTPTool` to call backend banking services
- **HandoffBuilder workflow**: The Triage Agent has no tools — only routing instructions. It hands off to specialist agents (Account, Transaction, Payment) which hand back to Triage (star topology). Autonomous mode is enabled on all agents with turn limits.
- The workflow handles all routing via handoffs, not `@tool` decorated functions

### 2. FastMCP Embedded in FastAPI

- FastMCP is embedded in the FastAPI backend, NOT run as a separate process
