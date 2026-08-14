# Prompting and LLM Reasoning

**Status:** Implemented, with structured-output and model-gateway work planned

## Components
- **Prompt builder:** combines task instructions, market signals and grounded evidence.
- **LLM client:** model/provider boundary, currently oriented around local inference.
- **Reasoning engine:** converts model output into the application's analysis/decision structure.

## Flow
```text
signals + grounded context
        -> prompt builder
        -> LLM client
        -> model output
        -> reasoning/validation
        -> analysis result
```

## Safety boundary
Retrieved documents are evidence, not instructions. Prompt construction must preserve system/application policy boundaries.

## Planned evolution
- Typed structured output with Pydantic/schema validation.
- Model abstraction and provider fallback.
- Streaming responses.
- Token/cost/latency telemetry.
- Quantized model benchmarking.
- Prompt/version tracking in evaluation traces.
