# Process Log — Hour-by-Hour Timeline

**Challenge:** S2.T1.3 — 'Made in Rwanda' Content Recommender
**Candidate:** Willy Arison Andriambolamanana

---

## Timeline

| Time | Activity |
|------|----------|
| **0:00 - 0:30** | Read the challenge brief thoroughly. Understood requirements, deliverables, and scoring criteria. |
| **0:30 - 1:00** | Set up repository structure, created `requirements.txt`, and installed dependencies. |
| **1:00 - 1:30** | Built the synthetic data generator (`data/generator.py`) — catalog, queries, and click log. |
| **1:30 - 2:30** | Developed `recommender.py`: TF-IDF index, cosine similarity, local-boost rule, fairness cap, CLI interface. |
| **2:30 - 3:00** | Created `dispatcher.md` — the Product & Business artifact with weekly lead flow, SMS templates, unit economics, and 3-month pilot plan. |
| **3:00 - 3:30** | Built `eval.ipynb` — evaluation notebook with NDCG@5 and local-presence rate metrics. |
| **3:30 - 4:00** | Finalized `README.md`, `process_log.md`, `SIGNED.md`, and `LICENSE`. Tested the CLI. |

---

## LLM / Assistant Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Claude | Latest | Assisted with code structure, TF-IDF implementation, and documentation writing |
| Copilot | Latest | Code autocompletion in VSCode |

### 3 Sample Prompts Sent

1. *"Build a content-based recommender in Python using TF-IDF with a local-boost factor for Rwandan products."*
2. *"Design a weekly lead workflow for an artisan in Rwanda without a smartphone — include SMS template and cost estimates."*
3. *"Implement NDCG@5 evaluation metric for a recommendation system."*

### 1 Prompt Discarded (and why)

- *"Generate realistic Rwandan product catalog with 10,000 products"* — Discarded because the challenge spec says 400 products. Over-generating would be wasteful and not match the expected dataset size.

---

## Hardest Decision

The hardest decision was choosing **TF-IDF over sentence embeddings** (like Sentence-BERT). TF-IDF is faster (CPU-only constraint), simpler to deploy, and works well for keyword matching. However, it struggles with synonyms and code-switched queries (e.g., "sac en kitenge pas cher"). Sentence embeddings would handle those better but require more memory and are slower. For a Tier 1 challenge with a 250ms query-time limit, TF-IDF was the right call — speed and simplicity over perfect accuracy.
