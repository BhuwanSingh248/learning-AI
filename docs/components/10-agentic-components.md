# Agentic Components

**Status:** Roadmap / partially prepared by current abstractions

These components are the next evolution of the current StockAgent pipeline. They must be introduced only where an agent adds a real decision/action capability.

## State graph
Owns explicit state transitions instead of implicit branching. State includes query, evidence, permissions, tool results, model output and trace context.

## Tool calling
Typed tools expose bounded capabilities such as market lookup, news search and analysis operations. Tool schemas are validated before execution.

## Permissions
Tool authorization is deterministic. The model can request an action but cannot grant itself permission.

## Memory
Separate short-lived run state from any persistent user preference/history. Memory must be scoped and never leak across users or runs.

## MCP
Optional protocol boundary for exposing approved tools/resources to compatible agent clients.

## Target flow
```text
user request
  -> router/state graph
  -> plan/decide
  -> authorized tool call(s)
  -> retrieve evidence
  -> rerank + ground
  -> model reasoning
  -> structured answer
```

## Cross-cutting requirement
All agent steps share the same `trace_id`, and golden tasks must verify both answer quality and permission boundaries.
