"""
Synthetic Data Generator for 'Made in Rwanda' Content Recommender
Generates catalog, queries, and click log as described in the challenge brief.
Reproducible - run this to regenerate all data files in under 2 minutes.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import random

# ---------- CONFIG ----------
RANDOM_SEED = 42
N_PRODUCTS = 400
N_FOREIGN = 100    # how many foreign (non-Rwandan) products to add
N_QUERIES = 120
N_CLICKS = 5000

OUTPUT_DIR = Path(__file__).parent

# ---------- REAL RWANDAN DATA ----------
DISTRICTS = [
    "Gasabo", "Kicukiro", "Nyarugenge", "Nyamirambo",
    "Huye", "Musanze", "Rubavu", "Rusizi", "Nyagatare", "Gisenyi"
]

CATEGORIES = ["apparel", "leather", "basketry", "jewellery", "home-decor"]

MATERIALS = {
    "apparel": ["cotton", "kitenge", "linen", "polyester", "silk"],
    "leather": ["cowhide", "goatskin", "sheepskin", "genuine-leather"],
    "basketry": ["sisal", "papyrus", "banana-fibre", "raffia", "bamboo"],
    "jewellery": ["beads", "brass", "silver", "wood", "bone"],
    "home-decor": ["wood", "clay", "metal", "fabric", "stone"]
}

ARTISAN_NAMES = [
    "Dushime Leather", "Kigali Leather", "Rwanda Basket Co-op", "Nyamiramo Crafts",
    "Gorilla Arts", "Igihozo Stitches", "Urugo Decor", "Agaseke Weavers",
    "Inshuti Artisans", "Mountain Gold Jewellery", "Ishema Fashion",
    "Ubumuntu Designs", "Kirehe Pottery", "Virunga Textiles", "Baho Baskets"
]

RWANDAN_BRANDS = [
    "Kigali Leather", "Agaseke Weavers", "Mountain Gold Jewellery",
    "Ishema Fashion", "Baho Baskets", "Igihozo Stitches",
    "Urugo Decor", "Inshuti Artisans", "Ubumuntu Designs", "Gorilla Arts"
]

PRODUCT_TEMPLATES = {
    "apparel": [
        "{} {} {} shirt", "{} {} dress", "{} {} trousers",
        "{} {} jacket", "{} traditional {} robe"
    ],
    "leather": [
        "{} {} leather bag", "{} {} leather wallet",
        "{} {} leather belt", "{} {} leather shoes",
        "{} {} leather jacket"
    ],
    "basketry": [
        "{} {} basket", "{} {} woven bowl",
        "{} {} storage basket", "{} {} gift basket",
        "{} {} wall decoration"
    ],
    "jewellery": [
        "{} {} necklace", "{} {} bracelet",
        "{} {} earrings", "{} {} anklet",
        "{} {} ring set"
    ],
    "home-decor": [
        "{} {} vase", "{} {} candle holder",
        "{} {} wall art", "{} {} table mat",
        "{} {} throw pillow"
    ]
}

DESCRIPTION_TEMPLATES = {
    "apparel": "Handmade {} {} apparel made from {} by artisans in {}. Perfect for casual and formal wear.",
    "leather": "Premium {} {} leather product, handcrafted in {} using traditional techniques.",
    "basketry": "Beautiful {} {} basket handwoven by skilled artisans in {} using {}.",
    "jewellery": "Elegant {} {} jewellery piece, handcrafted by {} artisans from {}.",
    "home-decor": "Unique {} {} home decor item, handmade in {} with {}."
}

QUERY_TEMPLATES = [
    # English queries
    ("leather boots", "en"),
    ("gift for wife", "en"),
    ("handmade bag", "en"),
    ("traditional basket", "en"),
    ("Rwandan souvenirs", "en"),
    ("wedding gift", "en"),
    ("home decoration", "en"),
    ("men's wallet", "en"),
    ("women's dress", "en"),
    ("leather belt", "en"),
    ("wooden sculpture", "en"),
    ("beaded necklace", "en"),
    ("coffee table decor", "en"),
    ("birthday present", "en"),
    ("artisan crafts", "en"),
    ("fashion accessories", "en"),
    ("leather shoes", "en"),
    ("woven baskets", "en"),
    ("kitenge fabric", "en"),
    ("African prints", "en"),
    ("bracelet for men", "en"),
    ("earrings gold", "en"),
    ("shoulder bag", "en"),
    ("wall hanging", "en"),
    ("storage baskets", "en"),
    ("formal shirt", "en"),
    ("summer dress", "en"),
    ("leather journal", "en"),
    ("handbag cheap", "en"),
    ("quality crafts", "en"),
    # French queries
    ("cadeau en cuir", "fr"),
    ("sac à main femme", "fr"),
    ("panier traditionnel", "fr"),
    ("décor maison", "fr"),
    ("bijoux artisanaux", "fr"),
    ("ceinture en cuir", "fr"),
    ("robe africaine", "fr"),
    ("chaussures en cuir", "fr"),
    ("collier perles", "fr"),
    ("portefeuille homme", "fr"),
    ("boucles d'oreilles", "fr"),
    ("artisanat rwandais", "fr"),
    ("vannerie traditionnelle", "fr"),
    ("tissu kitenge", "fr"),
    ("souvenir du Rwanda", "fr"),
    ("tableau mural", "fr"),
    ("vêtements africains", "fr"),
    ("bracelet cuir", "fr"),
    ("poterie décorative", "fr"),
    ("linge de maison", "fr"),
    # Code-switched queries
    ("sac en kitenge pas cher", "mix"),
    ("traditional igitenge dress", "mix"),
    ("agaseke basket prix", "mix"),
    ("cadeau umuhungu", "mix"),
    ("beaded necklace rwandais", "mix"),
    ("leather agatagara", "mix"),
    ("custom imishanana", "mix"),
    ("basket dekorasi", "mix"),
    ("imikenyero shoes", "mix"),
    ("Rwanda craft cadeau", "mix"),
    # Misspellings
    ("lether boots", "en-misspelled"),
    ("hand made bag", "en-misspelled"),
    ("tradishional basket", "en-misspelled"),
    ("souvineer", "en-misspelled"),
    ("birfday gift", "en-misspelled"),
    ("accesories", "en-misspelled"),
    ("wallat", "en-misspelled"),
    ("neclace", "en-misspelled"),
    ("earings", "en-misspelled"),
    ("bracelett", "en-misspelled"),
    ("cado en cuir", "fr-misspelled"),
    ("panier main", "fr-misspelled"),
    ("decorasion maison", "fr-misspelled"),
    ("bijou fait main", "fr-misspelled"),
    ("chaussure cuire", "fr-misspelled"),
]

GLOBAL_BRANDS = [
    "Amazon Basics", "Zara", "H&M", "Nike", "Adidas",
    "Levi's", "Mango", "Forever 21", "Shein", "Walmart"
]

# Foreign (non-Rwandan) countries
FOREIGN_COUNTRIES = [
    "China", "India", "Kenya", "Uganda", "Ethiopia",
    "Tanzania", "Nigeria", "Dubai", "Bangladesh", "Vietnam"
]

FOREIGN_MATERIALS = {
    "apparel": ["polyester", "cotton", "nylon", "denim", "acrylic"],
    "leather": ["synthetic-leather", "cowhide", "faux-leather"],
    "basketry": ["plastic", "rattan", "seagrass", "bamboo"],
    "jewellery": ["plastic", "gold-plated", "silver-plated", "glass", "cubic-zirconia"],
    "home-decor": ["plastic", "MDF", "glass", "ceramic", "metal"]
}

FOREIGN_PRODUCT_TEMPLATES = {
    "apparel": [
        "{} {} {} shirt", "{} {} dress", "{} {} trousers",
        "{} {} jacket"
    ],
    "leather": [
        "{} {} leather bag", "{} {} leather wallet",
        "{} {} leather belt", "{} {} leather shoes",
        "{} {} leather jacket"
    ],
    "basketry": [
        "{} {} basket", "{} {} woven bowl",
        "{} {} storage basket", "{} {} gift basket"
    ],
    "jewellery": [
        "{} {} necklace", "{} {} bracelet",
        "{} {} earrings", "{} {} anklet",
        "{} {} ring set"
    ],
    "home-decor": [
        "{} {} vase", "{} {} candle holder",
        "{} {} wall art", "{} {} table mat"
    ]
}

FOREIGN_DESCRIPTION_TEMPLATES = {
    "apparel": "Imported {} {} from {}. Made with {} for everyday wear.",
    "leather": "Imported {} {} leather product from {}. Made with {}.",
    "basketry": "Imported {} {} from {}. Woven with {}.",
    "jewellery": "Imported {} {} jewellery from {}. Made with {}.",
    "home-decor": "Imported {} {} home decor from {}. Made with {}."
}

# ---------- GENERATOR ----------

def generate_catalog(seed=RANDOM_SEED):
    """Generate synthetic product catalog with local and foreign products."""
    rng = np.random.default_rng(seed)
    random.seed(seed)

    products = []
    sku_counter = 0

    # --- Make local Rwandan products ---
    for i in range(N_PRODUCTS):
        sku_counter += 1
        cat = rng.choice(CATEGORIES)
        district = rng.choice(DISTRICTS)
        material = rng.choice(MATERIALS[cat])
        artisan = rng.choice(ARTISAN_NAMES)

        # Price ranges by category
        price_ranges = {
            "apparel": (5000, 35000),
            "leather": (15000, 80000),
            "basketry": (3000, 25000),
            "jewellery": (5000, 50000),
            "home-decor": (7000, 45000)
        }
        price = int(rng.integers(*price_ranges[cat]))

        title_template = rng.choice(PRODUCT_TEMPLATES[cat])
        adj = rng.choice(["handmade", "premium", "traditional", "artisan", "modern"])
        title = title_template.format(adj, material, cat)
        title = title.replace("  ", " ").strip()

        desc_template = DESCRIPTION_TEMPLATES[cat]
        description = desc_template.format(adj, material, district, material)
        description = description.replace("  ", " ").strip()

        products.append({
            "sku": f"RW-{cat[:3].upper()}-{sku_counter:04d}",
            "title": title,
            "description": description,
            "category": cat,
            "material": material,
            "origin_district": district,
            "price_rwf": price,
            "artisan_id": f"ART-{random.randint(100, 999)}",
            "is_local": True
        })

    # --- Make foreign (non-Rwandan) products ---
    for i in range(N_FOREIGN):
        sku_counter += 1
        cat = rng.choice(CATEGORIES)
        country = rng.choice(FOREIGN_COUNTRIES)
        material = rng.choice(FOREIGN_MATERIALS[cat])
        brand = rng.choice(GLOBAL_BRANDS)

        # Foreign products are cheaper (mass-produced)
        foreign_price_ranges = {
            "apparel": (2000, 15000),
            "leather": (5000, 25000),
            "basketry": (1000, 8000),
            "jewellery": (2000, 15000),
            "home-decor": (3000, 12000)
        }
        price = int(rng.integers(*foreign_price_ranges[cat]))

        title_template = rng.choice(FOREIGN_PRODUCT_TEMPLATES[cat])
        adj = rng.choice(["mass-produced", "imported", "generic", "factory", "basic"])
        title = title_template.format(brand, material, cat)
        title = title.replace("  ", " ").strip()

        desc_template = FOREIGN_DESCRIPTION_TEMPLATES[cat]
        description = desc_template.format(brand, material, country, material)
        description = description.replace("  ", " ").strip()

        products.append({
            "sku": f"GN-{cat[:3].upper()}-{sku_counter:04d}",
            "title": title,
            "description": description,
            "category": cat,
            "material": material,
            "origin_district": country,
            "price_rwf": price,
            "artisan_id": f"BRAND-{random.randint(100, 999)}",
            "is_local": False
        })

    df = pd.DataFrame(products)
    return df


def generate_queries(seed=RANDOM_SEED):
    """Generate synthetic search queries."""
    rng = np.random.default_rng(seed)

    queries = []
    for i, (query_text, lang) in enumerate(QUERY_TEMPLATES):
        # Generate a 'global best match' baseline for each query
        global_brand = rng.choice(GLOBAL_BRANDS)
        global_product = f"{global_brand} {query_text}"

        queries.append({
            "query_id": f"Q-{i+1:04d}",
            "query": query_text,
            "language": lang,
            "global_best_match": global_product,
            "global_brand": global_brand
        })

    df = pd.DataFrame(queries)
    return df


def generate_click_log(catalog_df, seed=RANDOM_SEED):
    """Generate synthetic click events with position-bias noise."""
    rng = np.random.default_rng(seed)

    clicks = []
    for i in range(N_CLICKS):
        product = catalog_df.sample(1, random_state=rng).iloc[0]
        # Position bias: earlier positions get more clicks
        position = int(rng.geometric(p=0.3))  # ~70% in position 1
        position = min(position, 20)

        clicks.append({
            "click_id": f"CLK-{i+1:06d}",
            "sku": product["sku"],
            "query_id": rng.choice([f"Q-{j+1:04d}" for j in range(N_QUERIES)]),
            "position": position,
            "clicked": 1 if rng.random() > 0.3 else 0,  # 70% click rate
            "converted": 1 if rng.random() > 0.8 else 0,  # 20% conversion
            "price_rwf": product["price_rwf"]
        })

    df = pd.DataFrame(clicks)
    return df


def generate_all():
    """Generate all datasets and save to CSV."""
    print("Generating product catalog...")
    catalog = generate_catalog()
    catalog.to_csv(OUTPUT_DIR / "catalog.csv", index=False)
    print(f"   - {len(catalog)} products saved to data/catalog.csv")

    print("Generating search queries...")
    queries = generate_queries()
    queries.to_csv(OUTPUT_DIR / "queries.csv", index=False)
    print(f"   - {len(queries)} queries saved to data/queries.csv")

    print("Generating click log...")
    clicks = generate_click_log(catalog)
    clicks.to_csv(OUTPUT_DIR / "click_log.csv", index=False)
    print(f"   - {len(clicks)} click events saved to data/click_log.csv")

    print("\nAll data generated successfully!")
    return catalog, queries, clicks


if __name__ == "__main__":
    generate_all()
