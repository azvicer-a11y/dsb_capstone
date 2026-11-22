# Pre-registered protocol: retrospective test evaluation of prediction intervals

Fixed on 2026-11-20, **before** any interval method was applied to the test listings. The SHA-256 checksum of this file is recorded in `docs/validation_report.md`. After the evaluation nothing below may be changed, and no new winner may be chosen from the test results.

**Status of the test set:** the 278 test listings were never used for any interval method, but the same dataset (including these listings, for point predictions) was explored in earlier phases. This is therefore a **final retrospective check, not an independent external validation**.

| Item | Locked value |
|---|---|
| Methods | **G3a** (chosen interval method) and **G1** (simple baseline), exactly as in `uncertainty_research` (`src/valora_intervals.py`) |
| G1 | Training q(α/2) and q(1−α/2) of €/m² per city × area. Cities with < 10 training listings and Unknown use the overall training quantiles. Central estimate = training city median €/m² × area (the final point method) |
| G3a | `QuantileRegressor(alpha=0.0, solver='highs')` on **log price**, one model per quantile. Inputs: log(area); rooms with training-median imputation and a missing indicator; standardised numeric inputs; city one-hot with `min_frequency=10` and `handle_unknown='infrequent_if_exist'`. If the lower quantile exceeds the upper, the two are swapped |
| Quantile levels | 80%: 0.10 / 0.50 / 0.90. 90%: 0.05 / 0.50 / 0.95 |
| Fitting data | All 1,098 primary **development** listings (`split == 'development'`, `population == 'primary'`). No test listing is used in fitting |
| Evaluation data | The 278 primary **test** listings (`split == 'test'`, `population == 'primary'`). The 4 luxury listings are not part of the primary population and are excluded |
| Metrics | Empirical coverage; mean and median width (EUR); median relative width (width ÷ central estimate); mean interval score (Winkler); mean pinball loss of both bounds; share above the upper bound and below the lower bound; MAE of the central estimate |
| Groups | Coverage by city (cities with ≥ 10 test listings, others pooled as "other cities"); coverage by price band (< €100k, €100–200k, €200–300k, €300–500k, ≥ €500k) and size band, formed from the actual values **only for analysis** |
| Reporting | Reported next to the cross-validation results, whether better or worse. No re-fitting, no threshold changes, no new winner |
