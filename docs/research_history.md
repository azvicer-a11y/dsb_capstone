# Research history

This document shows how the project developed. It separates my original work from the later revisions, which were prepared with AI assistance (see the README, *Contributions and acknowledgements*). It does not hide earlier problems: finding and fixing them is part of the research.

The original notebooks are kept in `archive/original_notebooks/`, and the original README in `archive/original_docs/`.

---

## Part A: My original work

### A1. Idea and data collection
- **Original idea (earlier phase).** I first described VALORA AI as a future decision-support tool for professional valuers in Montenegro. The goals were to estimate property values, compare price per m² across cities, analyse market patterns, explore time trends and build an application. That broader vision is recorded in `archive/original_docs/README_original.md`. **The final project is limited to the research questions** about asking prices and prediction uncertainty. It contains no application.
- **Data I collected and assembled:**
  - **1,986 real online adverts** from Realitica (incl. its Adriatic section) and Estitor;
  - **927 rows from professional appraisal reports**;
  - **4,000 artificial rows** (2,000 "simulated" and 2,000 "generated"), which I created for early experiments.
- **Data preparation** in Google Colab:
  - a combined file `VALORA_AI_FINAL_COLAB.csv` (6,913 rows);
  - a partly cleaned file `valora_cleaned_step2.csv` (4,036 rows), with `property_type_clean` and `city_clean`;
  - a manual check column `provjera`, in which I had already flagged suspicious prices ("PROVJERITI: cijena", "sumnjivo niska cijena").

### A2. First exploration (`01_EDA.ipynb`)
- **Cleaning:** I kept real apartments only, removed duplicates by ID, and applied ranges (price €10,000–2,000,000, area 15–350 m², €300–15,000 per m²). Result: **1,473 → 1,432 apartments**.
- **Analysis:** I built a city column by matching city names inside the location text, and charted the price and area distributions, the median €/m² per city (≥ 10 listings) and the correlations.
- **Observations:** price and area are strongly related; location matters; asking prices are not sale prices.

### A3. Five modelling experiments (one notebook each, same 12-section structure)
All of them used `valora_cleaned_step2.csv`, 1,473 real apartments, inputs area + rooms + city, and an 80/20 random split (seed 42).

| Experiment | Saved test MAE | R² |
|---|---|---|
| Mean-price baseline | €107,905 | −0.00 |
| Linear Regression | €68,637 | 0.49 |
| Random Forest (min leaf 2) | €71,129 | 0.39 |
| Random Forest + Feature Engineering (area², area per bedroom, size group) | €71,302 | 0.40 |
| Optimized Random Forest (GridSearchCV on the training data) | €71,179 | 0.40 |
| Extra Trees (tuned, GridSearchCV) | **€67,535** | 0.52 |

### A4. Combined comparison (`VALORA_AI_ALL_MODELS.ipynb`)
- All models in one notebook on the same split. Linear Regression had the lowest test MAE there (€68,637), because the Extra Trees in that notebook was **not tuned** (€74,588).
- The notebook already listed limitations: asking prices are not sale prices, the test data had been looked at, and a fresh dataset is needed.

**Reproduction check.** In the later audit, every saved number above was reproduced **exactly** by re-running the original code locally.

---

## Part B: Problems found in the audit

| # | Problem | Effect |
|---|---|---|
| B1 | **2,000 simulated rows were labelled `data_source = "Online listing"`, `is_synthetic = False`** | A filter on those columns alone would have mixed artificial rows into "real" data. The original notebooks were not affected, because they also filtered `data_origin` |
| B2 | **EDA and modelling used different data** (EDA: a separate upload not in the repository, 1,432 rows; modelling: 1,473 rows) | The two notebooks did not describe the same population, and the EDA could not be reproduced exactly |
| B3 | **36 rentals** (€1,450–2,750 for 25–78 m²) were in the modelling data; the quality ranges were only flagged, not applied | Monthly rents were predicted as if they were sale prices |
| B4 | **47 exact re-posts** and **cross-platform repeats** of the same flat | The same flat could be in both training and test data (leakage) |
| B5 | **703 unknown cities** in modelling, although the location text named the municipality for most of them (e.g. 128 × "Budva,") | The most important input after size was missing for almost half the data |
| B6 | City names matched as **substrings** | "Bar" can match inside other place names |
| B7 | The **final model was chosen by lowest test MAE**, and the error analysis used Extra Trees, not the winner | Test results influenced the choice, so the reported score was optimistic |
| B8 | 7 houses typed as apartments, 2 price parsing errors, 1 apartment of 1 m² | Small data errors |
| B9 | Studios (*garsonjera*) stored as missing rooms | A real property trait was treated as unknown |
| B10 | No requirements file, no automatic tests, Colab-only file upload | The work could not be reproduced |
| B11 | Sensitive file paths of appraisal reports in the raw CSV | Privacy risk (see `privacy_and_data_rights.md`) |
| B12 | No dates in the data | The original ARIMA and trend goal cannot be met with these data |

---

## Part C: Revisions of the main analysis

### C1. One cleaning procedure (`src/valora_prep.py`, `notebooks/01_eda.ipynb`)
- **Provenance** is decided from **all** label columns together. Tests ensure that no simulated, generated or appraisal row can reach the model.
- **One fixed order of rules,** each with a count: not apartment (513) → misclassified type (7) → rentals (36) → price errors (2) → invalid area (1) → exact re-posts (47, keeping the oldest ID) → **1,380** valid listings.
  - **1,376** of these lie inside my original ranges (primary population).
  - 4 are valid luxury listings kept for a sensitivity check.
- **Rooms and bathrooms:** studios are set to 0 rooms. Bathrooms are not used, because they exist on one platform only.

### C2. Location
- Whole-token reading of the location text, with no substring matching.
- 15 settlement names (e.g. Igalo, Bečići) are mapped to their municipality, each verified against the official Monstat 2023 settlement register.
- Ambiguous names stay Unknown: Zelenika, Prijevor, Luštica, Centar.
- **Result:** unknown city went from **668** (platform field) to **289** (explicit text) to **33** (with settlements) of 1,376 listings, with **no** contradiction to any existing city.

### C3. Duplicates
- **47 identical re-posts** (same platform and content, different ID) were **removed**, keeping the oldest ID.
- **74 groups of probable duplicates** (172 listings with the same city, neighbourhood, price and area; 17 groups across two platforms) were **kept**, but each group is always placed on the same side of every train/test split and CV fold (group-aware splitting).
- Detection is heuristic and exact-match only. Repeated adverts with small changes may remain.

### C4. Evaluation
- **Protocol written before training:**
  - group-aware 80/20 split;
  - group-aware 5-fold CV on the development data;
  - MAE as the main metric;
  - a selection rule based on CV MAE plus a 1-standard-error simplicity rule.

  The test set was used once, after the choice.
- **Baselines:** three, including the practical rule "city median €/m² × area".
- **Models:** all five original model types were re-evaluated, plus Ridge, Gradient Boosting and log-target variants. Tuning is nested inside the CV.
- **Location experiment:** a controlled experiment measured what each location step is worth.

### C5. Result of the main analysis
- Under the pre-registered rule, the **city €/m² × area rule** was chosen. No machine-learning model beat it reliably on mean absolute error.
- *Corrected later:* on the test sample the tree models had a better RMSE and R², but cross-validation on the development data did **not** confirm this (see Part D).

### C6. Why the new numbers differ from the old ones
- The new test MAE values (≈ €55–61k for the models) are lower than the old ones (≈ €68–75k).
- **This is mostly because the data and the test set changed:** rentals and errors were removed, and repeats can no longer leak. It is **not** proof that the algorithms became better.
- The fair before/after comparison is the controlled location experiment, which changes one thing at a time on the same rows and folds.

### C7. Not done
- No time series or ARIMA (no dates).
- No application.
- No use of the appraisal reports.

---

## Part D: Later exploratory phases

All three phases used **only the 1,098 development listings and the same 5 group-aware folds**, with plans fixed in advance. Records are in `docs/research/`. Those records are working documents from the time and keep their original wording.

| Phase | Question | Result |
|---|---|---|
| D1. Research extension | Can ML improve on the city €/m² rule? (hybrid residual learning, €/m² targets, room-count estimation, city × area effects, neighbourhood information) | **No reliable gain.** Hybrids: nested tuning chose near-zero corrections. Rooms: estimable from area (≈ 0.3 rooms error), but no price gain. Neighbourhood information (mainly Podgorica) gave the only weak signal (CV MAE €49,502 vs €50,527) and remains exploratory |
| D2. Correction | Do tree models really control large errors better? | **No.** This was seen on the test set only; in CV the Random Forest had a *lower* R² (0.563) than the rule (0.582). The statement was corrected |
| D3. Opportunity audit | Which other questions can these data answer? (no models trained) | Clustering, classification targets, house prices (no land area), rents (37 adverts), anomaly detection and time series were judged not justified. Prediction ranges ranked first |
| D4. Uncertainty research | How reliably can uncertainty be quantified? (8 interval methods) | Linear quantile regression (G3a) chosen: 78.9% CV coverage at 80% nominal, median relative width 64%, even coverage across cities. Conformal intervals around the rule covered ≈ 80% overall, but unevenly by city |
| D5. Final consolidation | – | G3a was added to `02_modelling.ipynb` (sections 8.8–10.2), with **one pre-registered retrospective test check** of G1 and G3a (protocol locked before execution). Test coverage: 74.8% at 80% for both methods; 86.0% (G3a) and 85.6% (G1) at 90%. Reported as it is; nothing was changed afterwards |

**How the research question evolved:**

| Stage | Question |
|---|---|
| Original | *Can ML estimate apartment asking prices in Montenegro?* |
| After the main results | *Can ML improve on a simple city €/m² rule, and how much does location quality contribute?* |
| Final | *How accurately can we estimate apartment asking prices in Montenegro, and how reliably can we quantify the uncertainty of these predictions?* |

The later questions were formulated **after** earlier results. They are follow-up questions, not hypotheses set in advance.

**Unchanged throughout:**
- the cleaning rules;
- the population (1,376);
- the split and folds;
- the point-estimation method;
- its selection rule.
