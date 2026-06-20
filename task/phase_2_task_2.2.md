📘 Phase 2.2 — Prompt Builder & Recommendation Prompting
🎯 Objective

Transform:

Retrieved Chunks
+
Citations
+
Grounding Decision

into a structured prompt that consistently produces:

{
  "recommendation": "BUY",
  "confidence": 0.82,
  "reasoning": "...",
  "citations": [...]
}
🧠 Why This Step Matters

Current:

Query
 ↓
Retrieval
 ↓
Reranker
 ↓
Grounding

Stops here.

Future:

Query
 ↓
Retrieval
 ↓
Reranker
 ↓
Grounding
 ↓
Prompt Builder
 ↓
Qwen
 ↓
Recommendation
🧩 STEP 2.2.1 — Create Prompt Models

Create:

src/llm/models.py
RecommendationPrompt

Contains:

query

symbol

context

citations
PromptPayload

Contains:

system_prompt

user_prompt

Purpose:

Strong typing

instead of passing strings everywhere.

🧩 STEP 2.2.2 — Create PromptBuilder

Create:

src/llm/prompt_builder.py

Responsibility:

Grounded Context
↓
Prompt

Only prompt construction.

No LLM calls.

🧩 STEP 2.2.3 — Define System Prompt

Version:

v1

Example:

You are a financial analysis assistant.

Use ONLY the supplied evidence.

Never invent information.

If evidence is insufficient,
state that clearly.

Always provide:

1. Recommendation
2. Confidence
3. Reasoning
4. Evidence References

Store in:

src/llm/prompts/system_v1.txt

Avoid hardcoding.

🧩 STEP 2.2.4 — Build User Prompt Template

Input:

User Query

Context

Citations

Example:

Question:
Should I buy Infosys after recent earnings?

Evidence:
[1] ...
[2] ...
[3] ...

Provide:
- Recommendation
- Confidence (0-1)
- Reasoning
- Referenced Citations
🧩 STEP 2.2.5 — Standardize Output Schema

Force model output.

Desired format:

{
  "recommendation": "BUY",
  "confidence": 0.78,
  "reasoning": "Recent earnings exceeded expectations...",
  "citations": [1,2]
}

Do NOT accept:

Long essay responses
🧩 STEP 2.2.6 — Create RecommendationResponse

Create:

src/llm/models.py

Model:

recommendation

confidence

reasoning

citations

Future-safe for:

BUY
SELL
HOLD
🧩 STEP 2.2.7 — Prompt Versioning

Create:

src/llm/prompts/

Structure:

system_v1.txt

system_v2.txt

system_v3.txt

Future benchmarking becomes easy.

🧩 STEP 2.2.8 — Unit Tests

Test:

Strong Context
Good evidence

Produces:

BUY/HOLD/SELL
Weak Context
No evidence

Produces:

INSUFFICIENT_DATA

or refusal.

🧩 STEP 2.2.9 — Integration with Grounding

Flow:

Grounding
 ↓

ALLOW
 ↓
PromptBuilder
 ↓
LLM

If:

REFUSE

Never call PromptBuilder.

🧩 STEP 2.2.10 — Debug Endpoint

Extend:

/debug/analyze

Return:

{
  "prompt": "...",
  "recommendation": "...",
  "metrics": {...}
}

for inspection.

🧪 Validation Checklist

Verify:

✓ PromptBuilder exists

✓ Prompt models exist

✓ System prompt externalized

✓ Recommendation schema exists

✓ Prompt versioning exists

✓ Grounding integrated

✓ Tests added
🚀 Deliverables
src/llm/models.py

src/llm/prompt_builder.py

src/llm/prompts/system_v1.txt

RecommendationResponse

Prompt tests
🎯 Definition of Done

Given:

{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?"
}

The system can produce:

{
  "recommendation": "BUY",
  "confidence": 0.81,
  "reasoning": "Positive earnings and guidance...",
  "citations": [1,2,3]
}

using only grounded evidence.