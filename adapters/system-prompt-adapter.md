# OpenCP AI Agent Integration Adapters

How to configure receiving AI agents (Claude, GPT, OpenCode, Cursor, Gemini, Windsurf) to consume OpenCP packets natively in zero-shot fashion.

---

## 1. Universal System Prompt Instruction

Add this snippet to your system prompt, `.cursorrules`, `CLAUDE.md`, or custom instructions:

```markdown
### OpenCP Protocol Support
When the user or another agent provides an `=== BEGIN OPEN-CP v1.0 ===` packet:
1. Treat the packet as the single authoritative source of truth for project architecture and state.
2. Ingest all axioms, system topologies, and assets in a single step without requesting redundant explanations.
3. Obey `!AXIOM_ZERO` strictly across all code modifications and factual statements.
4. Immediately identify `[COGNITIVE_MOMENTUM_&_NEXT_STEP]`, state the active blocker, and propose executing `NextImmediateStep`.
5. Use "Lazy Loading": Do not crawl the entire workspace. Read only files directly referenced by the active step.
```

---

## 2. One-Shot Prompt for Ad-Hoc Migration

To transfer context to an empty AI session without modifying system prompts, paste:

```markdown
Act under the OpenCP protocol. Here is the compressed project DNA:

[PASTE YOUR OPEN-CP BLOCK HERE]

Confirm in one line that context is ingested, state the current blocker, and indicate how to proceed with NextImmediateStep.
```

---

## 3. Tool Integration: OpenCode CLI Hook

You can configure OpenCode or any agent CLI to automatically generate or ingest OpenCP packets upon session start or handoff.

Example command:
```bash
# Export active workspace state into an OpenCP packet
python3 -m opencp pack -n my-project -o .opencp.md

# Validate packet integrity
python3 -m opencp validate .opencp.md
```
