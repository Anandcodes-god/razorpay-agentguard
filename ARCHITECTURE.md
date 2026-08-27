# AgentGuard Architecture

## System Diagram

```mermaid
graph TD
    %% Core Entities
    Human[👤 Human Principal]
    Agent[🤖 Autonomous Agent]
    RZP[💳 Razorpay API]

    %% AgentGuard System
    subgraph AgentGuard Risk Controller
        API[⚡ FastAPI Gateway]
        Engine[🛡️ Deterministic Policy Engine]
        LLM[🧠 LangGraph Risk Assessor]
        DB[(SQLite / Intent Contracts)]
    end

    %% Flows
    Human -->|1. Natural Language Mandate| API
    API -->|2. Parses into strict limits| DB
    
    Agent -->|3. Attempt Payment| API
    API -->|4. Fetch history & contract| DB
    API -->|5. Run basic checks| Engine
    
    Engine -->|6a. Hard Pass| RZP
    Engine -->|6b. Hard Fail| API
    Engine -->|6c. Ambiguous / Anomaly| LLM
    
    LLM -->|7. Semantic reasoning & Audit| API
    API -->|8. Final Decision (Allow/Block)| RZP
```

## The "Defense in Depth" Philosophy

Many "AI Risk Managers" make the mistake of putting an LLM in the critical path of every transaction. This introduces massive latency, high costs, and non-deterministic failure modes (hallucinations).

AgentGuard uses a **layered architecture**:

### Layer 1: The Deterministic Engine (Speed < 50ms)
Pure Python `if/else` logic.
- Is the agent ID registered in the DB?
- Has the agent's authorization expired?
- Is the transaction amount strictly `> max_budget`?
- Are they making 50 requests a second? (Velocity check)

If any of these fail, the transaction is **BLOCKED** immediately. No LLM is ever called.

### Layer 2: The LLM Assessor (Speed < 2000ms)
Invoked *only* if Layer 1 returns a `REVIEW` status (e.g., the amount is fine, but the merchant category seems mismatched to the original human intent, or velocity is slightly anomalous).

We use **LangGraph** to construct a cyclical reasoning agent:
1. **Observe**: Fetch transaction history, merchant details, and the human's original Intent Contract.
2. **Reason**: Perform semantic analysis (e.g., "Is buying a Steam Gift Card allowed if the human said 'Buy weekly groceries'?").
3. **Decide**: Generate an exact `ALLOW` or `BLOCK` decision with a strict array of reasoning steps.

### Layer 3: The Audit Trail
Every decision, whether Deterministic or LLM-based, writes an `AuditLog` to the database with a `severity` and `step_number`. This provides a complete, 100% transparent lineage for the frontend UI to render the "Timeline", ensuring absolute observability for human compliance teams.
