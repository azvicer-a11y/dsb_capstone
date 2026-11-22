# VALORA AI: Research-opportunity audit

**Type:** data audit and research plan only. **No model was trained.** `valora_ai/` and `research_extension/` were not changed (checksums in `checks/`).
**Data used:**
- inventory counts and missingness: all 1,986 real listings (no prices involved);
- every price-based statistic: only the **1,098 development listings**, so the 278 test listings could not influence the choice of a research question.

Script: `audit_inventory.py`. Full output: `results/audit_output.txt`.
**All proposals are exploratory:** the data have already been analysed several times.

## 1. Data inventory

### 1.1 Columns (real listings, n = 1,986)

| Column | Coverage | Usable for research? |
|---|---|---|
| price, area, location text | 100% | Yes: core |
| city (after cleaning, apartments) | 97.6% | Yes |
| neighbourhood / settlement below city level | 72% of development apartments; 37 places with ≥ 10 listings (768 primary listings) | Yes, but dominated by Estitor/Podgorica (capped at about 20 per neighbourhood) |
| rooms (`sobe`) | 73% overall (Estitor 94%, Realitica 66%, Adriatic 90%) | Yes, but largely redundant with area (Spearman 0.81) |
| bathrooms (`kupatila`) | 19%, **Estitor only** | No: encodes the platform |
| description (`opis`) | 28%, Estitor + Adriatic only; some contain prices and names | No (leakage, privacy, platform-specific) |
| student's check flag (`provjera`) | 100% | Yes, as weak labels for data-quality research |
| dates | **none** | No time analysis possible |
| floor, condition, year built, land area | Only in **simulated** rows; never in real ones | No |

### 1.2 Property types, sale and rent (real listings)

| | Sale | Rent (< €10k) | Total |
|---|---|---|---|
| Apartment | 1,437 | 36 | 1,473 |
| House / villa | 449 | 1 | 450 |
| Unclear / commercial | 63 | 0 | 63 |

- **Rent:** only 37 rental adverts, nearly all apartments in Ulcinj and Bar, with no reliable area or furnishing information. **A rental study is not feasible.**
- **Houses:**
  - 444 usable sale listings, all from Realitica (incl. Adriatic), spread thinly over cities (17–58 per city).
  - Rooms are known for only 49%, and there are no bathrooms.
  - **There is no real land area**: `land_area_m2` is empty for every real row, and only simulated rows have land. Land is usually a major part of a house's price.
  - Median area is 179 m², and some areas may include land or be parsing errors.
  - **A separate house price model is not justified.** At most, a short descriptive comparison is possible.
- **Appraisals:** 927 rows, of which 676 have an unknown type and only 137 have both price and area. The years are irregular, the labels are unverified, and there are privacy risks. **Not for now.**

### 1.3 Apartments (primary, n = 1,376)
- **Coastal vs continental:** 727 coastal, 616 continental, 33 unknown. "Coastal" means the six coastal municipalities, a geographic fact.
- **Development data (€/m²):**

| | Median | 80% range |
|---|---|---|
| Coastal | €3,333 | €2,292–5,208 |
| Continental | €2,702 | €1,941–3,609 |

- **Within-city dispersion is large.** The 80% range of €/m² spans:

| City | Range as % of the city median |
|---|---|
| Nikšić | 37% |
| Cetinje | 40% |
| Podgorica | 52% |
| Herceg Novi | 84% |
| Budva | 85% |
| Tivat | 97% |

  **The city explains the level, but most of the uncertainty is within the city.**

## 2. Assessment of each direction

### 2.1 Clustering (unsupervised segmentation)
- **Question:** *Can unsupervised ML identify meaningful market segments within apartment listings?*
- **Data reality:**
  - Without price there are effectively **two** informative features: size (area, plus rooms, which correlates 0.81 with area) and location (city; neighbourhood mainly in Podgorica).
  - Platform must not be used, because it reflects the sampling.
- **Approach A** (no price in clustering): K-Means, GMM or hierarchical clustering on log area, rooms and one-hot city.
  - The result would almost certainly be size bands × city groups, i.e. a known partition.
  - City one-hot dominates distance-based methods unless it is down-weighted. That weighting would be an arbitrary choice that determines the result.
- **Approach B** (price or €/m² included): descriptive only, e.g. a GMM on log area and log €/m².
  - It could show a coastal high-€/m² component.
  - It would not be more informative than quantiles of €/m² by city and size.
  - It must never be presented as price prediction.
- **Evaluation if done:**
  - silhouette and Davies–Bouldin index;
  - stability (adjusted Rand index across bootstrap resamples and seeds);
  - **the decisive test:** compare with a naive partition (city group × size tercile). If the clusters do not beat the naive partition in stability and interpretability, they add nothing.
- **Expected limitations:** low dimensionality, a platform-dependent sample, and no attributes such as condition or view.
- **Feasibility:** high technically, but **low scientific value**.
- **Presentation value:** attractive visuals, but a weak story. Risk of naming clusters without evidence.
- **Verdict: not recommended as a main direction.** At most a small check that "clusters ≈ size × city" can be reported as a negative result.

### 2.2 Prediction ranges (uncertainty quantification)
- **Question:** *Can we estimate reliable ranges of asking prices for apartments in Montenegro, and how wide must they be?*
- **Practical value:** high. The point estimate is off by about 16% for a typical flat, and by much more for expensive ones. A valuer gains more from "€150–200k (80% range)" than from "€169k".
- **Data:** the 1,098 development listings with the existing folds, area, rooms and city. Neighbourhood information is optional and exploratory.
- **Methods**, from simple to more complex:
  1. **Empirical rule interval:** training p10–p90 of the city's €/m² × area. This is the baseline, and the valuer's intuition.
  2. **Conformal interval around the rule:** quantiles of out-of-fold log(price/rule) residuals.
     - Global version.
     - **Mondrian version** by region or size band, since the spread is much larger on the coast.
     - Calibration by **CV+ / cross-conformal** within the group-aware development folds (no separate calibration set is needed).
  3. **Quantile regression:** linear on log price, and quantile Gradient Boosting (α = 0.1 / 0.9).
     - Optionally conformalized quantile regression (CQR) for valid coverage.
- **Evaluation** (group-aware CV, nested where tuning is needed; test set not used):
  - empirical coverage vs the nominal 80% (and 90%);
  - mean and median relative interval width;
  - pinball loss;
  - interval score (Winkler);
  - **conditional coverage** by city (n shown), region, size band and price band.
- **What we already know:** within-city €/m² spread alone implies that an honest 80% range is wide: about ±20% for Nikšić/Cetinje, about ±40–50% for Tivat/Budva. The research would measure whether area, rooms and city narrow this, and where coverage fails. Expensive flats are likely under-covered.
- **Expected limitations:**
  - coverage is only guaranteed under exchangeability, and the data are a platform-dependent convenience sample;
  - estimated coverage for small cities is unreliable;
  - independent confirmation needs new adverts.
- **Feasibility:** high (≈ 6–8 configurations, minutes to run). It reuses the existing protocol.
- **Presentation value:** **high.** It is an honest, intuitive message ("how sure can a data-based estimate be?"), it builds directly on the existing result, and it turns the weakness (large errors) into a quantified finding.
- **Verdict: recommended direction #1.**

### 2.3 Anomaly detection
- **Question (reframed):** *Can simple data-science methods flag apartment listings that need manual review, because of data errors or prices unusual for similar flats?*
- **Practical value:**
  - **Data quality:** the project's biggest improvements came from finding rentals, re-posts and parsing errors by hand. Automating that check is useful for any future data collection.
  - **Market:** listings whose price is far from similar flats are worth a valuer's second look.
  - **Not** "bargains" or "overpriced", because there are no verified values.
- **Data:** the development listings, plus the real apartment rows that cleaning removed for **known** problems (36 rentals, 7 misclassified types, 2 price conflicts, 1 impossible area). The 278 test listings are not used.
- **Methods:**
  1. Robust statistics: within-city MAD z-score of log €/m², and title-vs-field consistency.
  2. Residual-based: out-of-fold log(price/rule).
  3. Isolation Forest and LOF on log area, log €/m², rooms and city or region.
- **Evaluation:**
  - **recall and precision at k on the known-problem labels** (46 rows);
  - overlap with the student's own "check" flags (30);
  - stability of flags across folds and seeds;
  - share of flags per city and platform, to see whether the methods simply flag one platform.
- **Expected limitations:**
  - the known labels are few and partly trivial (rentals are found by any price rule);
  - "unusual price" cannot be verified as an error or a genuine luxury flat without visiting the source;
  - a manual review of a sample of flags would be needed, without exporting text or URLs.
- **Feasibility:** medium-high.
- **Presentation value:** high, if framed as **data-quality assurance**. That links naturally to the project's main story (provenance, rentals, duplicates).
- **Verdict: recommended direction #2.**

### 2.4 Classification and alternative targets
- **Price segment** (low/mid/high, terciles learned on training data): a coarsened version of the same regression with the same inputs. It loses information, and accuracy would mostly reflect area. **Not recommended.**
- **Above/below the city reference** (sign of the rule's residual): the research extension already showed that area, rooms and city contain almost **no** learnable information about the residual. Nested tuning chose maximal shrinkage for every correction model. A classifier would be expected to be near chance. Its practical purpose would be served better by direction #2. **Not recommended.**
- **Relative position** (percentile of €/m² within the city): same issue as above.

### 2.5 Exploratory market structure (descriptive)
- **Topics:**
  - coastal vs continental €/m²;
  - the size "discount" (€/m² vs area by city; the research extension found negative descriptive slopes on the coast);
  - within-city spread;
  - neighbourhood differences in Podgorica, with bootstrap intervals;
  - supply structure by size;
  - platform comparison within the same neighbourhood.
- **Value:** medium-high for the presentation, low risk, little new methodology.
- **Limits:**
  - asking prices from a convenience sample;
  - Podgorica neighbourhoods depend on one capped platform;
  - associations only, never causes.
- **Verdict:** **not a separate direction.** Strengthen the existing EDA instead, e.g. a coastal/continental and size-discount section, if the student wants. It needs no new model.

### 2.6 Other questions considered

| Question | Verdict |
|---|---|
| House prices | Not feasible: no land area, Realitica only, thin city coverage |
| Rental prices | Not feasible: 37 rows |
| Asking price vs professional appraisal | Not now: unverified labels, mixed types, privacy, different years |
| Time trends / ARIMA | Impossible: no dates |
| Platform sampling bias (Estitor vs Realitica, same neighbourhood) | Possible as part of 2.5 or 2.3, but with small overlaps |
| Comparable-listings (kNN) estimate with its spread | A natural variant inside direction #1 (the range of the nearest comparables), not separate |

## 3. Ranking (by scientific justification, not expected metrics)

| Rank | Direction | Scientific justification | Feasibility | Presentation value |
|---|---|---|---|---|
| 1 | **Prediction ranges (conformal / quantile)** | High | High | High |
| 2 | **Anomaly detection as data-quality screening** | Medium-high (validated on known errors) | Medium-high | High |
| 3 | Descriptive market structure (EDA extension) | Medium (descriptive) | High | Medium-high |
| 4 | Clustering | Low (≈ size × city) | High | Medium (visual, weak story) |
| 5 | Classification / alternative targets | Low (no residual signal) | High | Low |
| 6 | Houses, rentals, appraisals, time series | Not feasible with these data | – | – |

## 4. Answers

1. **What is the most useful thing these data can give?**
   - An honest picture of **how far asking prices can be estimated from size and city, and how uncertain that estimate is**.
   - Solid lessons about **data quality** in scraped listings.
2. **Are there meaningful clusters?** Not beyond what city and size already show. Without price there are effectively only two dimensions. Not worth a main direction.
3. **Can another target be predicted reliably?** Not usefully. Segments and above/below-reference targets either repeat the regression or are close to unpredictable from the available features.
4. **Can useful price ranges be estimated?** Very likely yes, but they will be **wide**: about ±20% in Nikšić/Cetinje, about ±40–50% on the coast for 80% coverage. Measuring this honestly, and where coverage fails, is the research value.
5. **Can unusual listings be identified?** Yes, as *review flags*, and validated against the known errors found during cleaning. Not as "over/underpriced" verdicts.
6. **Strongest scientific and business story:**
   - *"Data quality and location matter more than algorithm complexity; a transparent €/m² rule is as accurate as ML; and an honest estimate comes with a range of ±X%."*
   - Direction #1 completes this story. Direction #2 supports its data-quality part.
7. **Keep or add?**
   - **Keep** the existing research as the core.
   - **Optionally add direction #1** (prediction ranges) as a compact extension.
   - Direction #2 is a good second choice if time allows. Otherwise, mention it as future work.

## 5. If approved: plan for direction #1 (max ≈ 8 configurations, development CV only)

| ID | Method | Calibration | Evaluation |
|---|---|---|---|
| I0 | Empirical city €/m² p10–p90 × area (train) | none | Coverage, width, Winkler, conditional coverage |
| I1 | Rule + global conformal (log residual) | CV+ (group-aware) | same |
| I2 | Rule + Mondrian conformal by region | CV+ | same |
| I3 | Rule + Mondrian conformal by size band | CV+ | same |
| I4 | Linear quantile regression (log price; area, rooms, city) | none / CQR | + pinball loss |
| I5 | Quantile HistGradientBoosting (fixed, conservative) | CQR | + pinball loss |
| (I6) | Best of I1–I5 + neighbourhood (exploratory) | CQR | Podgorica subset |

- **Rules fixed in advance:**
  - nominal 80% (and 90%);
  - a method is "valid" if its overall CV coverage is within ±3 percentage points of nominal;
  - among valid methods, the narrowest median relative width wins;
  - simplicity is preferred within 1 SE.
- **No test-set use.**

## 6. Conditions before any training
The student must confirm the research direction and that the course rules allow this assistance. The completed Capstone stays unchanged until then.
