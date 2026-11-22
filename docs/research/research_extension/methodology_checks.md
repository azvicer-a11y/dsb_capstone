# Leakage and methodology checks (research extension)

| Check | How | Result |
|---|---|---|
| Same population | 1,098 development listings from the final project's `cv_folds.csv`; all `population == primary` | Passed (assert in notebook section 2) |
| Test set untouched | The intersection of development IDs and the 278 test IDs is empty; test rows are never passed to any `fit` or `predict` | Passed: **0** test listings used |
| Same folds | SHA-256 fingerprint of the fold membership = `dd9f21b7d8b6`, as in the final project | Passed |
| Same pipelines | R0, R1 and R2 recomputed here reproduce the final project's **stored fold MAEs** (relative tolerance 1e-9) | Passed for all three |
| No price-derived inputs | Inputs: area, rooms, city, neighbourhood token, repeat_group (grouping only). €/m² appears only as a *target* (A1–A3) | Passed (by construction, `rx.py`) |
| Hybrid out-of-fold baseline | For 25 random training listings of outer fold 0, the baseline was recomputed from a rule fitted on the inner folds that exclude the listing's repeat group, and compared with the hybrid's stored out-of-fold baseline | Passed: 25/25 identical, own group excluded |
| Nested tuning | Ridge α of B1–B3 chosen by `GridSearchCV` with an inner `GroupKFold(4)` inside each outer training fold | Passed (chosen α logged per fold) |
| Train-only rooms imputation | `RoomsImputer.fit` uses only the training fold's known rooms, with area and city as inputs (no price). Known rooms are never replaced; `rooms_missing` is kept | Passed (by construction) |
| Rooms validation | Cross-fitted on the same 5 folds; estimators fitted on training folds, evaluated on masked known values of the validation fold; reweighted to the city-specific missingness pattern | Done; limitation: masked known values are not the same as truly missing ones |
| Neighbourhood encoding | One-hot with `min_frequency = 10` learned inside each training fold; places with fewer rows fall back to the city effect; no target encoding | Passed (by construction) |
| Final project unchanged | SHA-256 manifest of all files in `valora_ai/` before and after; the final tests run in a separate copy | See `FINAL_REPORT.md` |

## Deviations from the plan (all documented)

1. **D1 control added before execution.** It is recorded in `EXPERIMENT_PLAN.md`, whose checksum was saved at 2026-11-19T14:41:51Z, before the first run.
2. **`lib/rx.py` changed after the plan checksum:**
   - (a) wiring so the combination step C1 can pass extended feature sets to the hybrid (`features`, `log_target` parameters), before the first run;
   - (b) after the first run, `HybridRegressor` was changed to compute only the selected correction form. It had also evaluated `exp()` of the euro-scale additive correction, which caused overflow **warnings**, but the returned predictions were unaffected. Re-running gave **identical** metrics (difference < 1e-6).
3. **The notebook was executed three times:** first pass, after fix 2(b), and after the explanatory text was written. All results were identical. The text was written after the results and checked against them.
4. **No configuration, metric, threshold, seed, fold or data rule was changed after seeing results.** The α grid was **not** extended, although B1 and B2 chose its upper edge.
