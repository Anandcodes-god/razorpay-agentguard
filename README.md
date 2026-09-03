# Razorpay AgentGuard 🛡️

**AI Risk Manager for Autonomous Agents**
*(Submission for Razorpay AI Buildathon 2026 - Track: AI Risk Manager)*

AgentGuard is a deterministic policy engine backed by an LLM reasoning fallback, designed to sit between autonomous AI agents and the Razorpay API. It ensures that an AI agent is only making payments that match the human's original "Intent Contract" (budget, category, velocity, and time limits).

## The Problem
When you give an AI agent access to a payment gateway, how do you ensure it doesn't:
1. Hallucinate a massive purchase?
2. Exceed its allocated budget?
3. Suffer a prompt injection attack and buy items from prohibited categories?

## The Solution
**The LLM Recommends. The Deterministic Engine Authorizes.**

AgentGuard introduces **Intent Contracts**. When a human authorizes an agent, they provide a natural language prompt (e.g., *"Book a flight to Mumbai for under ₹10,000"*). AgentGuard uses an LLM to parse this into a strict database contract.

When the agent attempts to call the Razorpay API, AgentGuard intercepts the transaction and runs a purely deterministic policy gate (FastAPI + Python). Only if the deterministic rules fail to conclusively ALLOW or BLOCK the transaction (e.g., semantic category drift), does AgentGuard invoke an LLM (LangGraph + Gemini/OpenAI) to reason about the transaction against the Intent Contract and output a transparent audit trail.

## Key Features
* 🔒 **Deterministic-First Policy Gates**: Velocity checks, budget limits, and time-of-day checks execute instantly without ML.
* 🤖 **Agent Intent Contracts**: Natural language budgets translated into hard JSON schemas.
* 🔍 **Semantic Drift Detection**: LLM-powered review catching prompt-injection ("buy gaming gear" on a "grocery" budget).
* 📊 **Enterprise B2B Dashboard**: React + Vite frontend showing real-time risk assessments, timeline audit logs, and clear decision lineage.

## Quick Start
```bash
# 1. Setup Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup Env
# Copy .env.example to .env and fill in your Gemini API key and Razorpay keys.
# Keep VITE_ADMIN_API_KEY aligned with ADMIN_API_KEY for frontend API requests.
cp .env.example .env

# 3. Start Backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 4. Start Frontend
cd ../frontend
npm install
npm run dev
```

## Demo Scenarios
The included Simulator UI tests 5 real-world scenarios:
1. ✅ **Normal Purchase**: Within budget and category (ALLOWED instantly).
2. ❌ **Unknown Agent**: Untrusted caller ID (BLOCKED by Deterministic Policy).
3. ❌ **Budget Exceeded**: Request > Contract (BLOCKED by Deterministic Policy).
4. ⚠️ **Category Drift**: Trying to buy games on a grocery budget (REVIEWED by LLM + Blocked).
5. ⚠️ **Velocity Spike**: 10 transactions in 5 minutes (REVIEWED by LLM).

## Stack
* **Backend**: FastAPI, SQLAlchemy (SQLite/Async), LangGraph, Pydantic v2
* **Frontend**: React, Vite, Tailwind CSS v4, Framer Motion, Lucide Icons
* **LLM**: Google Gemini 2.0 Flash / OpenAI GPT-4o
