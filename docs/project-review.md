# FoodMythBuster — Rubric Review & Improvement Plan

## Rubric snapshot (DataTalksClub Zoomcamp)

Max = **28 points** + up to **9 bonus** from peer reviews. Stream vs Batch is either/or, not both.

| # | Criterion | Max | Your current standing | Confidence |
|---|---|---|---|---|
| 1 | Problem description | 4 | **4** — README explains the NOVA/health-claim gap with a cited study and a concrete stat (34.3%). | High |
| 2 | Cloud + IaC | 4 | **4** — GCP + Terraform (bucket, dataset, SA, IAM). Key-less SA impersonation is above average. | High |
| 3 | Batch orchestration | 4 | **3 – 4** — Bruin schedules the ingest, but `pipeline.yml` only contains the ingest. dbt is run manually in the README. | **Risky** |
| 4 | Data warehouse | 4 | **4** — Partition + cluster choices are explicitly mapped to dashboard tiles. | High |
| 5 | Transformations | 4 | **4** — dbt + 9 tests. Derived flags (`is_deceptive`, `has_health_claim`, `matched_health_claims`) are real business logic, not filler. | High |
| 6 | Dashboard | 4 | **4** — Looker Studio, 6 tiles (1 temporal, 5 categorical). | High |
| 7 | Reproducibility | 4 | **3 – 4** — README is thorough, but multi-phase manual steps leave room for a reviewer to trip up. | **Risky** |

**Realistic expected score: 26–28/28** before peer-review bonus. Two categories (orchestration, reproducibility) are the swing seats.

---

## Answers to your direct questions

### "Is Docker necessary?"
**No.** The rubric has no container category. The 32-point reference project (`energy-risk-dashboard-smes`) ships no Docker. Adding it is medium effort for near-zero rubric gain. Skip it — unless you want it for dashboard deployment (Cloud Run), which is a different motivation.

### "Would Kestra add anything?"
**Only if you have spare time.** The rubric is tool-agnostic — it asks for "multiple steps in the DAG, uploading data to data lake." Bruin satisfies that in principle.

The real risk is **peer recognition**: zoomcamp reviewers learned Kestra in the course and may not immediately read Bruin as "orchestration." Two options ordered by effort:

- *Cheap:* keep Bruin, but add the dbt asset to `pipeline.yml` so `bruin run pipelines/foodmythbuster` executes the full DAG in one command. Add a Mermaid or screenshot of the DAG to the README.
- *Expensive:* port to Kestra. ~1 day of work. Immediate reviewer recognition. Only worth it if orchestration is your weakest tile and you're chasing the bonus.

### "Is any transformation just filling the gap?"
**No filler.** Every derived column is referenced by a dashboard tile (confirmed in `schema.yml` + your Data Modeling section). The only optics issue is that you have **one** dbt model. That can read as "a thin staging layer" to a reviewer — see improvement #2 below.

---

## Improvements ranked by effort / gain

### Tier 1 — Do these (cheap, directly de-risks points)

**1. Wire dbt into the orchestrator.** *~30 min.*
`pipeline.yml` currently schedules `@daily` but the DAG has one node. Add a Bruin SQL or dbt asset so the scheduled run = ingest + build + test. Today a reviewer reading `pipeline.yml` sees one step, not "multiple steps in a DAG."

**2. Add one mart model.** *~1 hour.*
e.g. `mart_deceptive_by_category.sql` pre-aggregating the Tile 3 query. Benefits:
- Dashboard queries read a tiny pre-aggregated table → sub-second tiles and a near-zero query bill.
- Turns the dbt layer from "staging only" into "staging → mart," which is what reviewers pattern-match for full transformation points.
- Gives you a second place to demonstrate dbt features (ref, incremental, or a singular test).

**3. Put a screenshot (or GIF) of the Looker dashboard in the README.** *~10 min.*
Reviewers skim. A hero image is the cheapest possible signal that the dashboard exists and has real content. Link the public Looker URL next to it.

**4. Single-command runner.** *~20 min.*
A `Makefile` with `make infra`, `make ingest`, `make transform`, `make all`. Reproducibility points hinge on the reviewer succeeding on the first try. Seven exported env vars in Phase 3 is friction — move them into a `.env` + `make` target.

### Tier 2 — Consider (non-trivial, real upside)

**5. Deploy the dashboard (or publish the Looker Studio link).** *~15 min for Looker public share, ~2 h for Streamlit on Cloud Run.*
Your README has this as an open checkbox. Looker Studio "anyone with the link" is free and reviewer-friendly. A live dashboard is a strong reproducibility signal even though it isn't a rubric line item.

**6. Move health-claim list to a dbt seed.** *~30 min.*
The 14 hardcoded `en:*` labels inside `stg_products.sql` become `seeds/health_claims.csv`. Small change, but showcases a dbt feature and makes the list editable without a model change.

**7. Add dbt docs.** *~15 min.*
`dbt docs generate && dbt docs serve` + a screenshot in the README. Tiny effort, tangible polish.

### Tier 3 — Skip unless you're chasing bonus points

**8. Docker.** Skip per above.
**9. Streaming.** It's OR with batch in the rubric — building both won't raise your score.
**10. Kestra migration.** Only if Tier 1 item #1 doesn't land.
**11. CI/CD.** Not in the rubric. Nice signal but low yield for the time.

---

## Concrete gaps I'd close before submitting

- `pipeline.yml` has one asset; add the dbt/staging step so the DAG has ≥2 nodes and runs end-to-end on schedule.
- Only one dbt model exists; add one mart.
- README doesn't show the dashboard; add an image.
- Seven `export` lines for a cloud run; wrap in a `Makefile` or `.env.example`.
- `docs/looker-studio-guide.md` and tile descriptions exist — link them from the main README so a reviewer finds them.

## What's already better than the 32-point reference

- Partition/cluster choices explicitly justified tile-by-tile (their README lists clustering; yours explains *why*).
- dbt tests present (9 vs. limited testing there).
- IaC uses SA impersonation instead of keys — genuinely better practice.
- Dual-backend pipeline (DuckDB local / BigQuery cloud) demonstrates engineering rigor.

The delta that could have cost them points (no real orchestration) is exactly the one you should close on your side.
