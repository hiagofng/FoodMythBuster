# Looker Studio — Tile Titles & Descriptions

Copy-paste these into **text boxes** in Looker Studio, placed above or below each chart.
For the title, use bold/large font (~16pt). For the description, use regular/small font (~10–11pt).

---

## Dashboard Header

**Title:**
FoodMythBuster

**Subtitle:**
Are "healthy" food labels a lie? Investigating whether front-of-pack health claims align with NOVA classification (degree of industrial processing).

**Scope note (small caption, top or sidebar):**
Scope: Brazil-only products from Open Food Facts, filtered to rows with NOVA classification.

---

## KPI Scorecards

Each scorecard label should be self-explanatory:

| Scorecard | Label |
|---|---|
| 1 | Total Products |
| 2 | NOVA 4 (Ultra-Processed) |
| 3 | With Health Claim |
| 4 | Deceptive (Claim + NOVA 4) |

---

## Tile 1 — The Nutri-Score Paradox

**Title:**
The Paradox: Nutri-Score A/B but Ultra-Processed

**Description (text box above the charts):**
What is Nutri-Score? A front-of-pack nutrition label developed in France (2017) and adopted across several European countries. It grades packaged foods from A (best) to E (worst) based on nutrient density per 100 g — sugar, salt, saturated fat and calories weighed against fibre, protein, fruits and vegetables. It rates nutritional composition, not degree of processing — so a product reformulated to score well on paper can still be ultra-processed (NOVA 4), which is exactly what this chart reveals.

**Chart A title:**
Products by Nutri-Score: Total vs NOVA 4

**Chart B title:**
% Ultra-Processed by Nutri-Score Grade

---

## Tile 2 — Green Label but Ultra-Processed

**Title:**
% NOVA 4 with Health Claim

**Description (text box above the chart):**
Of all products carrying a front-of-pack health claim, a significant share are classified NOVA 4 (ultra-processed). Below, the percentage of NOVA 4 broken down by each individual claim — organic, light, zero-sugar, high-protein, and others. The number on each bar shows total products carrying that claim.

**Chart title:**
% Ultra-Processed Among Products Carrying Each Health Claim

---

## Tile 3 — Healthy Junk by Category Group

**Title:**
"Healthy Junk" by Category Group

**Description:**
Products that carry at least one health claim AND are classified NOVA 4, grouped by food category. These are the categories where "deceptive labeling" is most concentrated — products marketed as healthy that are, by processing standards, ultra-processed.

**Chart title:**
Deceptive Products (Health Claim + NOVA 4) by Category Group

---

## Tile 4 — Top Brands

**Title:**
Top Brands Selling "Healthy" Ultra-Processed Products

**Description:**
The 10 brands with the most products that simultaneously carry a front-of-pack health claim and are classified NOVA 4 (ultra-processed). Brand names are normalized (accent-stripped, lowercased) to avoid duplicates from inconsistent labeling in Open Food Facts.

**Chart title:**
Top 10 Brands Selling NOVA 4 Products Under Health Claims

---

## Tile 5 — Top Additive Families

**Title:**
Top 5 Additive Families in Deceptive Products

**Description:**
E-numbers extracted from products that are NOVA 4 and carry a health claim, grouped by functional family. Roman-numeral suffixes (e.g. E450i, E450ii) are collapsed to the base code. These are the chemical families most present in products sold as "healthy" but classified as ultra-processed.

**Chart title:**
Top 5 Additive Families in NOVA 4 Products with Health Claims

**Health concerns (text box below the chart):**
- Phosphates — Concerns for kidney issues and coronary heart disease risk. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3278747/
- Polyols — Association with cardiovascular and coronary disease, and gut-microbiota disruption. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12767680/
- Sweeteners — Linked to higher cardiovascular disease and coronary disease risk. Source: https://www.bmj.com/content/378/bmj-2022-071204
- Sorbates — Association with higher cancer risk. Source: https://pubmed.ncbi.nlm.nih.gov/41500678/

(Add the URLs as clickable hyperlinks: select the "Source" text → Ctrl+K → paste the URL.)

---

## Tile 6 — Temporal Gap

**Title:**
The Widening Gap: Deceptive NOVA 4 Use More Additives Over Time

**Description:**
Among NOVA 4 products, the average number of additives per product, split by whether they also carry a health claim. Products marketed as "healthy" consistently contain more additives than their non-claim counterparts. The 2023 marker is when ANVISA RDC 429/2020 mandatory front-of-pack warning labels became enforceable in Brazil — sample sizes jump that year, so read the trend carefully.

**Chart title:**
Avg Additives per Product — NOVA 4 with vs without Health Claim

**Caption (small text below the chart):**
Add a Table chart showing created_year, deceptive_n, and non_deceptive_n to display sample sizes per year.

---

## Footer

**Caption (text box at the bottom):**
Data: Open Food Facts (https://world.openfoodfacts.org) · NOVA classification: Prof. Carlos Monteiro, University of São Paulo · Built for Data Engineering Zoomcamp (https://github.com/DataTalksClub/data-engineering-zoomcamp)
