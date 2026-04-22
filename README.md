# Made in Rwanda - Content Recommender

AIMS KTT Hackathon - S2.T1.3 - Tier 1

A content-based recommender that helps buyers discover local Rwandan products instead of international alternatives. Built for CPU-only, low-bandwidth environments, and designed with offline artisans in mind.

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd made_in_rwanda_repo

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate the data

```bash
python data/generator.py
```

This creates 3 files in the data folder:
- catalog.csv - 400 products (80% Rwandan, 20% foreign)
- queries.csv - 120 search queries in English, French, and mixed languages
- click_log.csv - 5,000 synthetic click events

### 3. Run the recommender

```bash
# English query
python recommender.py --q "leather boots"

# French query
python recommender.py --q "cadeau en cuir pour femme"

# Control number of results
python recommender.py --q "traditional basket" --top-k 10
```

## What is included

| File | Description |
|------|-------------|
| recommender.py | Main command-line tool with SBERT and local boost |
| recommender_tfidf.py | Alternative TF-IDF version |
| eval.ipynb | Evaluation notebook with NDCG@5 and local-presence rate |
| dispatcher.md | Business plan for artisans without smartphones |
| data/generator.py | Data generator that creates synthetic product data |
| requirements.txt | Python package dependencies |
| process_log.md | Development timeline and AI tool declarations |
| SIGNED.md | Signed honor code |
| LICENSE | MIT License |

## How the system works

1. User enters a search query (like "leather boots")
2. System converts query and products to numerical vectors using SBERT
3. Finds products most similar to the query
4. Adds +0.10 boost to Rwandan products (local boost)
5. Adds small bonus for popular products (from click data)
6. Applies fairness rule: no single artisan can dominate results
7. Returns top results with Rwandan products prioritized

## Why we use SBERT as the main model

We provide two models:

1. SBERT (recommender.py) - Main model:
   - Understands word meanings, not just exact words
   - Works with French queries (important for Rwanda)
   - Better for synonyms and mixed language
   - Semantic understanding improves matching quality

2. TF-IDF (recommender_tfidf.py) - Alternative:
   - Fast: runs in under 250ms on CPU
   - Simple: easy to understand and deploy
   - Works well for exact word matches
   - Limitation: struggles with French and synonyms

For Rwanda, we use SBERT as the main model because it handles French queries better.

## Performance results

Our evaluation shows:
- NDCG@5 score: 0.92 (excellent recommendation quality)
- Local-presence rate: 90% (9 out of 10 searches show Rwandan products)
- Query time: under 100ms

Run the evaluation notebook to see detailed results:
```bash
jupyter notebook eval.ipynb
```

## Business adaptation

See dispatcher.md for the complete business plan, including:

- Weekly SMS workflow for artisans without smartphones
- 3-month pilot plan for 20 artisans
- Cost estimates and break-even analysis
- Simple message templates for low-literacy users

## 4-Minute video submission

Video URL: https://drive.google.com/file/d/1-AH-VqkFEd4JgDGvJL-81qqfYgLhOV52/view?usp=drive_link

Video structure (4 minutes total):
- 0:00-0:30: Introduction with name, challenge ID, and scores
- 0:30-1:30: Code walkthrough of recommender.py (SBERT version)
- 1:30-2:30: Live demo with French query
- 2:30-3:30: Business plan explanation from dispatcher.md
- 3:30-4:00: Answers to 3 required questions

## Evaluation

To evaluate the system yourself:

1. Run the evaluation notebook:
```bash
jupyter notebook eval.ipynb
```

2. Or test individual queries:
```bash
python recommender.py --q "cadeau en cuir" --top-k 5
python recommender_tfidf.py --q "leather boots" --top-k 5
```

## License

MIT License - see LICENSE file.

## Acknowledgments

- AIMS KTT Fellowship for the challenge
- Inspired by real Rwandan artisans and cooperatives
- Data is synthetic but designed to reflect real market conditions
