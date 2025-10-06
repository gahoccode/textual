# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records documenting key architectural choices made during the development of Terminal Portfolio Optimizer.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help teams:
- Understand why decisions were made
- Avoid revisiting settled decisions
- Onboard new team members
- Learn from past choices

## Format

Each ADR follows this structure:
1. **Title**: Short noun phrase describing the decision
2. **Status**: Proposed, Accepted, Deprecated, Superseded
3. **Context**: Forces at play, constraints, requirements
4. **Decision**: What we decided to do
5. **Consequences**: Resulting context, positive and negative outcomes

## Index

### Core Architecture Decisions
- [ADR-0001: Use Multiprocessing for PyWebView](./0001-multiprocessing-for-webview.md) - **Accepted**
- [ADR-0002: Worker Thread Pattern for Blocking Operations](./0002-worker-thread-pattern.md) - **Accepted**
- [ADR-0003: Base64 Encoding for Subprocess Communication](./0003-base64-subprocess-communication.md) - **Accepted**

### Technology Choices
- [ADR-0004: Choose Textual for Terminal UI](./0004-textual-for-tui.md) - **Accepted**
- [ADR-0005: Use PyPortfolioOpt for Optimization](./0005-pyportfolioopt-for-optimization.md) - **Accepted**
- [ADR-0006: WebGL Rendering for Random Portfolios](./0006-webgl-for-performance.md) - **Accepted**

### Design Decisions
- [ADR-0007: Stateless Application Design](./0007-stateless-application.md) - **Accepted**
- [ADR-0008: Three Simultaneous Optimization Strategies](./0008-three-optimization-strategies.md) - **Accepted**

## Creating New ADRs

When making a significant architectural decision:

1. Create a new file: `NNNN-short-title.md` (incrementing number)
2. Use the template below
3. Discuss with team (if applicable)
4. Mark as **Accepted** when implemented
5. Update this index

### Template

```markdown
# ADR-NNNN: [Title]

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

**Date**: YYYY-MM-DD

**Deciders**: [Names or roles]

## Context

[Describe the forces at play, constraints, and requirements that led to this decision]

## Decision

[State the decision clearly and concisely]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Risks
- [Risk 1 and mitigation]

## Alternatives Considered

### Option 1: [Alternative name]
- Pros: [...]
- Cons: [...]
- Reason for rejection: [...]

### Option 2: [Alternative name]
- Pros: [...]
- Cons: [...]
- Reason for rejection: [...]

## References

- [Link to related documentation]
- [Link to technical discussion]
```
