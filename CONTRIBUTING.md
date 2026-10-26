# Contributing to OpenCP

Thank you for your interest in improving the Open Cognitive Project Protocol!

## Core Principles
1. **Zero Fluff / Minimal Entropy**: Every token added to the standard must carry high information density. Avoid syntactic sugar that increases token footprint without semantic gain.
2. **Cross-Architecture Neutrality**: The specification must work identically across Claude, OpenAI, Gemini, Llama, DeepSeek, and custom agent runtimes.
3. **Deterministic Truth**: Invariants and verified assets must always take precedence over natural language explanations.

## Submitting Pull Requests
1. Ensure your example or specification update passes the CLI validator:
   ```bash
   python3 -m opencp validate examples/your-example.opencp
   ```
2. Keep all examples free of sensitive personal credentials, private keys, or actual proprietary tokens.
3. Open a Pull Request with a clear description of the entropy savings or structural improvement.
