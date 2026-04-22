"""
Made in Rwanda Content Recommender
A content-based 'niche-first' recommender that nudges buyers toward local substitutes.

Usage:
    python recommender_tfidf.py --q "leather boots"
    python recommender_tfidf.py --q "cadeau en cuir pour femme" --top-k 5
"""

import argparse
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")

# ---------- CONFIG ----------
DATA_DIR = Path(__file__).parent / "data"
SIMILARITY_THRESHOLD = 0.15  # minimum similarity for a "good match"
LOCAL_BOOST_FACTOR = 0.10    # extra boost for local products
TOP_K_DEFAULT = 5
FAIRNESS_CAP = 0.15          # max 15% of top-10 for any single artisan


class RwandaContentRecommender:
    """
    Content-based recommender with local-boost for 'Made in Rwanda' products.
    Uses TF-IDF for efficient, CPU-friendly similarity computation.
    """

    def __init__(self, catalog_path=None, click_log_path=None):
        """Initialize the recommender: load data and build the TF-IDF index."""
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
            # Calculate popularity score (clicks + conversions)
            pop = clicks.groupby("sku").agg(
                total_clicks=("clicked", "sum"),
                total_conversions=("converted", "sum")
            ).reset_index()
            pop["popularity_score"] = (
                pop["total_clicks"] * 1.0 + pop["total_conversions"] * 3.0
            )
            self.popularity = pop.set_index("sku")["popularity_score"].to_dict()
            print(f"   -> {len(clicks)} click events processed")

        # Build TF-IDF index on product text
        print("Building TF-IDF index...")
        self._build_index()
        print("   Ready!")

    def _build_index(self):
        """Create TF-IDF vectors from product titles + descriptions."""
        # Combine title and description for richer text
        self.catalog["search_text"] = (
            self.catalog["title"].fillna("") + " " +
            self.catalog["description"].fillna("") + " " +
            self.catalog["category"].fillna("") + " " +
            self.catalog["material"].fillna("") + " " +
            self.catalog["origin_district"].fillna("")
        )

        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),  # unigrams + bigrams for better matching
            min_df=1
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(self.catalog["search_text"])
        print(f"   -> TF-IDF matrix shape: {self.tfidf_matrix.shape}")

    def recommend(self, query, top_k=TOP_K_DEFAULT):
        """
        Main recommendation function.
        1. Compute TF-IDF cosine similarity between query and all products.
        2. Apply local-boost: bump up Rwandan products.
        3. Apply fairness cap: limit any single artisan's share.
        4. Return top-k results.
        """
        # Step 1: Vectorize query and compute similarities
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Create results dataframe
        results = self.catalog.copy()
        results["similarity"] = similarities

        # Step 2: Local-boost - add bonus to local products
        results["boosted_score"] = results["similarity"].copy()
        local_mask = results["is_local"] == True
        results.loc[local_mask, "boosted_score"] += LOCAL_BOOST_FACTOR

        # Add popularity boost if available
        if self.popularity:
            results["popularity"] = results["sku"].map(self.popularity).fillna(0)
            # Normalize popularity to 0-0.05 range
            max_pop = results["popularity"].max()
            if max_pop > 0:
                results["popularity_norm"] = results["popularity"] / max_pop * 0.05
                results["boosted_score"] += results["popularity_norm"]
        else:
            results["popularity"] = 0

        # Step 3: Sort by boosted score
        results = results.sort_values("boosted_score", ascending=False)

        # Step 4: Apply fairness cap - no artisan > 15% of top-10
        top_10 = results.head(10)
        artisan_counts = top_10["artisan_id"].value_counts()
        overrepresented = artisan_counts[artisan_counts > 10 * FAIRNESS_CAP].index

        if len(overrepresented) > 0:
            # Demote excess products from overrepresented artisans
            for artisan in overrepresented:
                excess = int(10 * FAIRNESS_CAP)
                artisan_mask = top_10["artisan_id"] == artisan
                # Keep first 'excess' items, penalize the rest
                artisan_items = top_10[artisan_mask].index
                if len(artisan_items) > excess:
                    penalize = artisan_items[excess:]
                    results.loc[penalize, "boosted_score"] -= 0.5  # big penalty

            # Re-sort after fairness adjustment
            results = results.sort_values("boosted_score", ascending=False)

        # Step 5: Return top-k
        top_results = results.head(top_k).copy()

        # Build output
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
        description="Made in Rwanda Content Recommender",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recommender_tfidf.py --q "leather boots"
  python recommender_tfidf.py --q "cadeau en cuir pour femme" --top-k 10
  python recommender_tfidf.py --q "traditional basket" --top-k 3
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

    # Build recommender
    recommender = RwandaContentRecommender(
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
