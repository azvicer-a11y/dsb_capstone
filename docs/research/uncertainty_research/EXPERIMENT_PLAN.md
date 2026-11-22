# Uncertainty research: plan (fixed before execution)

Written on 2026-11-20, **before** any interval method was fitted. Its checksum is recorded in `checks/plan_fixed.txt`. Execution was approved by the supervisor **on the condition** that the student confirms the research question and that the course rules allow this help. Both conditions are outside this workspace.

## Research question (to be confirmed by the student)
*How accurately can we estimate apartment asking prices in Montenegro, and how reliably can we quantify the uncertainty of these predictions?*

The question developed over four phases. **The interval question was formulated after** the point-prediction results, the research extension and the opportunity audit. It is an exploratory follow-up, not a pre-planned hypothesis.

## Data and splits
- **Data:** the 1,098 primary **development** listings of the final project. The 278 test listings are **never** loaded into any method (asserted in code).
- **Outer folds:** the existing 5 group-aware folds (fingerprint `dd9f21b7d8b6`). Every method is evaluated on the identical outer-validation listings.
- **Split conformal (G2, G4):** inside each outer training fold, a group-aware `GroupShuffleSplit(test_size = 0.25, random_state = 42)` separates a **fit** part (about 75%, ≈ 660 listings) from a **calibration** part (about 25%, ≈ 220 listings). The outer-validation listings are not seen until evaluation.
  - G1 and G3 use the whole outer training fold (≈ 880 listings). G2 and G4 fit on fewer listings. This is reported.
- **Calibration quantile:** finite-sample. With n calibration scores, take the k-th smallest, where k = ⌈(n+1)(1−α)⌉. If k > n, the interval is unbounded (reported).

## Configurations (8, including baselines)

| ID | Method | Fitted on | Central estimate |
|---|---|---|---|
| G1 | **Empirical €/m² quantiles**: training q(α/2) and q(1−α/2) of city €/m² × area. Cities with < 10 training listings and Unknown use overall training quantiles | whole outer training fold | rule (city median €/m² × area) |
| G2a | Split conformal, **absolute** residual \|y − ŷ\| around the rule; interval ŷ ± q | fit / calibration | rule (fit part) |
| G2b | Split conformal, **relative** residual \|y − ŷ\| / ŷ; interval ŷ(1 ± q), lower bound ≥ €1 | fit / calibration | rule (fit part) |
| G2c | Split conformal, **log** residual \|log y − log ŷ\|; interval [ŷ·e^−q, ŷ·e^q] | fit / calibration | rule (fit part) |
| G3a | **Linear quantile regression** on log price; inputs log area, rooms (training-median imputation + missing indicator), city one-hot (≥ 10 training listings, otherwise "infrequent"); `QuantileRegressor(alpha=0, solver='highs')`, standardised numeric inputs | whole outer training fold | q0.5 |
| G3b | **Quantile HistGradientBoosting** on log price; same inputs plus engineered set D; fixed conservative settings (learning rate 0.05, 200 iterations, 8 leaves, min leaf 40) | whole outer training fold | q0.5 |
| G4a | **CQR** on G3a: score max(q̂lo − y, y − q̂hi) on the log scale; interval [q̂lo − Q, q̂hi + Q] | fit / calibration | q0.5 (fit part) |
| G4b | **CQR** on G3b | fit / calibration | q0.5 (fit part) |

- **Quantile crossing:** if q̂lo > q̂hi for any listing, the two bounds are swapped for that listing, and the count is reported.
- **Levels:** every configuration is computed at **80%** (main) and **90%** (secondary). QR and HGB are fitted separately for each quantile.

## Metrics (per outer fold, then mean ± std over the 5 folds)
- Empirical coverage, at listing level. **Group-level coverage** is also reported: each repeat group weighted once.
- Mean and median width (EUR).
- Median relative width (width ÷ central estimate).
- Mean interval score (Winkler, α).
- Mean pinball loss of the lower and upper bounds at their nominal quantiles.
- MAE of the central estimate.
- Paired fold differences of the interval score against the best method, with SE.

## Selection rule (80%, fixed now)
1. **Acceptable coverage:** mean CV coverage within **77–83%** (nominal ±3 percentage points).
2. Among acceptable methods, the best is the one with the **lowest mean interval score**. The interval score rewards narrow intervals and penalises misses, so the choice is **not** based on width alone.
3. **Simplicity:** choose the simplest acceptable method whose mean interval score is within 1 paired SE of the best. Complexity ranks: G1 = G2a = G2b = G2c = 1; G3a = G4a = 2; G3b = G4b = 3. Ties are broken by lower interval score.
4. If **no** method reaches acceptable coverage, report this, and name the method closest to 80% as the most reliable one available.

## Interpretation thresholds (fixed now, descriptive)
The median relative width of the 80% interval (width ÷ central estimate) is described as:
- below 40%: narrow (practically informative);
- 40–80%: moderate;
- above 80%: wide (limited practical value).

These are interpretive labels, not proven standards.

## Geography and high prices (post-hoc error analysis only)
- **By city** (dev n ≥ 20): Podgorica, Budva, Herceg Novi, Tivat, Bar, Kotor, Kolašin, Ulcinj, Cetinje, Nikšić. Coverage and width with n.
- **By region:** **coastal** = the six coastal municipalities (Herceg Novi, Kotor, Tivat, Budva, Bar, Ulcinj); **continental** = all others; Unknown is reported separately.
- **High prices:** price bands and size bands are formed from the *actual* price and area, **only for analysing the errors afterwards**, never for choosing an interval. Misses are split into above-upper and below-lower.

## Anomaly screening (secondary)
1. **Flags:** development listings outside the chosen method's **90%** out-of-fold interval, and a robust within-city score, |MAD z| of log €/m² > 3.5 (training medians and MADs per fold).
2. **Retrospective check:** the 46 real apartment rows removed during cleaning for known problems (36 rentals, 7 misclassified types, 2 price conflicts, 1 invalid area) are scored with methods fitted on the development data only. They are kept **separate**: never used to fit price or interval models. Recovering them is a retrospective check, not independent validation.
3. **Weak labels:** overlap with the student's "check" flags, using only development listings that carry one.
4. **Isolation Forest is not run:** the available labels are few, mostly found by simple price rules, and were already used during cleaning, so they cannot validate an ML anomaly detector reliably. It is left as future work.
5. Flags are presented only as **candidates for manual review**.

## Demonstrations
- Hypothetical flats: 45 m² Podgorica, 70 m² Podgorica, 70 m² Budva, 70 m² Nikšić, 100 m² Tivat.
- The chosen method is fitted on all 1,098 development listings, with the same fit/calibration split rule if it is a conformal method.
- **Support:** the number of development listings in the city within ±15% of the area. Fewer than 10 gives a warning.
- Rooms, where a method needs them: the median known rooms of development listings in that area window and city (reported).
- **Relevant coverage:** the method's out-of-fold coverage in that city.

## Not done
- No Mondrian or group-conditional conformal variants (the 8-configuration budget).
- No new data rules, seeds or splits.
- No test-set use.
- No application.
