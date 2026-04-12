"""
FoodMythBuster Dashboard
Are "healthy" food labels a lie?

Backend selection via FOODMYTHBUSTER_BACKEND:
  duckdb  (default) — reads data/foodmythbuster.duckdb
  bigquery          — reads from BigQuery; requires GCP_PROJECT_ID
                      (optional BQ_DATASET, default: foodmythbuster).
                      Uses Application Default Credentials.
"""

import os

import duckdb
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="FoodMythBuster", layout="wide")

BACKEND = os.getenv("FOODMYTHBUSTER_BACKEND", "duckdb").lower()
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/foodmythbuster.duckdb")

if BACKEND == "bigquery":
    from google.cloud import bigquery
    GCP_PROJECT = os.environ["GCP_PROJECT_ID"]
    BQ_DATASET = os.getenv("BQ_DATASET", "foodmythbuster")
    TABLE = f"`{GCP_PROJECT}.{BQ_DATASET}.stg_products`"
else:
    TABLE = "staging.stg_products"


def is_bq() -> bool:
    return BACKEND == "bigquery"


@st.cache_resource
def get_client():
    if is_bq():
        return bigquery.Client(project=GCP_PROJECT)
    return duckdb.connect(DUCKDB_PATH, read_only=True)


@st.cache_data(ttl=600)
def query(sql: str):
    client = get_client()
    if is_bq():
        # 1 GB per-query cap: hard ceiling on any accidental runaway scan.
        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=1_000_000_000,
        )
        return client.query(sql, job_config=job_config).to_dataframe()
    return client.execute(sql).fetchdf()


# ── Taxonomies ──────────────────────────────────────────────────────────────
# OFF category tags consolidated into human-readable groups.
CATEGORY_GROUPS: dict[str, list[str]] = {
    "Milks & Dairy Drinks": [
        "milks", "flavoured-milks", "chocolate-milks", "dairy-drinks",
        "milk-drinks", "condensed-milks", "plant-based-milks",
    ],
    "Fermented Dairy": [
        "yogurts", "fermented-milk-products", "fermented-dairy-desserts",
        "kefir", "skyr", "drinkable-yogurts",
    ],
    "Cheeses": ["cheeses", "processed-cheeses", "cream-cheeses"],
    "Desserts & Ice Cream": [
        "desserts", "dairy-desserts", "puddings", "frozen-desserts",
        "ice-creams-and-sorbets", "chilled-desserts", "custards",
        "ice-creams", "sorbets",
    ],
    "Breakfast Cereals": [
        "breakfast-cereals", "mueslis", "granolas", "corn-flakes",
        "chocolate-breakfast-cereals",
    ],
    "Biscuits & Cookies": [
        "biscuits", "cookies", "biscuits-and-cakes",
        "chocolate-biscuits", "filled-biscuits", "sweet-biscuits",
    ],
    "Snacks": [
        "salty-snacks", "sweet-snacks", "chips-and-fries", "crackers",
        "appetizers", "extruded-snacks",
    ],
    "Chocolate & Confectionery": [
        "chocolates", "chocolate-bars", "candies", "sweets",
        "confectioneries", "chocolate-candies",
    ],
    "Beverages": [
        "beverages", "sodas", "fruit-juices", "flavoured-waters",
        "sports-drinks", "iced-teas", "nectars", "energy-drinks",
        "carbonated-drinks", "soft-drinks", "fruit-based-beverages",
    ],
    "Breads & Bakery": [
        "breads", "breakfast-pastries", "pastries", "bakery-products",
        "sandwich-breads", "toasts", "cakes",
    ],
    "Sauces & Dressings": [
        "sauces", "salad-dressings", "mayonnaises", "ketchups",
        "mustards", "tomato-sauces",
    ],
    "Spreads & Jams": [
        "spreads", "sweet-spreads", "chocolate-spreads", "jams",
        "hazelnut-spreads", "nut-spreads",
    ],
    "Prepared Meals": [
        "meals", "ready-meals", "prepared-meals", "frozen-meals",
        "frozen-foods",
    ],
    "Processed Meats": [
        "processed-meats", "sausages", "charcuterie",
        "prepared-meats", "cooked-sausages",
    ],
    "Plant-Based Alternatives": [
        "meat-analogues", "vegetable-based-products",
        "plant-based-meat-alternatives",
    ],
}

# E-number → functional family. Roman-numeral suffixes (e450i, e450ii, …)
# are normalised to the base code before lookup, so e450i and e450ii both
# collapse to "Phosphates".
ADDITIVE_CATEGORIES: dict[str, str] = {
    "e100": "Curcumin", "e101": "Riboflavin",
    "e150": "Caramel Colors",
    "e160": "Carotenes & Carotenoids",
    "e161": "Carotenes & Carotenoids",
    "e162": "Beetroot Red",
    "e163": "Anthocyanins",
    "e200": "Sorbates", "e202": "Sorbates", "e203": "Sorbates",
    "e210": "Benzoates", "e211": "Benzoates",
    "e212": "Benzoates", "e213": "Benzoates",
    "e220": "Sulphites", "e221": "Sulphites", "e222": "Sulphites",
    "e223": "Sulphites", "e224": "Sulphites", "e226": "Sulphites",
    "e227": "Sulphites", "e228": "Sulphites",
    "e249": "Nitrites & Nitrates", "e250": "Nitrites & Nitrates",
    "e251": "Nitrites & Nitrates", "e252": "Nitrites & Nitrates",
    "e300": "Ascorbic Acid & Ascorbates",
    "e301": "Ascorbic Acid & Ascorbates",
    "e302": "Ascorbic Acid & Ascorbates",
    "e304": "Ascorbic Acid & Ascorbates",
    "e306": "Tocopherols", "e307": "Tocopherols",
    "e308": "Tocopherols", "e309": "Tocopherols",
    "e260": "Acetates", "e261": "Acetates",
    "e262": "Acetates", "e263": "Acetates",
    "e270": "Lactates", "e325": "Lactates",
    "e326": "Lactates", "e327": "Lactates",
    "e330": "Citric Acid & Citrates", "e331": "Citric Acid & Citrates",
    "e332": "Citric Acid & Citrates", "e333": "Citric Acid & Citrates",
    "e334": "Tartrates", "e335": "Tartrates",
    "e336": "Tartrates", "e337": "Tartrates",
    "e338": "Phosphates", "e339": "Phosphates", "e340": "Phosphates",
    "e341": "Phosphates", "e343": "Phosphates",
    "e450": "Phosphates", "e451": "Phosphates", "e452": "Phosphates",
    "e322": "Lecithins",
    "e400": "Alginates", "e401": "Alginates", "e402": "Alginates",
    "e403": "Alginates", "e404": "Alginates", "e405": "Alginates",
    "e406": "Agar",
    "e407": "Carrageenan",
    "e410": "Gums", "e412": "Gums", "e413": "Gums", "e414": "Gums",
    "e415": "Gums", "e417": "Gums", "e418": "Gums",
    "e420": "Polyols",
    "e421": "Polyols",
    "e440": "Pectins",
    "e460": "Celluloses", "e461": "Celluloses", "e463": "Celluloses",
    "e464": "Celluloses", "e465": "Celluloses", "e466": "Celluloses",
    "e471": "Mono- & Diglycerides",
    "e472": "Mono- & Diglycerides",
    "e500": "Carbonates", "e501": "Carbonates",
    "e503": "Carbonates", "e504": "Carbonates",
    "e551": "Silicates", "e552": "Silicates",
    "e553": "Silicates", "e554": "Silicates",
    "e620": "Glutamates", "e621": "Glutamates", "e622": "Glutamates",
    "e623": "Glutamates", "e624": "Glutamates", "e625": "Glutamates",
    "e950": "Sweeteners", "e951": "Sweeteners", "e952": "Sweeteners",
    "e953": "Sweeteners", "e954": "Sweeteners", "e955": "Sweeteners",
    "e960": "Sweeteners", "e961": "Sweeteners", "e962": "Sweeteners",
    "e965": "Polyols", "e966": "Polyols",
    "e967": "Polyols", "e968": "Polyols",
    "e1400": "Modified Starches", "e1401": "Modified Starches",
    "e1402": "Modified Starches", "e1403": "Modified Starches",
    "e1404": "Modified Starches", "e1410": "Modified Starches",
    "e1412": "Modified Starches", "e1413": "Modified Starches",
    "e1414": "Modified Starches", "e1420": "Modified Starches",
    "e1422": "Modified Starches", "e1440": "Modified Starches",
    "e1442": "Modified Starches", "e1450": "Modified Starches",
    "e1451": "Modified Starches",
}

CATEGORY_PAIRS = [(tag, grp) for grp, tags in CATEGORY_GROUPS.items() for tag in tags]
ADDITIVE_PAIRS = list(ADDITIVE_CATEGORIES.items())


def _duckdb_values(pairs: list[tuple[str, str]]) -> str:
    return ",\n            ".join(f"('{k}', '{v}')" for k, v in pairs)


def _bq_struct_array(pairs: list[tuple[str, str]], f1: str, f2: str) -> str:
    items = ",\n            ".join(
        f"STRUCT('{k}' AS {f1}, '{v}' AS {f2})" for k, v in pairs
    )
    return f"[\n            {items}\n        ]"


CATEGORY_VALUES_DUCKDB = _duckdb_values(CATEGORY_PAIRS)
ADDITIVE_VALUES_DUCKDB = _duckdb_values(ADDITIVE_PAIRS)
CATEGORY_STRUCT_BQ = _bq_struct_array(CATEGORY_PAIRS, "tag", "grp")
ADDITIVE_STRUCT_BQ = _bq_struct_array(ADDITIVE_PAIRS, "code", "category")


# ── Header ──────────────────────────────────────────────────────────────────
st.sidebar.caption(f"Viewing: **Brazil** · `{TABLE}`")
st.sidebar.caption(f"Backend: **{'BigQuery' if is_bq() else 'DuckDB (local)'}**")
st.title("FoodMythBuster")
st.markdown(
    "Are **'healthy' food labels** a lie? Investigating whether front-of-pack "
    "health claims align with **NOVA classification** (degree of industrial processing)."
)

# ── KPIs ────────────────────────────────────────────────────────────────────
if is_bq():
    kpi_sql = f"""
        SELECT
          COUNT(*) AS total,
          COUNTIF(is_ultra_processed) AS nova4,
          COUNTIF(has_health_claim) AS with_claim,
          COUNTIF(is_deceptive) AS deceptive
        FROM {TABLE}
    """
else:
    kpi_sql = f"""
        SELECT
            count(*)                             AS total,
            count(*) FILTER (is_ultra_processed) AS nova4,
            count(*) FILTER (has_health_claim)   AS with_claim,
            count(*) FILTER (is_deceptive)       AS deceptive
        FROM {TABLE}
    """
kpi = query(kpi_sql)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Products", f"{kpi['total'][0]:,}")
c2.metric("NOVA 4 (Ultra-Processed)", f"{kpi['nova4'][0]:,}")
c3.metric("With Health Claim", f"{kpi['with_claim'][0]:,}")
c4.metric("Deceptive (Claim + NOVA 4)", f"{kpi['deceptive'][0]:,}")

st.divider()

# ── Chart 1: Nutri-Score paradox ────────────────────────────────────────────
st.subheader("1 · The Paradox: Nutri-Score A/B but Ultra-Processed")

st.info(
    "**What is Nutri-Score?** A front-of-pack nutrition label developed in "
    "France (2017) and adopted across several European countries. It grades "
    "packaged foods from **A (green, best)** to **E (red, worst)** based on "
    "nutrient density per 100 g — sugar, salt, saturated fat and calories "
    "weighed against fibre, protein, fruits and vegetables. It rates "
    "**nutritional composition**, not degree of processing — so a product "
    "reformulated to score well on paper can still be **ultra-processed "
    "(NOVA 4)**, which is exactly what this chart reveals."
)

if is_bq():
    paradox_sql = f"""
        SELECT
          nutriscore_grade,
          COUNT(*) AS total,
          COUNTIF(is_ultra_processed) AS nova4,
          ROUND(100.0 * COUNTIF(is_ultra_processed) / COUNT(*), 1) AS pct_nova4
        FROM {TABLE}
        WHERE nutriscore_grade IN ('a','b','c','d','e')
        GROUP BY nutriscore_grade
        ORDER BY nutriscore_grade
    """
else:
    paradox_sql = f"""
        SELECT
            nutriscore_grade,
            count(*)                             AS total,
            count(*) FILTER (is_ultra_processed) AS nova4,
            round(100.0 * count(*) FILTER (is_ultra_processed) / count(*), 1) AS pct_nova4
        FROM {TABLE}
        WHERE nutriscore_grade IN ('a', 'b', 'c', 'd', 'e')
        GROUP BY nutriscore_grade
        ORDER BY nutriscore_grade
    """
df_paradox = query(paradox_sql)

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(
        df_paradox, x="nutriscore_grade", y=["total", "nova4"],
        barmode="group", title="Products by Nutri-Score: Total vs NOVA 4",
        labels={"value": "Products", "nutriscore_grade": "Nutri-Score"},
        color_discrete_map={"total": "#636EFA", "nova4": "#EF553B"},
    )
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        df_paradox, x="nutriscore_grade", y="pct_nova4",
        title="% Ultra-Processed by Nutri-Score Grade",
        labels={"pct_nova4": "% NOVA 4", "nutriscore_grade": "Nutri-Score"},
        color="pct_nova4", color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Chart 2: 'Green Label' but Ultra-Processed ──────────────────────────────
st.subheader("2 · 'Green Label' but Ultra-Processed")

deceptive_total = int(kpi["deceptive"][0])
with_claim_total = int(kpi["with_claim"][0])
pct_deceptive = round(100.0 * deceptive_total / with_claim_total, 1) if with_claim_total else 0.0

st.markdown(
    f"**{deceptive_total:,} products** in this dataset carry at least one "
    "front-of-pack health claim *and* are classified **NOVA 4 (ultra-processed)** — "
    f"that is **{pct_deceptive}%** of all claim-bearing products. "
    "Below, the share of NOVA 4 broken down by each individual claim."
)

if is_bq():
    labels_sql = f"""
        WITH exploded AS (
          SELECT claim, is_ultra_processed
          FROM {TABLE}, UNNEST(matched_health_claims) AS claim
          WHERE ARRAY_LENGTH(matched_health_claims) > 0
        )
        SELECT
          REPLACE(claim, 'en:', '') AS label,
          COUNT(*) AS total,
          COUNTIF(is_ultra_processed) AS nova4,
          ROUND(100.0 * COUNTIF(is_ultra_processed) / COUNT(*), 1) AS pct_nova4
        FROM exploded
        GROUP BY claim
        ORDER BY pct_nova4 DESC
    """
else:
    labels_sql = f"""
        WITH exploded AS (
            SELECT unnest(matched_health_claims) AS claim, is_ultra_processed
            FROM {TABLE}
            WHERE len(matched_health_claims) > 0
        )
        SELECT
            replace(claim, 'en:', '')            AS label,
            count(*)                             AS total,
            count(*) FILTER (is_ultra_processed) AS nova4,
            round(100.0 * count(*) FILTER (is_ultra_processed) / count(*), 1) AS pct_nova4
        FROM exploded
        GROUP BY claim
        ORDER BY pct_nova4 DESC
    """
df_labels = query(labels_sql)

fig = px.bar(
    df_labels, x="label", y="pct_nova4", color="pct_nova4",
    color_continuous_scale="RdYlGn_r",
    title="% Ultra-Processed Among Products Carrying Each Health Claim",
    labels={"pct_nova4": "% NOVA 4", "label": "Health Claim"},
    text="total",
)
fig.update_traces(texttemplate="%{text} products", textposition="outside")
fig.update_yaxes(range=[0, max(df_labels["pct_nova4"].max() * 1.18, 10)])
st.plotly_chart(fig, use_container_width=True)

# ── Chart 3: 'Healthy Junk' by category group ──────────────────────────────
st.subheader("3 · 'Healthy Junk' by Category Group")

if is_bq():
    category_sql = f"""
        WITH mapping AS (
          SELECT tag, grp FROM UNNEST({CATEGORY_STRUCT_BQ})
        ),
        exploded AS (
          SELECT
            product_id,
            REPLACE(tag, 'en:', '') AS category
          FROM {TABLE}, UNNEST(categories_tags) AS tag
          WHERE is_deceptive
        )
        SELECT
          m.grp                         AS category_group,
          COUNT(DISTINCT e.product_id)  AS products
        FROM exploded e
        JOIN mapping m ON e.category = m.tag
        GROUP BY m.grp
        ORDER BY products DESC
    """
else:
    category_sql = f"""
        WITH mapping(tag, grp) AS (
            VALUES
                {CATEGORY_VALUES_DUCKDB}
        ),
        exploded AS (
            SELECT
                product_id,
                replace(unnest(categories_tags), 'en:', '') AS category
            FROM {TABLE}
            WHERE is_deceptive
        )
        SELECT
            m.grp                         AS category_group,
            count(DISTINCT e.product_id)  AS products
        FROM exploded e
        JOIN mapping m ON e.category = m.tag
        GROUP BY m.grp
        ORDER BY products DESC
    """
df_cat = query(category_sql)

fig = px.bar(
    df_cat, x="products", y="category_group", orientation="h",
    title="Deceptive Products (Health Claim + NOVA 4) by Category Group",
    labels={"products": "Products", "category_group": ""},
    color="products", color_continuous_scale="RdYlGn_r",
    text="products",
)
fig.update_traces(textposition="outside")
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    height=550,
    coloraxis_showscale=False,
)
st.plotly_chart(fig, use_container_width=True)

# ── Chart 4: Top brands selling deceptive products ─────────────────────────
st.subheader("4 · Top Brands: Health Claim + Ultra-Processed")

if is_bq():
    brands_sql = f"""
        SELECT
          ANY_VALUE(brands) AS brand,
          COUNT(*) AS products
        FROM {TABLE}
        WHERE is_deceptive
          AND brands IS NOT NULL
          AND brands != ''
        GROUP BY LOWER(
          REGEXP_REPLACE(NORMALIZE(TRIM(brands), NFD), r'\\p{{Mn}}', '')
        )
        ORDER BY products DESC
        LIMIT 10
    """
else:
    brands_sql = f"""
        SELECT
            mode(brands)       AS brand,
            count(*)           AS products
        FROM {TABLE}
        WHERE is_deceptive
          AND brands IS NOT NULL
          AND brands != ''
        GROUP BY lower(strip_accents(trim(brands)))
        ORDER BY products DESC
        LIMIT 10
    """
df_brands = query(brands_sql)

fig = px.bar(
    df_brands, x="products", y="brand", orientation="h",
    title="Top 10 Brands Selling NOVA 4 Products Under Health Claims",
    labels={"products": "Products", "brand": ""},
    color_discrete_sequence=["#EF553B"],
)
fig.update_layout(yaxis=dict(autorange="reversed"), height=450)
st.plotly_chart(fig, use_container_width=True)

# ── Chart 5: Top additive families ─────────────────────────────────────────
st.subheader("5 · Top 5 Additive Families in Deceptive Products")
st.caption(
    "E-numbers from products that are **NOVA 4 and carry a health claim**, "
    "grouped by functional family. Roman-numeral suffixes (e.g. E450i, "
    "E450ii) are collapsed to the base code."
)

if is_bq():
    additive_sql = f"""
        WITH mapping AS (
          SELECT code, category FROM UNNEST({ADDITIVE_STRUCT_BQ})
        ),
        exploded AS (
          SELECT
            REGEXP_EXTRACT(
              REPLACE(LOWER(tag), 'en:', ''),
              r'^(e\\d+)'
            ) AS base_code
          FROM {TABLE}, UNNEST(additives_tags) AS tag
          WHERE is_deceptive
        ),
        joined AS (
          SELECT m.category, e.base_code
          FROM exploded e
          JOIN mapping m ON e.base_code = m.code
        )
        SELECT
          category,
          COUNT(*) AS occurrences,
          ARRAY_AGG(DISTINCT UPPER(base_code) ORDER BY UPPER(base_code)) AS codes
        FROM joined
        GROUP BY category
        ORDER BY occurrences DESC
        LIMIT 5
    """
else:
    additive_sql = f"""
        WITH mapping(code, category) AS (
            VALUES
                {ADDITIVE_VALUES_DUCKDB}
        ),
        exploded AS (
            SELECT
                regexp_extract(
                    replace(lower(unnest(additives_tags)), 'en:', ''),
                    '^(e\\d+)', 1
                ) AS base_code
            FROM {TABLE}
            WHERE is_deceptive
        ),
        joined AS (
            SELECT m.category, e.base_code
            FROM exploded e
            JOIN mapping m ON e.base_code = m.code
        )
        SELECT
            category,
            count(*)                                             AS occurrences,
            list_sort(list_distinct(array_agg(upper(base_code)))) AS codes
        FROM joined
        GROUP BY category
        ORDER BY occurrences DESC
        LIMIT 5
    """
df_add = query(additive_sql)

df_add["label"] = df_add.apply(
    lambda r: f"{'/'.join(r['codes'])} ({r['category']})", axis=1
)

fig = px.bar(
    df_add, x="occurrences", y="label", orientation="h",
    title="Top 5 Additive Families in NOVA 4 Products with Health Claims",
    labels={"occurrences": "Occurrences", "label": ""},
    color_discrete_sequence=["#EF553B"],
    text="occurrences",
)
fig.update_traces(textposition="outside")
fig.update_layout(yaxis=dict(autorange="reversed"), height=400)
st.plotly_chart(fig, use_container_width=True)

ADDITIVE_HEALTH_REFS: dict[str, tuple[str, str]] = {
    "Phosphates": (
        "Concerns for kidney issues and coronary heart disease risk.",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC3278747/",
    ),
    "Polyols": (
        "Association with cardiovascular and coronary disease, "
        "and gut-microbiota disruption.",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC12767680/",
    ),
    "Sweeteners": (
        "Linked to higher cardiovascular disease and coronary disease risk.",
        "https://www.bmj.com/content/378/bmj-2022-071204",
    ),
    "Sorbates": (
        "Association with higher cancer risk.",
        "https://pubmed.ncbi.nlm.nih.gov/41500678/",
    ),
}

top5_categories = set(df_add["category"])
refs_shown = [
    (cat, *ADDITIVE_HEALTH_REFS[cat])
    for cat in ADDITIVE_HEALTH_REFS
    if cat in top5_categories
]

if refs_shown:
    st.markdown("**Health concerns linked to these additive families**")
    for cat, concern, url in refs_shown:
        st.markdown(f"- **{cat}** — {concern} [source]({url})")

# ── Chart 6: Temporal — deceptive vs non-deceptive NOVA 4 additive gap ─────
st.subheader("6 · The Widening Gap: Deceptive NOVA 4 Use More Additives Over Time")
st.caption(
    "Among NOVA 4 products, average number of additives per product, split by "
    "whether they *also* carry a health claim. The 2023 dashed marker is when "
    "**ANVISA RDC 429/2020** mandatory front-of-pack warning labels became enforceable "
    "in Brazil — sample sizes jump that year, so read the trend carefully."
)

if is_bq():
    temporal_sql = f"""
        SELECT
          EXTRACT(YEAR FROM created_date) AS created_year,
          AVG(IF(has_health_claim, additives_count, NULL)) AS avg_deceptive,
          AVG(IF(NOT has_health_claim, additives_count, NULL)) AS avg_non_deceptive,
          COUNTIF(has_health_claim) AS deceptive_n,
          COUNTIF(NOT has_health_claim) AS non_deceptive_n
        FROM {TABLE}
        WHERE is_ultra_processed
          AND created_date BETWEEN DATE '2020-01-01' AND DATE '2024-12-31'
        GROUP BY created_year
        ORDER BY created_year
    """
else:
    temporal_sql = f"""
        SELECT
            created_year,
            avg(additives_count) FILTER (has_health_claim)     AS avg_deceptive,
            avg(additives_count) FILTER (NOT has_health_claim) AS avg_non_deceptive,
            count(*) FILTER (has_health_claim)                 AS deceptive_n,
            count(*) FILTER (NOT has_health_claim)             AS non_deceptive_n
        FROM {TABLE}
        WHERE is_ultra_processed
          AND created_year BETWEEN 2020 AND 2024
        GROUP BY created_year
        ORDER BY created_year
    """
df_temporal = query(temporal_sql)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_temporal["created_year"], y=df_temporal["avg_deceptive"],
    mode="lines+markers", name="With health claim (deceptive)",
    line=dict(color="#EF553B", width=3),
    marker=dict(size=9),
))
fig.add_trace(go.Scatter(
    x=df_temporal["created_year"], y=df_temporal["avg_non_deceptive"],
    mode="lines+markers", name="No health claim",
    line=dict(color="#636EFA", width=3),
    marker=dict(size=9),
))
fig.add_vline(
    x=2023, line_dash="dash", line_color="gray",
    annotation_text="ANVISA RDC 429/2020 enforced",
    annotation_position="top left",
)
fig.update_layout(
    title="Avg additives per product · NOVA 4 with vs without health claim",
    xaxis_title="Year product was added to Open Food Facts",
    yaxis_title="Avg additives per product",
    height=450,
    xaxis=dict(tickmode="linear", dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

sample_lines = [
    f"**{int(r['created_year'])}** → "
    f"deceptive n={int(r['deceptive_n'])}, "
    f"non-deceptive n={int(r['non_deceptive_n'])}"
    for _, r in df_temporal.iterrows()
]
st.caption("Sample sizes per year — " + " · ".join(sample_lines))

# ── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Data: [Open Food Facts](https://world.openfoodfacts.org) · "
    "NOVA classification: Prof. Carlos Monteiro, University of São Paulo · "
    "Built for [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)"
)
