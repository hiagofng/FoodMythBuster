# Looker Studio Dashboard — Step-by-Step Guide

> Recreating the FoodMythBuster Streamlit dashboard in **Google Looker Studio**,
> connected to the existing `foodmythbuster.stg_products` BigQuery table.

---

## Table of Contents

1. [Mental Model: Streamlit vs Looker Studio](#1--mental-model-streamlit-vs-looker-studio)
2. [Prerequisites](#2--prerequisites)
3. [Creating the Report & Connecting BigQuery](#3--creating-the-report--connecting-bigquery)
4. [How Data Sources Work](#4--how-data-sources-work)
5. [Tile 0 — KPI Scorecards](#5--tile-0--kpi-scorecards)
6. [Tile 1 — Nutri-Score Paradox](#6--tile-1--nutriscore-paradox)
7. [Tile 2 — Green Label but Ultra-Processed](#7--tile-2--green-label-but-ultra-processed)
8. [Tile 3 — Healthy Junk by Category Group](#8--tile-3--healthy-junk-by-category-group)
9. [Tile 4 — Top Brands](#9--tile-4--top-brands)
10. [Tile 5 — Top Additive Families](#10--tile-5--top-additive-families)
11. [Tile 6 — Temporal Gap](#11--tile-6--temporal-gap)
12. [Styling & Layout](#12--styling--layout)
13. [Publishing & Sharing](#13--publishing--sharing)
14. [Limitations vs Streamlit](#14--limitations-vs-streamlit)

---

## 1 · Mental Model: Streamlit vs Looker Studio

Think of the difference like this:

| Concept | Streamlit (`app.py`) | Looker Studio |
|---|---|---|
| Where it runs | Python process on your machine or a server | Google's servers — browser only, zero deploy |
| How you build | Write Python code | Drag-and-drop in a visual editor (like Google Slides meets Excel pivot charts) |
| Data connection | You write SQL strings, call `query()` | You pick a "Data Source" (BigQuery table or custom SQL) — Looker writes the query for you |
| Charts | `plotly.express` / `go.Figure()` | Built-in chart types — bar, line, scorecard, table, etc. |
| Calculated fields | Python expressions in SQL or pandas | Formula language (similar to Google Sheets formulas) |
| Interactivity | `st.selectbox`, `st.slider` | "Controls" — drop-down filters, date range pickers, search bars |
| Caching | `@st.cache_data(ttl=600)` | Automatic — Looker Studio caches BigQuery results for ~12 hours by default |
| Cost control | `maximum_bytes_billed` in code | Managed per data source (see Section 4) |

**The analogy:** if Streamlit is like cooking from scratch (full control, you write every line), Looker Studio is like assembling a meal kit — the ingredients arrive pre-cut, you just arrange them on the plate. You lose some control but gain speed and zero-maintenance hosting.

---

## 2 · Prerequisites

- [x] `foodmythbuster.stg_products` exists and is queryable in BigQuery (your pipeline already did this)
- [x] A Google account with access to that BigQuery project
- [x] A browser — that's it, no installs

Go to **[lookerstudio.google.com](https://lookerstudio.google.com)** and sign in with the same Google account that has BigQuery access.

---

## 3 · Creating the Report & Connecting BigQuery

### 3.1 — Create a blank report

1. On the Looker Studio home page, click **"+ Blank Report"** (or **Create → Report**)
2. It immediately asks you to **add a data source**

### 3.2 — Add BigQuery as a data source

This is the equivalent of your `get_client()` + `query()` functions in `app.py`. Instead of writing connection code, you point-and-click:

1. In the "Add data to report" panel, select **BigQuery** (it's the first connector listed)
2. **Authorize** if prompted — this grants Looker Studio read access to your BQ datasets
3. Navigate: **My Projects → `<your-project-id>` → `foodmythbuster` → `stg_products`**
4. Click **ADD**
5. Click **ADD TO REPORT** when it asks to confirm

You now have a data source connected. Think of it as a live wire to your BigQuery table — every chart you add will pull from this table.

> **What just happened behind the scenes?** Looker Studio read the schema of
> `stg_products` and created a "field list" — every column becomes a
> **dimension** (text, date, boolean) or a **metric** (number you can
> aggregate). You'll see this field list on the right panel whenever you
> select a chart.

### 3.3 — Rename the report

Click "Untitled Report" at the top-left and rename it to **"FoodMythBuster"**.

---

## 4 · How Data Sources Work

Before building charts, understand this key concept — it's the biggest difference from Streamlit.

### Table-based vs Custom Query data sources

In Streamlit, every chart has its own hand-written SQL. In Looker Studio, you have two options:

| Approach | When to use | Analogy |
|---|---|---|
| **Table source** (what we just added) | Simple aggregations: COUNT, AVG, GROUP BY on flat columns | Like a pivot table on a spreadsheet |
| **Custom Query source** | Complex SQL: UNNEST arrays, JOINs, CTEs, regex | Like your raw SQL in `app.py` |

**For `stg_products`, the flat columns work for tiles 0, 1, 4, and 6.** But tiles 2, 3, and 5 need `UNNEST(matched_health_claims)`, `UNNEST(categories_tags)`, and `UNNEST(additives_tags)` — arrays that Looker Studio's formula language cannot explode. For those, we'll add **Custom Query** data sources.

### Adding a Custom Query data source

You'll do this several times, so memorize the flow:

1. Menu bar → **Resource → Manage added data sources**
2. Click **ADD A DATA SOURCE**
3. Select **BigQuery**
4. Instead of picking a table, click **CUSTOM QUERY** (left sidebar)
5. Select your project
6. Paste the SQL (provided below for each tile)
7. Click **ADD** → **ADD TO REPORT**

> **Cost note:** Each custom query runs against BigQuery when someone views
> the report. Looker Studio caches results for ~12h. Your table is ~5 MB,
> so costs are negligible. But the habit of adding `WHERE` clauses and
> `LIMIT` is good practice for when you scale to the global dataset.

---

## 5 · Tile 0 — KPI Scorecards

These are the four numbers at the top: Total Products, NOVA 4, With Health Claim, Deceptive.

**In Streamlit** you did this with `st.metric()`. **In Looker Studio** the equivalent is a **Scorecard** chart.

### Step by step

For **each** of the four KPIs:

1. Click **Add a chart → Scorecard** (looks like a single big number)
2. Place it at the top of the canvas — arrange four in a row
3. In the right **Data** panel, configure:

| Scorecard | Metric | How to configure |
|---|---|---|
| Total Products | `Record Count` | Metric = `Record Count` (built-in, auto-available) |
| NOVA 4 | Count where `is_ultra_processed = true` | See calculated field below |
| With Health Claim | Count where `has_health_claim = true` | See calculated field below |
| Deceptive | Count where `is_deceptive = true` | See calculated field below |

### Creating calculated metrics

Looker Studio doesn't have `COUNT(*) FILTER (condition)` like DuckDB. Instead, you create **calculated fields**:

1. In the Data panel (right side), click **"+ Add a field"** (or go to **Resource → Manage added data sources → EDIT → Add a field**)
2. Create these three fields:

**Field: `nova4_count`**
```
SUM(CASE WHEN is_ultra_processed = true THEN 1 ELSE 0 END)
```
Type: Number, Aggregation: Auto

**Field: `claim_count`**
```
SUM(CASE WHEN has_health_claim = true THEN 1 ELSE 0 END)
```

**Field: `deceptive_count`**
```
SUM(CASE WHEN is_deceptive = true THEN 1 ELSE 0 END)
```

3. Assign each calculated field as the **Metric** of the corresponding scorecard.

> **Analogy:** calculated fields in Looker Studio are like adding a virtual
> column to a spreadsheet that doesn't exist in the raw data — it's computed
> on the fly. Same idea as a SQL `CASE WHEN` wrapped in `SUM`.

### Formatting

- Click a scorecard → **Style** tab (right panel)
- Enable **Compact Numbers** to get "1,234" formatting
- Set font size to ~32pt for the number, ~12pt for the label
- Optionally add a colored background rectangle behind all four (Insert → Shape)

---

## 6 · Tile 1 — Nutri-Score Paradox

Two side-by-side bar charts. In `app.py` this was `px.bar()` with `barmode="group"`.

### Chart A — "Products by Nutri-Score: Total vs NOVA 4"

This one uses the **table data source** (no custom SQL needed):

1. **Add a chart → Bar chart** (grouped bar)
2. Data source: `stg_products`
3. Configure:
   - **Dimension:** `nutriscore_grade`
   - **Metric 1:** `Record Count` (= total)
   - **Metric 2:** `nova4_count` (the calculated field from above)
   - **Sort:** `nutriscore_grade` ascending
4. **Filter:** Add a filter → `nutriscore_grade` is not NULL
   (equivalent to your `WHERE nutriscore_grade IN ('a','b','c','d','e')`)

> In Looker Studio, when you put two metrics on the same bar chart, it
> automatically groups them side by side — no `barmode="group"` needed.

### Chart B — "% Ultra-Processed by Nutri-Score Grade"

This needs a percentage. Create a calculated field:

**Field: `pct_nova4`**
```
SUM(CASE WHEN is_ultra_processed = true THEN 1 ELSE 0 END) / COUNT(product_id) * 100
```

1. **Add a chart → Bar chart**
2. **Dimension:** `nutriscore_grade`
3. **Metric:** `pct_nova4`
4. **Sort:** `nutriscore_grade` ascending
5. **Filter:** `nutriscore_grade` is not NULL

#### Adding the color gradient (RdYlGn_r equivalent)

Looker Studio doesn't have per-bar conditional coloring as flexible as Plotly's `color_continuous_scale`. The closest approach:

1. **Style** tab → **Color by** → select a single color, OR
2. Use a **"Bar chart with conditional formatting"**: Style → Series → enable "Conditional formatting" → add rules:
   - If metric >= 60 → red (#EF553B)
   - If metric >= 40 → orange
   - If metric < 40 → green

This approximates the red-yellow-green scale.

---

## 7 · Tile 2 — Green Label but Ultra-Processed

This chart uses `UNNEST(matched_health_claims)` — **you need a Custom Query data source**.

### Add the data source

Go to **Resource → Manage added data sources → Add a data source → BigQuery → Custom Query**.

Paste the SQL from `docs/looker-studio-queries/tile2_health_claims.sql` (file created alongside this guide):

```sql
SELECT
  REPLACE(claim, 'en:', '') AS label,
  COUNT(*) AS total,
  COUNTIF(is_ultra_processed) AS nova4,
  ROUND(100.0 * COUNTIF(is_ultra_processed) / COUNT(*), 1) AS pct_nova4
FROM `YOUR_PROJECT.foodmythbuster.stg_products`,
  UNNEST(matched_health_claims) AS claim
WHERE ARRAY_LENGTH(matched_health_claims) > 0
GROUP BY claim
ORDER BY pct_nova4 DESC
```

> **Replace `YOUR_PROJECT`** with your actual GCP project ID.

### Build the chart

1. **Add a chart → Bar chart**
2. **Data source:** select the custom query you just added (it will appear by name)
3. **Dimension:** `label`
4. **Metric:** `pct_nova4`
5. **Sort:** `pct_nova4` descending
6. **Style:** enable data labels → shows the value on each bar

To also show "N products" on each bar like Streamlit's `text="total"`:
- Add a second metric `total` and enable data labels for it
- Or use a **table** below the chart showing label + total + pct_nova4

---

## 8 · Tile 3 — Healthy Junk by Category Group

This is the most complex tile — it UNNEST's `categories_tags` and JOINs against a mapping table. **Custom Query required.**

### Add the data source

Custom Query SQL (also in `docs/looker-studio-queries/tile3_category_groups.sql`):

```sql
WITH mapping AS (
  SELECT tag, grp FROM UNNEST([
    STRUCT('milks' AS tag, 'Milks & Dairy Drinks' AS grp),
    STRUCT('flavoured-milks', 'Milks & Dairy Drinks'),
    STRUCT('chocolate-milks', 'Milks & Dairy Drinks'),
    STRUCT('dairy-drinks', 'Milks & Dairy Drinks'),
    STRUCT('milk-drinks', 'Milks & Dairy Drinks'),
    STRUCT('condensed-milks', 'Milks & Dairy Drinks'),
    STRUCT('plant-based-milks', 'Milks & Dairy Drinks'),
    STRUCT('yogurts', 'Fermented Dairy'),
    STRUCT('fermented-milk-products', 'Fermented Dairy'),
    STRUCT('fermented-dairy-desserts', 'Fermented Dairy'),
    STRUCT('kefir', 'Fermented Dairy'),
    STRUCT('skyr', 'Fermented Dairy'),
    STRUCT('drinkable-yogurts', 'Fermented Dairy'),
    STRUCT('cheeses', 'Cheeses'),
    STRUCT('processed-cheeses', 'Cheeses'),
    STRUCT('cream-cheeses', 'Cheeses'),
    STRUCT('desserts', 'Desserts & Ice Cream'),
    STRUCT('dairy-desserts', 'Desserts & Ice Cream'),
    STRUCT('puddings', 'Desserts & Ice Cream'),
    STRUCT('frozen-desserts', 'Desserts & Ice Cream'),
    STRUCT('ice-creams-and-sorbets', 'Desserts & Ice Cream'),
    STRUCT('chilled-desserts', 'Desserts & Ice Cream'),
    STRUCT('custards', 'Desserts & Ice Cream'),
    STRUCT('ice-creams', 'Desserts & Ice Cream'),
    STRUCT('sorbets', 'Desserts & Ice Cream'),
    STRUCT('breakfast-cereals', 'Breakfast Cereals'),
    STRUCT('mueslis', 'Breakfast Cereals'),
    STRUCT('granolas', 'Breakfast Cereals'),
    STRUCT('corn-flakes', 'Breakfast Cereals'),
    STRUCT('chocolate-breakfast-cereals', 'Breakfast Cereals'),
    STRUCT('biscuits', 'Biscuits & Cookies'),
    STRUCT('cookies', 'Biscuits & Cookies'),
    STRUCT('biscuits-and-cakes', 'Biscuits & Cookies'),
    STRUCT('chocolate-biscuits', 'Biscuits & Cookies'),
    STRUCT('filled-biscuits', 'Biscuits & Cookies'),
    STRUCT('sweet-biscuits', 'Biscuits & Cookies'),
    STRUCT('salty-snacks', 'Snacks'),
    STRUCT('sweet-snacks', 'Snacks'),
    STRUCT('chips-and-fries', 'Snacks'),
    STRUCT('crackers', 'Snacks'),
    STRUCT('appetizers', 'Snacks'),
    STRUCT('extruded-snacks', 'Snacks'),
    STRUCT('chocolates', 'Chocolate & Confectionery'),
    STRUCT('chocolate-bars', 'Chocolate & Confectionery'),
    STRUCT('candies', 'Chocolate & Confectionery'),
    STRUCT('sweets', 'Chocolate & Confectionery'),
    STRUCT('confectioneries', 'Chocolate & Confectionery'),
    STRUCT('chocolate-candies', 'Chocolate & Confectionery'),
    STRUCT('beverages', 'Beverages'),
    STRUCT('sodas', 'Beverages'),
    STRUCT('fruit-juices', 'Beverages'),
    STRUCT('flavoured-waters', 'Beverages'),
    STRUCT('sports-drinks', 'Beverages'),
    STRUCT('iced-teas', 'Beverages'),
    STRUCT('nectars', 'Beverages'),
    STRUCT('energy-drinks', 'Beverages'),
    STRUCT('carbonated-drinks', 'Beverages'),
    STRUCT('soft-drinks', 'Beverages'),
    STRUCT('fruit-based-beverages', 'Beverages'),
    STRUCT('breads', 'Breads & Bakery'),
    STRUCT('breakfast-pastries', 'Breads & Bakery'),
    STRUCT('pastries', 'Breads & Bakery'),
    STRUCT('bakery-products', 'Breads & Bakery'),
    STRUCT('sandwich-breads', 'Breads & Bakery'),
    STRUCT('toasts', 'Breads & Bakery'),
    STRUCT('cakes', 'Breads & Bakery'),
    STRUCT('sauces', 'Sauces & Dressings'),
    STRUCT('salad-dressings', 'Sauces & Dressings'),
    STRUCT('mayonnaises', 'Sauces & Dressings'),
    STRUCT('ketchups', 'Sauces & Dressings'),
    STRUCT('mustards', 'Sauces & Dressings'),
    STRUCT('tomato-sauces', 'Sauces & Dressings'),
    STRUCT('spreads', 'Spreads & Jams'),
    STRUCT('sweet-spreads', 'Spreads & Jams'),
    STRUCT('chocolate-spreads', 'Spreads & Jams'),
    STRUCT('jams', 'Spreads & Jams'),
    STRUCT('hazelnut-spreads', 'Spreads & Jams'),
    STRUCT('nut-spreads', 'Spreads & Jams'),
    STRUCT('meals', 'Prepared Meals'),
    STRUCT('ready-meals', 'Prepared Meals'),
    STRUCT('prepared-meals', 'Prepared Meals'),
    STRUCT('frozen-meals', 'Prepared Meals'),
    STRUCT('frozen-foods', 'Prepared Meals'),
    STRUCT('processed-meats', 'Processed Meats'),
    STRUCT('sausages', 'Processed Meats'),
    STRUCT('charcuterie', 'Processed Meats'),
    STRUCT('prepared-meats', 'Processed Meats'),
    STRUCT('cooked-sausages', 'Processed Meats'),
    STRUCT('meat-analogues', 'Plant-Based Alternatives'),
    STRUCT('vegetable-based-products', 'Plant-Based Alternatives'),
    STRUCT('plant-based-meat-alternatives', 'Plant-Based Alternatives')
  ])
),
exploded AS (
  SELECT
    product_id,
    REPLACE(tag, 'en:', '') AS category
  FROM `YOUR_PROJECT.foodmythbuster.stg_products`,
    UNNEST(categories_tags) AS tag
  WHERE is_deceptive
)
SELECT
  m.grp AS category_group,
  COUNT(DISTINCT e.product_id) AS products
FROM exploded e
JOIN mapping m ON e.category = m.tag
GROUP BY m.grp
ORDER BY products DESC
```

### Build the chart

1. **Add a chart → Bar chart → Horizontal**
2. **Data source:** the custom query above
3. **Dimension:** `category_group`
4. **Metric:** `products`
5. **Sort:** `products` descending

---

## 9 · Tile 4 — Top Brands

This one is simple enough for the table data source, but the brand normalization (`LOWER(REGEXP_REPLACE(NORMALIZE(...)))`) isn't possible in Looker Studio formulas. **Custom Query.**

SQL (also in `docs/looker-studio-queries/tile4_top_brands.sql`):

```sql
SELECT
  ANY_VALUE(brands) AS brand,
  COUNT(*) AS products
FROM `YOUR_PROJECT.foodmythbuster.stg_products`
WHERE is_deceptive
  AND brands IS NOT NULL
  AND brands != ''
GROUP BY LOWER(
  REGEXP_REPLACE(NORMALIZE(TRIM(brands), NFD), r'\p{Mn}', '')
)
ORDER BY products DESC
LIMIT 10
```

### Build the chart

1. **Add a chart → Bar chart → Horizontal**
2. **Dimension:** `brand`
3. **Metric:** `products`
4. **Sort:** `products` descending
5. **Style:** single color → `#EF553B` (the red you used in Plotly)

---

## 10 · Tile 5 — Top Additive Families

Another complex UNNEST + mapping + regex. **Custom Query required.**

SQL (also in `docs/looker-studio-queries/tile5_additive_families.sql`):

```sql
WITH mapping AS (
  SELECT code, category FROM UNNEST([
    STRUCT('e100' AS code, 'Curcumin' AS category),
    STRUCT('e101', 'Riboflavin'),
    STRUCT('e150', 'Caramel Colors'),
    STRUCT('e160', 'Carotenes & Carotenoids'),
    STRUCT('e161', 'Carotenes & Carotenoids'),
    STRUCT('e162', 'Beetroot Red'),
    STRUCT('e163', 'Anthocyanins'),
    STRUCT('e200', 'Sorbates'), STRUCT('e202', 'Sorbates'), STRUCT('e203', 'Sorbates'),
    STRUCT('e210', 'Benzoates'), STRUCT('e211', 'Benzoates'),
    STRUCT('e212', 'Benzoates'), STRUCT('e213', 'Benzoates'),
    STRUCT('e220', 'Sulphites'), STRUCT('e221', 'Sulphites'), STRUCT('e222', 'Sulphites'),
    STRUCT('e223', 'Sulphites'), STRUCT('e224', 'Sulphites'), STRUCT('e226', 'Sulphites'),
    STRUCT('e227', 'Sulphites'), STRUCT('e228', 'Sulphites'),
    STRUCT('e249', 'Nitrites & Nitrates'), STRUCT('e250', 'Nitrites & Nitrates'),
    STRUCT('e251', 'Nitrites & Nitrates'), STRUCT('e252', 'Nitrites & Nitrates'),
    STRUCT('e300', 'Ascorbic Acid & Ascorbates'), STRUCT('e301', 'Ascorbic Acid & Ascorbates'),
    STRUCT('e302', 'Ascorbic Acid & Ascorbates'), STRUCT('e304', 'Ascorbic Acid & Ascorbates'),
    STRUCT('e306', 'Tocopherols'), STRUCT('e307', 'Tocopherols'),
    STRUCT('e308', 'Tocopherols'), STRUCT('e309', 'Tocopherols'),
    STRUCT('e260', 'Acetates'), STRUCT('e261', 'Acetates'),
    STRUCT('e262', 'Acetates'), STRUCT('e263', 'Acetates'),
    STRUCT('e270', 'Lactates'), STRUCT('e325', 'Lactates'),
    STRUCT('e326', 'Lactates'), STRUCT('e327', 'Lactates'),
    STRUCT('e330', 'Citric Acid & Citrates'), STRUCT('e331', 'Citric Acid & Citrates'),
    STRUCT('e332', 'Citric Acid & Citrates'), STRUCT('e333', 'Citric Acid & Citrates'),
    STRUCT('e334', 'Tartrates'), STRUCT('e335', 'Tartrates'),
    STRUCT('e336', 'Tartrates'), STRUCT('e337', 'Tartrates'),
    STRUCT('e338', 'Phosphates'), STRUCT('e339', 'Phosphates'), STRUCT('e340', 'Phosphates'),
    STRUCT('e341', 'Phosphates'), STRUCT('e343', 'Phosphates'),
    STRUCT('e450', 'Phosphates'), STRUCT('e451', 'Phosphates'), STRUCT('e452', 'Phosphates'),
    STRUCT('e322', 'Lecithins'),
    STRUCT('e400', 'Alginates'), STRUCT('e401', 'Alginates'), STRUCT('e402', 'Alginates'),
    STRUCT('e403', 'Alginates'), STRUCT('e404', 'Alginates'), STRUCT('e405', 'Alginates'),
    STRUCT('e406', 'Agar'),
    STRUCT('e407', 'Carrageenan'),
    STRUCT('e410', 'Gums'), STRUCT('e412', 'Gums'), STRUCT('e413', 'Gums'),
    STRUCT('e414', 'Gums'), STRUCT('e415', 'Gums'), STRUCT('e417', 'Gums'),
    STRUCT('e418', 'Gums'),
    STRUCT('e420', 'Polyols'), STRUCT('e421', 'Polyols'),
    STRUCT('e440', 'Pectins'),
    STRUCT('e460', 'Celluloses'), STRUCT('e461', 'Celluloses'), STRUCT('e463', 'Celluloses'),
    STRUCT('e464', 'Celluloses'), STRUCT('e465', 'Celluloses'), STRUCT('e466', 'Celluloses'),
    STRUCT('e471', 'Mono- & Diglycerides'), STRUCT('e472', 'Mono- & Diglycerides'),
    STRUCT('e500', 'Carbonates'), STRUCT('e501', 'Carbonates'),
    STRUCT('e503', 'Carbonates'), STRUCT('e504', 'Carbonates'),
    STRUCT('e551', 'Silicates'), STRUCT('e552', 'Silicates'),
    STRUCT('e553', 'Silicates'), STRUCT('e554', 'Silicates'),
    STRUCT('e620', 'Glutamates'), STRUCT('e621', 'Glutamates'), STRUCT('e622', 'Glutamates'),
    STRUCT('e623', 'Glutamates'), STRUCT('e624', 'Glutamates'), STRUCT('e625', 'Glutamates'),
    STRUCT('e950', 'Sweeteners'), STRUCT('e951', 'Sweeteners'), STRUCT('e952', 'Sweeteners'),
    STRUCT('e953', 'Sweeteners'), STRUCT('e954', 'Sweeteners'), STRUCT('e955', 'Sweeteners'),
    STRUCT('e960', 'Sweeteners'), STRUCT('e961', 'Sweeteners'), STRUCT('e962', 'Sweeteners'),
    STRUCT('e965', 'Polyols'), STRUCT('e966', 'Polyols'),
    STRUCT('e967', 'Polyols'), STRUCT('e968', 'Polyols'),
    STRUCT('e1400', 'Modified Starches'), STRUCT('e1401', 'Modified Starches'),
    STRUCT('e1402', 'Modified Starches'), STRUCT('e1403', 'Modified Starches'),
    STRUCT('e1404', 'Modified Starches'), STRUCT('e1410', 'Modified Starches'),
    STRUCT('e1412', 'Modified Starches'), STRUCT('e1413', 'Modified Starches'),
    STRUCT('e1414', 'Modified Starches'), STRUCT('e1420', 'Modified Starches'),
    STRUCT('e1422', 'Modified Starches'), STRUCT('e1440', 'Modified Starches'),
    STRUCT('e1442', 'Modified Starches'), STRUCT('e1450', 'Modified Starches'),
    STRUCT('e1451', 'Modified Starches')
  ])
),
exploded AS (
  SELECT
    REGEXP_EXTRACT(
      REPLACE(LOWER(tag), 'en:', ''),
      r'^(e\d+)'
    ) AS base_code
  FROM `YOUR_PROJECT.foodmythbuster.stg_products`,
    UNNEST(additives_tags) AS tag
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
  STRING_AGG(DISTINCT UPPER(base_code), '/' ORDER BY UPPER(base_code)) AS codes
FROM joined
GROUP BY category
ORDER BY occurrences DESC
LIMIT 5
```

### Build the chart

1. **Add a chart → Bar chart → Horizontal**
2. Create a calculated field in this data source to combine codes + category:
   ```
   CONCAT(codes, " (", category, ")")
   ```
   Name it `label`.
3. **Dimension:** `label`
4. **Metric:** `occurrences`
5. **Sort:** `occurrences` descending

### The health-concern references

Looker Studio doesn't support dynamic markdown with links like Streamlit's `st.markdown()`. Your options:

- **Text box:** Add a text box below the chart and manually type the references:
  > - **Phosphates** — Concerns for kidney issues and coronary heart disease risk. [source](https://pmc.ncbi.nlm.nih.gov/articles/PMC3278747/)
  > - **Sweeteners** — Linked to higher cardiovascular disease risk. [source](https://www.bmj.com/content/378/bmj-2022-071204)

  Looker Studio text boxes support clickable hyperlinks (select text → Ctrl+K → paste URL).

- **Embed an image:** design a small reference card in Canva/Figma and embed it.

---

## 11 · Tile 6 — Temporal Gap (Line Chart)

**Custom Query** needed because of the conditional aggregation (`AVG(IF(...))`).

SQL (also in `docs/looker-studio-queries/tile6_temporal.sql`):

```sql
SELECT
  EXTRACT(YEAR FROM created_date) AS created_year,
  AVG(IF(has_health_claim, additives_count, NULL)) AS avg_deceptive,
  AVG(IF(NOT has_health_claim, additives_count, NULL)) AS avg_non_deceptive,
  COUNTIF(has_health_claim) AS deceptive_n,
  COUNTIF(NOT has_health_claim) AS non_deceptive_n
FROM `YOUR_PROJECT.foodmythbuster.stg_products`
WHERE is_ultra_processed
  AND created_date BETWEEN DATE '2020-01-01' AND DATE '2024-12-31'
GROUP BY created_year
ORDER BY created_year
```

### Build the chart

1. **Add a chart → Time series** (line chart)
2. **Dimension:** `created_year` (set type to **Number**, not Date — it's just a year integer)
3. **Metric 1:** `avg_deceptive`
4. **Metric 2:** `avg_non_deceptive`
5. **Style:**
   - Series 1 color: `#EF553B` (red — deceptive)
   - Series 2 color: `#636EFA` (blue — non-deceptive)
   - Enable data point markers (dots)
   - Line weight: 3px

> **The 2023 dashed vertical line** (ANVISA regulation marker): Looker Studio
> doesn't support arbitrary `vline` annotations. Workaround: add a **reference
> line** on the X axis at value 2023, or add a text annotation box positioned
> over the chart at the 2023 mark.

### Sample-size caption

Add a **Table** chart below the line chart:
- Dimensions: `created_year`
- Metrics: `deceptive_n`, `non_deceptive_n`
- This gives viewers the exact sample sizes per year, same as your `st.caption()`.

---

## 12 · Styling & Layout

### Page setup

1. **Theme → Custom**: pick a clean theme or start from "Simple Dark" / "Simple Light"
2. **Page size:** set to **1200 x 2400** (tall scrolling report) or use **multiple pages** (one tile per page, like slides)
3. Background: white or very light gray (`#FAFAFA`)

### Replicating the Streamlit look

| Streamlit element | Looker Studio equivalent |
|---|---|
| `st.title()` | Text box, 24pt bold |
| `st.subheader()` | Text box, 16pt bold, placed above each chart |
| `st.markdown()` | Text box with formatted text |
| `st.divider()` | Line shape (Insert → Line) |
| `st.info()` | Rounded rectangle shape with light-blue fill + text box inside |
| `st.caption()` | Text box, 10pt, gray color |
| `st.sidebar` | No exact equivalent — use a **filter bar** at the top, or a left-column layout |

### Adding interactivity (bonus, not in Streamlit)

Looker Studio makes it easy to add filters viewers can play with:

1. **Add a control → Drop-down list**
   - Control field: `nutriscore_grade`
   - Now viewers can filter the entire page to a single Nutri-Score grade
2. **Date range control** — let viewers pick a custom date window for the temporal chart
3. **Cross-filtering:** In chart settings, enable "Cross-filter" — clicking a bar in one chart filters all other charts on the page. This is like having `st.selectbox` wired to every query at once.

---

## 13 · Publishing & Sharing

This is where Looker Studio shines vs Streamlit (no server to deploy):

1. Click **Share** (top right)
2. Options:
   - **Invite people** by email (like Google Docs)
   - **Get link** → "Anyone with the link can view"
   - **Embed** → generates an `<iframe>` you can paste into a website
   - **Download as PDF** → static snapshot
3. The report is **live** — viewers see fresh data (cached ~12h). No `streamlit run` needed.

### Scheduling email delivery

1. **Share → Schedule email delivery**
2. Set frequency (daily, weekly, monthly)
3. Recipients get a PDF snapshot of the dashboard in their inbox

---

## 14 · Limitations vs Streamlit

Be aware of what you lose moving from code to a visual tool:

| Feature | Streamlit | Looker Studio |
|---|---|---|
| Arbitrary Python logic | Full Python | None — SQL + formula language only |
| Custom color scales per bar | `color_continuous_scale="RdYlGn_r"` | Limited (conditional formatting rules, not gradients) |
| Vertical reference lines | `fig.add_vline()` | Workaround only (reference lines or text boxes) |
| Dynamic markdown with links | `st.markdown(f"[source]({url})")` | Text boxes with manual hyperlinks |
| Array operations in formulas | N/A (done in SQL) | Must use Custom Query — Looker formulas can't UNNEST |
| Cost control per query | `maximum_bytes_billed` | Not configurable per chart — rely on caching + small table size |
| Version control | `git diff app.py` | No code files — report state lives in Google's cloud (you can duplicate reports as "versions") |

### What you gain

- **Zero deployment** — no server, no Docker, no Cloud Run
- **Google-native sharing** — share like a Google Doc
- **Auto-refresh** — data updates when BigQuery updates, no `cache_data` wiring
- **Non-technical viewers** — anyone with a browser can explore filters without running Python
- **Scheduled emails** — built-in PDF delivery

---

## Quick Reference: Data Sources Summary

| Tile | Data Source Type | SQL File |
|---|---|---|
| KPI Scorecards | Table: `stg_products` | — |
| 1 · Nutri-Score Paradox | Table: `stg_products` + calculated fields | — |
| 2 · Health Claims | Custom Query | `tile2_health_claims.sql` |
| 3 · Category Groups | Custom Query | `tile3_category_groups.sql` |
| 4 · Top Brands | Custom Query | `tile4_top_brands.sql` |
| 5 · Additive Families | Custom Query | `tile5_additive_families.sql` |
| 6 · Temporal Gap | Custom Query | `tile6_temporal.sql` |

All SQL files are in `docs/looker-studio-queries/`. Replace `YOUR_PROJECT` with your GCP project ID before pasting.
