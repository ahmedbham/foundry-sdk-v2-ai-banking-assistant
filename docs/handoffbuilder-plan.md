# Plan: Replace Supervisor with HandoffBuilder Orchestration

## TL;DR
Replace the current tool-based supervisor routing pattern (`@tool` functions that manually create/run sub-agents) with the MAF `HandoffBuilder` orchestration using autonomous mode. A **Triage Agent** acts as the entry point and hands off to specialist agents (Account, Transaction, Payment). Specialists hand back to Triage only (star topology). Synchronous responses, no checkpointing.

## Current Architecture
- **Supervisor Agent** has 3 `@tool`-decorated async functions that each instantiate a specialist agent, run it, and return text
- Each specialist agent uses `MCPStreamableHTTPTool` to call the backend MCP server
- `POST /chat` creates a supervisor, calls `agent.run()`, returns `response.text`

## Target Architecture
- **HandoffBuilder** wires a Triage Agent + 3 specialist agents into a workflow
- Triage has handoffs to all 3 specialists; specialists have handoff back to Triage only
- Autonomous mode enabled on all 4 agents so routing completes without user-in-the-loop
- `POST /chat` calls `workflow.run()` and iterates events to extract the final response

---

## Steps

### Phase 1: Refactor Specialist Agents (parallel)

**Step 1a** — Refactor `account_agent.py`
- Adjust factory function to accept a shared `AzureOpenAIChatClient` and config dict
- Keep current instructions + MCPStreamableHTTPTool wiring unchanged
- Must return an `Agent` instance (required by HandoffBuilder for cloning)

**Step 1b** — Refactor `transaction_agent.py` (parallel with 1a)
- Same pattern as account agent

**Step 1c** — Refactor `payment_agent.py` (parallel with 1a)
- Same pattern as account agent

### Phase 2: Replace Supervisor with Handoff Workflow (*depends on Phase 1*)

**Step 2** — Rewrite `supervisor_agent.py`
- Remove all `@tool`-decorated handler functions (`handle_account_query`, `handle_transaction_query`, `handle_payment_query`)
- Remove the `create_supervisor_agent()` function
- Create a **Triage Agent** (`Agent` with no tools, only routing instructions telling it which agents to hand off to)
- Create a new `create_handoff_workflow()` factory function that:
  1. Builds an `AzureOpenAIChatClient` (shared across all agents)
  2. Creates Triage + 3 specialist agents using their factory functions
  3. Builds the workflow via:
     ```python
     HandoffBuilder(name="banking-assistant")
       .participants([triage, account, transaction, payment])
       .add_handoff(source=triage, targets=[account, transaction, payment])
       .add_handoff(source=account, targets=[triage])
       .add_handoff(source=transaction, targets=[triage])
       .add_handoff(source=payment, targets=[triage])
       .with_start_agent(triage)
       .with_autonomous_mode(
           agents=[triage, account, transaction, payment],
           turn_limits={"TriageAgent": 10, "AccountAgent": 10, "TransactionAgent": 10, "PaymentAgent": 10}
       )
       .build()
     ```
  4. Returns the `Workflow` object
- Update Triage instructions to describe when to hand off to each specialist

### Phase 3: Update API Layer (*depends on Phase 2*)

**Step 3** — Update `middle-tier/main.py`
- Replace `create_supervisor_agent()` call with `create_handoff_workflow()`
- Change `agent.run(message)` to `workflow.run(message)` and iterate events to extract the final assistant response
- Keep the `[User ID: {user_id}]` prefix on messages

### Phase 4: Update Package Exports (*parallel with Phase 3*)

**Step 4** — Update `middle-tier/agents/__init__.py`
- Export `create_handoff_workflow` instead of `create_supervisor_agent`

### Phase 5: Dependency Check

**Step 5** — Verify `middle-tier/requirements.txt`
- Confirm `agent-framework[azure]>=0.1.0a1` includes `agent_framework_orchestrations` (HandoffBuilder lives there)
- If not, add `agent-framework-orchestrations` as explicit dependency

---

## Relevant Files

- `middle-tier/agents/supervisor_agent.py` — **Major rewrite**: remove tool routing, add HandoffBuilder workflow
- `middle-tier/agents/account_agent.py` — **Minor refactor**: accept shared client parameter
- `middle-tier/agents/transaction_agent.py` — **Minor refactor**: same
- `middle-tier/agents/payment_agent.py` — **Minor refactor**: same
- `middle-tier/agents/__init__.py` — **Update exports**
- `middle-tier/main.py` — **Update**: wire workflow, iterate events
- `middle-tier/config.py` — **No changes expected**
- `middle-tier/requirements.txt` — **Verify** orchestrations dependency

## Verification

1. Run `python -c "from agent_framework.orchestrations import HandoffBuilder"` to confirm package availability
2. Send account query ("What's my balance?") → verify AccountAgent handles via MCP
3. Send transaction query ("Show my transactions") → verify TransactionAgent handles
4. Send payment query ("Pay $50 to Bob") → verify PaymentAgent handles
5. Send ambiguous query → verify Triage routes appropriately
6. `GET /health` still returns 200
7. End-to-end via `docker-compose up` + frontend chat

## Decisions

- **Star topology**: Triage → specialists → Triage only (no cross-specialist handoffs)
- **Synchronous** `POST /chat` response (no SSE streaming changes)
- **No checkpointing**: each request is stateless
- **Shared LLM client** across all agents
- **Autonomous mode on all 4 agents**: ensures Triage → specialist → response completes without user-in-the-loop

## Further Considerations

1. **Turn limits** — Starting at 10 per agent. May need increasing if specialists require multiple MCP round-trips. Monitor for truncation.
2. **Error handling** — If a specialist fails (e.g., MCP unreachable), HandoffBuilder may surface errors differently than the current pattern. Test failure scenarios during verification.
