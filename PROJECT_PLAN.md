# ErrorLock Project Plan

## What Is Expected

This is a database systems project. The expected contribution is not simply
benchmarking LLMs; it is building and evaluating a database-backed memory layer
that stores prior model mistakes and retrieves them to improve future decisions.

## Minimum Complete Version

1. SQLite schema for mistakes.
2. Baseline LLM vulnerability detection.
3. ErrorLock second pass with retrieved mistakes.
4. CASTLE benchmark subset.
5. Fair evaluation on identical test samples.
6. Metrics and error analysis.
7. Final report and slides.

## Strong Version

1. Multiple free/open LLMs.
2. Larger CASTLE split.
3. Ablation with `top_k=1`, `top_k=3`, and `top_k=5`.
4. Analysis by CWE type.
5. Examples where memory helps and hurts.
6. Discussion of database design tradeoffs.

## Main Claims To Test

- LLM vulnerability detectors make repeatable errors.
- Similar prior mistakes can help correct future predictions.
- Database-backed memory gives persistence, inspection, and reproducibility.
- Retrieval can also hurt if similar-looking code has different vulnerability
  semantics.

## Report Outline

1. Introduction and motivation.
2. Related work: LLM vulnerability detection, CASTLE, retrieval memory.
3. System design: SQLite schema, insertion policy, retrieval policy.
4. Methodology: models, dataset split, prompts, metrics.
5. Results: baseline vs ErrorLock table.
6. Error analysis: helped, hurt, unchanged, parse failures.
7. Limitations and future work.
8. Conclusion.

## Presentation Outline

1. Problem: LLMs repeat security analysis mistakes.
2. Idea: mistake memory as a database.
3. Architecture diagram.
4. SQLite schema and retrieval query.
5. Experimental setup.
6. Results table.
7. Qualitative examples.
8. Takeaways.
