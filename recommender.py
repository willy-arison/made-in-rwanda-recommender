"""
Made in Rwanda Content Recommender (SBERT version)
Main recommender that that uses all-MiniLM-L6-v2 instead of TF-IDF.

all-MiniLM-L6-v2 is a small model from HuggingFace (22 million parameters).
It understands word meanings, not just exact words like TF-IDF.
This means it can match "leather boots" to "cowhide shoes" even though
they share no words.

Usage:
    python recommender.py --q "leather boots"
    python recommender.py --q "gift for wife"
    python recommender.py --q "cadeau en cuir pour femme" --top-k 5
"""

import argparse
import os
import sys
import warnings
from pathlib import Path

# Suppress all warnings (HF token warning, model load notes, etc.)
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Also suppress logging from the model itself
import logging
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("safetensors").setLevel(logging.ERROR)

# ---------- CONFIG ----------
DATA_DIR = Path(__file__).parent / "data"
LOCAL_BOOST_FACTOR = 0.10    # extra boost for local products
TOP_K_DEFAULT = 5
FAIRNESS_CAP = 0.15          # max 15% of top-10 for any single artisan
MODEL_NAME = "all-MiniLM-L6-v2"  # the HuggingFace model we use


class RwandaRecommenderSBERT:
    """
    Content-based recommender that uses all-MiniLM-L6-v2 from HuggingFace.
    This model understands word meanings, so it can match queries to products
    even when they use different words.

    Why this model?
    - Small (22 million parameters), runs on CPU
    - Understands synonyms: "leather" and "cowhide" are seen as related
    - Handles misspellings better than TF-IDF
    - Can match concepts like "gift for wife" to appropriate products
    """

    def __init__(self, catalog_path=None, click_log_path=None):
        """Load data, load the model, and create embeddings for all products."""
        self.catalog_path = catalog_path or (DATA_DIR / "catalog.csv")
        self.click_log_path = click_log_path or (DATA_DIR / "click_log.csv")

        # Load catalog
        print("Loading catalog...")
        self.catalog = pd.read_csv(self.catalog_path)
        print(f"   -> {len(self.catalog)} products loaded")

        # Load click log for popularity signals
        self.popularity = None
        if os.path.exists(self.click_log_path):
            print("Loading click data...")
            clicks = pd.read_csv(self.click_log_path)
            pop = clicks.groupby("sku").agg(
                total_clicks=("clicked", "sum"),
                total_conversions=("converted", "sum")
            ).reset_index()
            pop["popularity_score"] = (
                pop["total_clicks"] * 1.0 + pop["total_conversions"] * 3.0
            )
            self.popularity = pop.set_index("sku")["popularity_score"].to_dict()
            print(f"   -> {len(clicks)} click events processed")

        # Load the HuggingFace model
        print(f"Loading model: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        print("   Model loaded successfully")

        # Build embeddings for all products
        print("Creating product embeddings (this may take a moment)...")
        self._build_embeddings()
        print("   Ready!")

    def _build_embeddings(self):
        """
        Convert each product's text into an embedding (a list of numbers).
        The embedding captures the meaning of the text.
        We use the same search_text field as the TF-IDF version for fairness.
        """
        # Combine title, description, category, material, and district
        self.catalog["search_text"] = (
            self.catalog["title"].fillna("") + " " +
            self.catalog["description"].fillna("") + " " +
            self.catalog["category"].fillna("") + " " +
            self.catalog["material"].fillna("") + " " +
            self.catalog["origin_district"].fillna("")
        )

        # Convert all product texts to embeddings
        # Each embedding is a list of 384 numbers (the model output size)
        texts = self.catalog["search_text"].tolist()
        self.product_embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32  # process 32 products at a time
        )
        print(f"   Embedding shape: {self.product_embeddings.shape}")

    def recommend(self, query, top_k=TOP_K_DEFAULT):
        """
        Main recommendation function.

        1. Convert the query to an embedding using the same model
        2. Compute cosine similarity between query and all products
        3. Apply local boost (+0.10) to Rwandan products
        4. Add popularity boost from click data
        5. Apply fairness cap (no artisan takes more than 15% of top-10)
        6. Return top-k results
        """
        # Step 1: Convert query to embedding
        query_embedding = self.model.encode([query])

        # Step 2: Compute cosine similarity between query and all products
        similarities = cosine_similarity(query_embedding, self.product_embeddings).flatten()

        # Create results dataframe
        results = self.catalog.copy()
        results["similarity"] = similarities

        # Step 3: Local boost - add bonus to local products
        # Why +0.10? If the boost is too small (0.01) it changes nothing.
        # If too big (0.50) it shows bad matches. 0.10 is a middle ground
        # that helps local products when the match is close.
        results["boosted_score"] = results["similarity"].copy()
        local_mask = results["is_local"] == True
        results.loc[local_mask, "boosted_score"] += LOCAL_BOOST_FACTOR

        # Step 4: Add popularity boost if click data is available
        # Popular products get a small boost (0 to 0.05) based on clicks and sales
        if self.popularity:
            results["popularity"] = results["sku"].map(self.popularity).fillna(0)
            max_pop = results["popularity"].max()
            if max_pop > 0:
                results["popularity_norm"] = results["popularity"] / max_pop * 0.05
                results["boosted_score"] += results["popularity_norm"]
        else:
            results["popularity"] = 0

        # Step 5: Sort by boosted score
        results = results.sort_values("boosted_score", ascending=False)

        # Step 6: Apply fairness cap
        # No single artisan should take more than 15% of top-10 spots.
        # This makes sure many different artisans get seen.
        top_10 = results.head(10)
        artisan_counts = top_10["artisan_id"].value_counts()
        overrepresented = artisan_counts[artisan_counts > 10 * FAIRNESS_CAP].index

        if len(overrepresented) > 0:
            for artisan in overrepresented:
                excess = int(10 * FAIRNESS_CAP)
                artisan_mask = top_10["artisan_id"] == artisan
                artisan_items = top_10[artisan_mask].index
                if len(artisan_items) > excess:
                    penalize = artisan_items[excess:]
                    results.loc[penalize, "boosted_score"] -= 0.5

            # Re-sort after fairness adjustment
            results = results.sort_values("boosted_score", ascending=False)

        # Step 7: Return top-k results
        top_results = results.head(top_k).copy()

        output = []
        for idx, row in top_results.iterrows():
            output.append({
                "rank": len(output) + 1,
                "sku": row["sku"],
                "title": row["title"],
                "category": row["category"],
                "artisan": row["artisan_id"],
                "district": row["origin_district"],
                "price_rwf": int(row["price_rwf"]),
                "is_local": bool(row["is_local"]),
                "similarity_score": round(row["similarity"], 4),
                "boosted_score": round(row["boosted_score"], 4)
            })

        return output

    def get_local_presence_rate(self, queries_df, top_k=3):
        """
        Calculate local-presence rate:
        Percentage of queries with at least one local product in top-k results.
        """
        local_count = 0
        for _, row in queries_df.iterrows():
            results = self.recommend(row["query"], top_k=top_k)
            if any(r["is_local"] for r in results):
                local_count += 1

        rate = local_count / len(queries_df) * 100
        return rate


def format_results(results):
    """Format recommendation results for display."""
    lines = []
    lines.append(f"{'Rank':<6} {'SKU':<16} {'Product Title':<50} {'Price (RWF)':<14} {'Local?':<8} {'Score':<8}")
    lines.append("-" * 102)
    for r in results:
        local_tag = "YES" if r["is_local"] else "NO"
        title = r["title"][:48]
        lines.append(
            f"{r['rank']:<6} {r['sku']:<16} {title:<50} "
            f"{r['price_rwf']:<14,} {local_tag:<8} {r['boosted_score']:<8.4f}"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Made in Rwanda Content Recommender (SBERT version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recommender.py --q "leather boots"
  python recommender.py --q "gift for wife"
  python recommender.py --q "cadeau en cuir pour femme" --top-k 10
  python recommender.py --q "traditional basket" --top-k 3

Compare with TF-IDF version:
  python recommender.py --q "gift for wife"
  python recommender.py --q "gift for wife"

The SBERT version understands word meanings. "Gift for wife" will match
products even if they do not contain those exact words.
        """
    )
    parser.add_argument(
        "--q", "--query", type=str, required=True,
        help="Search query (e.g. 'leather boots')"
    )
    parser.add_argument(
        "--top-k", type=int, default=TOP_K_DEFAULT,
        help=f"Number of recommendations to return (default: {TOP_K_DEFAULT})"
    )
    parser.add_argument(
        "--catalog", type=str, default=None,
        help="Path to catalog CSV (default: data/catalog.csv)"
    )
    parser.add_argument(
        "--clicks", type=str, default=None,
        help="Path to click log CSV (default: data/click_log.csv)"
    )

    args = parser.parse_args()

    # Build the SBERT recommender
    recommender = RwandaRecommenderSBERT(
        catalog_path=args.catalog,
        click_log_path=args.clicks
    )

    # Get recommendations
    print(f"\nSearching for: \"{args.q}\"")
    print("=" * 80)
    results = recommender.recommend(args.q, top_k=args.top_k)

    if not results:
        print("No results found.")
        return

    print(format_results(results))

    # Summary
    local_count = sum(1 for r in results if r["is_local"])
    print(f"\nSummary: {local_count}/{len(results)} results are local products")


if __name__ == "__main__":
    main()
