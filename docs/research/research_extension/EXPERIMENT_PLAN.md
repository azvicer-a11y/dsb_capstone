# Research extension: experiment plan (fixed before execution)

Written on 2026-11-19, **before** any new model was trained. The configurations, metrics and decision rules below were not changed after seeing results. Any deviation is listed in `FINAL_REPORT.md`.

**Status of approval:** execution was approved by the project supervisor on the condition that the student confirms the research decisions and that the course rules allow this help. Both confirmations are outside this workspace and must be obtained by the supervisor or the student.

## Fixed evaluation frame

| Item | Value |
|---|---|
| Data | `valora_ai/data/processed/valora_apartments_clean.csv` (read-only) |
| Population | The 1,098 primary **development** listings. The 278 test listings are **not loaded into any model** (checked in code). |
| Folds | The existing 5 group-aware folds (`valora_ai/docs/results/cv_folds.csv`, fingerprint `dd9f21b7d8b6`). No new random splits. |
| Groups | The existing `repeat_group`. Inner folds (tuning, out-of-fold baselines) are also group-aware. |
| Main metric | MAE in EUR on the total-price scale |
| Additional metrics | RMSE and R² (per fold, and pooled over out-of-fold predictions); paired fold difference vs **R0**, with its standard error (SE = sd/√5); fit time; complexity |
| Signal rule | A configuration shows a *practical signal* if its mean paired MAE difference vs its control is negative and larger in size than one SE. This is **not** a significance test and not proof of superiority. |
| Integrity check | The reference methods R0–R2 recomputed here must reproduce the stored CV MAE of the final project exactly. If not, stop. |
| Resources | At most 2 parallel processes |

## Configurations (12 new + D1 control + 3 references + at most 1 combination)

| ID | Hypothesis | Features | Target | Model | Evaluation | Expected value |
|---|---|---|---|---|---|---|
| R0 | Reference: practical rule | area, city_clean | price | City median €/m² (train) × area | 5-fold CV | Control for all paired differences |
| R1 | Reference: best ML in CV | set D (area, rooms, log area, area², area/room, size group, city) | log price | Ridge (α = 1) | 5-fold CV | Control for the feature ablations D/E/F |
| R2 | Reference: tree model | area, rooms, city | price | Random Forest (300 trees, leaf 2) | 5-fold CV | Context |
| A1 | Modelling €/m² directly helps | set D | price / area | Ridge (α = 1) → × area | 5-fold CV | Medium |
| A2 | Log €/m² is (almost) the same as log price | set D | log(price / area) | Ridge (α = 1) → exp × area | 5-fold CV | **Mathematical check**: should be ≈ R1, because log price = log €/m² + log area |
| A3 | Trees work better on €/m² | area, rooms, city | price / area | Random Forest → × area | 5-fold CV | Medium |
| B1 | ML can correct the rule (additive) | set D | price − OOF baseline | Ridge, α nested (inner group CV) | 5-fold CV | **High** |
| B2 | Multiplicative correction | set D | price ÷ OOF baseline | Ridge, α nested | 5-fold CV | High |
| B3 | Log-residual correction | set D | log price − log OOF baseline | Ridge, α nested | 5-fold CV | High |
| B4 | A non-linear correction captures the size effect | set D | log residual | HistGradientBoosting (fixed, conservative) | 5-fold CV | High |
| D1 | Control for D/E/F (same pipeline family as the variants) | R1 features, but missing rooms median-imputed **before** area/room is computed, + indicator | log price | Ridge (α = 1) | 5-fold CV | Control: should be ≈ R1. Paired comparisons for D2, D3, E1 and F1 use **D1**, so that only one thing changes |
| D2 | Better rooms imputation helps | R1 + rooms imputed by area quintile (train) + indicator | log price | Ridge (α = 1) | 5-fold CV + subset with missing rooms | Medium |
| D3 | Learned rooms estimate helps | R1 + **expected** rooms from P(rooms ∣ log area, city) (multinomial logistic, train) + indicator | log price | Ridge (α = 1) | 5-fold CV + subset + masking validation | Medium |
| E1 | The area effect differs by city | R1 + city × centred log area (cities with ≥ 30 training rows) | log price | Ridge (α = 1) | 5-fold CV | Medium |
| F1 | Location within the city helps | R1 + one-hot(city + neighbourhood), ≥ 10 training rows, others fall back to city | log price | Ridge (α = 1) | 5-fold CV + Podgorica subset | Medium |
| C1 | Combination (conditional, see below) | – | – | – | 5-fold CV | Only if the conditions are met |

## How the hybrid (B) avoids leakage
- For each outer training fold, every training listing gets an **out-of-fold baseline**. The city medians come from inner group-aware folds that exclude the listing's own repeat group.
- The correction is learned on these out-of-fold residuals.
- Validation listings get the baseline computed from the whole outer training fold.
- The fallback (overall training €/m²) applies to Unknown and to cities with fewer than 10 listings in the relevant training data.
- Ridge's intercept is not penalised. A very large α therefore shrinks the correction to a **constant** (a global level adjustment), not exactly to zero. With α → ∞ and no intercept shift, B1–B3 would equal R0.

## Rooms (D)
- Known room counts are **never** replaced.
- `rooms_missing` (1 = not stated in the advert) is always included.
- The imputers use only area and city, never price. They are fitted on the training fold's known rooms.
- Imputing a training row's missing rooms does not use its price, so no cross-fitting is needed for the price model. Cross-fitting (the same 5 folds) is used to **validate** the rooms estimate on temporarily masked known values.
- The masking is reweighted to follow the real missingness pattern (by city share).

## Omitted, with reasons
- **Polynomial and spline area terms:** non-linear area terms (log area, area², size group) were already tested in feature set D and did not help Linear Regression or Random Forest. Repeating them adds configurations without a new hypothesis.
- **Geographical groupings** (coast/north/centre, distance to the sea): no reliable source in the data, and they would have to be invented. Not done.
- **Target encoding of neighbourhoods:** one-hot encoding with a frequency threshold and regularisation is simpler and sufficient for 23 well-covered neighbourhoods.
- **Price-category classification** (from the earlier plan): not requested in this phase.

## Combination rule (fixed now)
C1 is run **only if** at least one experiment shows a signal. It is then exactly one configuration:
- the **best hybrid form** (B1–B4, lowest CV MAE), if it shows a signal against R0, otherwise R1;
- plus every feature addition (D2/D3, E1, F1) that showed a signal against **D1** (the same-pipeline control; see the D1 row), using the better of D2/D3 if both did.

*Design note, added before execution:* D1 was added while writing the code. The final project's R1 computes area per room **before** imputing rooms, but D2/D3 impute rooms first, so R1 is not an exact control for them. D1 is the exact control.

If nothing shows a signal, C1 is not run, and this is reported.

## Final recommendation rule (fixed now)
1. The final project's rule stays in force: lowest CV MAE, and a simpler method if it is within one SE.
2. A new approach is recommended for the Capstone **only** if it beats R0 with a paired signal and its added complexity can be explained.
3. Every new result is labelled exploratory, because it has not been confirmed on new, unseen adverts.
