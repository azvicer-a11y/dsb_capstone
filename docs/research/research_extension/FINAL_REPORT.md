# VALORA AI: Research extension, final report

**Type:** exploratory research after the completed Capstone. **The final project (`valora_ai/`) was not changed.**
**Approval condition:** execution was approved by the supervisor on the condition that the student confirms the research decisions and that the course rules allow this assistance. Neither confirmation can be checked from this workspace; both remain open.
**Reproduce:** `research_extension.ipynb` (≈ 30 s). It reads the final project's processed data and folds read-only. The plan, fixed before execution, is in `EXPERIMENT_PLAN.md`.

## 1. Bottom line

- **The completed Capstone and its chosen method, the city €/m² × area rule, stand.**
- No machine-learning approach beat the rule under the pre-registered selection rule.
- The only gain larger than its uncertainty came from **more precise location data** (neighbourhood within the city). It is concentrated in Podgorica, depends on one platform's capped sample, and is exploratory.
- **One statement in the final project needs correcting:** "tree models control large errors better". It rests on the 278-listing test sample and does **not** replicate in cross-validation on the 1,098 development listings.

## 2. Evaluation frame
- **Data and folds:** the same 1,098 development listings and the same 5 group-aware folds as the final project (fingerprint `dd9f21b7d8b6`). **The 278 test listings were not used**, so the old and new test results are not compared.
- **Integrity:** the references R0–R2 reproduce the stored fold MAEs exactly.
- **Metrics:** MAE in euros (main); RMSE and R² (per fold, and pooled over out-of-fold predictions); paired fold difference against the rule, with its standard error.
- **"Signal":** a paired gain larger than one SE. This is a practical flag, not a significance test.
- **Size of the study:** 15 configurations (3 references, 1 control, 11 new; the combination C1 turned out identical to F1). Total run time ≈ 30 s.

## 3. Complete results (cross-validation, development data only)

| ID | Description | CV MAE (mean ± std) | CV RMSE | CV R² | Pooled OOF R² | Paired Δ vs R0 (SE) | Signal | 95th pct abs error | Fit time | Complexity |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | Combination: D1 + neighbourhood (= F1) | €49,502 ± 4,452 | €102,863 | 0.575 | 0.569 | -1,025 (864) | yes | €159,621 | 0.2 s | 3 |
| F1 | D1 + one-hot city\|neighbourhood (≥10 training rows, else city) | €49,502 ± 4,452 | €102,863 | 0.575 | 0.569 | -1,025 (864) | yes | €159,621 | 0.2 s | 2 |
| R0 | City median €/m² × area (final model) | €50,527 ± 6,297 | €100,654 | 0.590 | 0.582 | – | no | €156,585 | 0.1 s | 1 |
| B3 | Rule × exp(log Ridge correction) (nested α) | €50,731 ± 5,768 | €101,257 | 0.586 | 0.579 | +204 (287) | no | €163,694 | 2.5 s | 2 |
| A2 | Ridge on log €/m², set D | €51,551 ± 5,215 | €103,014 | 0.573 | 0.568 | +1,024 (598) | no | €169,057 | 0.1 s | 2 |
| R1 | Ridge, log target, set D | €51,595 ± 5,153 | €103,326 | 0.571 | 0.566 | +1,068 (627) | no | €169,228 | 0.2 s | 2 |
| D2 | Rooms imputed by training area-quintile median | €51,720 ± 5,203 | €103,833 | 0.567 | 0.562 | +1,193 (624) | no | €168,201 | 0.1 s | 2 |
| D1 | Control: R1 family, median rooms before engineering | €51,731 ± 5,184 | €103,896 | 0.567 | 0.561 | +1,204 (647) | no | €167,095 | 0.1 s | 2 |
| D3 | Rooms = expected value from P(rooms \| log area, city) | €51,736 ± 5,176 | €103,815 | 0.567 | 0.562 | +1,209 (627) | no | €168,754 | 0.3 s | 2 |
| B2 | Rule × multiplicative Ridge correction (nested α) | €51,818 ± 6,572 | €99,414 | 0.599 | 0.591 | +1,291 (357) | no | €156,274 | 2.4 s | 2 |
| E1 | D1 + city × log(area) interactions (cities ≥ 30 training rows) | €51,897 ± 5,858 | €103,138 | 0.573 | 0.567 | +1,370 (646) | no | €160,901 | 0.2 s | 2 |
| B1 | Rule + additive Ridge correction (nested α) | €51,937 ± 6,326 | €99,658 | 0.598 | 0.590 | +1,410 (220) | no | €156,184 | 2.4 s | 2 |
| B4 | Rule × exp(log HGB correction), fixed settings | €52,128 ± 5,864 | €102,526 | 0.575 | 0.568 | +1,601 (859) | no | €161,828 | 1.0 s | 3 |
| A1 | Ridge on €/m², set D | €53,406 ± 4,870 | €103,368 | 0.569 | 0.568 | +2,879 (719) | no | €172,766 | 0.1 s | 2 |
| A3 | Random Forest on €/m², C2 | €54,900 ± 4,514 | €105,309 | 0.546 | 0.549 | +4,373 (1,511) | no | €182,876 | 2.5 s | 3 |
| R2 | Random Forest, C2 | €56,061 ± 3,753 | €103,596 | 0.564 | 0.563 | +5,534 (1,268) | no | €182,410 | 3.2 s | 3 |

**The final project's selection rule applied to all of these** (best + 1 SE = €51,493; simplest method within it): **R0, the city €/m² rule**. Within the tolerance: R0, F1, C1, B3.

![Paired difference vs the rule](figures/rx_02_paired_difference_vs_rule.png)

## 4. Experiment reports

### A: Price per m²
- **A2 (log €/m²) equals R1** (paired −€44, SE €41), as expected from log price = log €/m² + log area.
- **A1** (plain €/m²) is worse.
- **A3:** a Random Forest on €/m² improves on a forest on total price (−€1,161, SE €936), but stays €4,373 behind the rule.

**Conclusion:** no new value. A2 confirms the mathematics; it is not a new finding.

### B: Hybrid rule + learned correction (main experiment)
- **Leakage protection:** out-of-fold baselines (verified for 25 listings, own repeat group excluded) and α tuned by nested group CV.
- **Results:** B3 (log correction) ties the rule (+€204, SE €287). B1, B2 and B4 are worse on MAE.
- **Tuning:** nested tuning chose the **largest available shrinkage** for B1 and B2 (α = 10,000 in every fold) and α = 1,000 for B3. The data prefer "almost no correction". The grid was not extended after seeing this.
- **Large errors:** B1 and B2 have about 1% lower RMSE (pooled €102.1–102.4k vs €103.3k) and R² 0.59 vs 0.58. This is not a meaningful gain.
- **The hybrid does not fix the rule's weakness:** flats ≥ €500k are still underestimated by about €300k on average.

### D: Rooms (bedroom-count report)
- **Audit:**
  - 163 of 1,098 (14.8%) missing, 161 of them on Realitica.
  - Strongly city-dependent: Bar 73%, Kolašin 63%, Podgorica 6%.
  - Smaller and cheaper flats (51 m² / €145k vs 63 m² / €182k), so **not missing at random**.
  - 21 studios are 0 rooms; zero never means "missing".
  - The data contain advertised **rooms**, not verified bedrooms.
- **Estimating rooms (masking, cross-fitted, 935 known values):**
  - area-quintile median: 71% exact, error 0.30 rooms;
  - learned expectation: 77% exact, error 0.32 rooms;
  - training median: 38% exact, error 0.66 rooms.
  - Weighted to the real missing pattern: 0.27 / 0.31 / 0.68.
  - Errors are larger above 80 m² (≈ 0.45–0.5 rooms).
- **Effect on price:** none. D2 −€11 (SE €56), D3 +€4 (SE €45). On the 163 listings with missing rooms: €36,401 → €35,877 / €36,015.
- **Conclusion:** rooms are estimable from area, but the estimate repeats information the model already has. Keep the simple median + indicator. Estimated rooms are never stored or presented as real data.

### E: Area effects per city
- E1: +€166 (SE €349), so no gain.
- The descriptive slopes suggest that price per m² falls more with size on the coast (Bar −0.23, Ulcinj −0.20, Tivat −0.19), but these extra parameters do not improve predictions.

### F: Location within the city
- **Audit:**
  - 771 listings have a sub-city place; 31 places have ≥ 10 listings (569 listings).
  - 324 of these come from Estitor (Podgorica, capped at about 20 per neighbourhood).
  - 17 Podgorica names appear on both platforms.
- **F1 results:**
  - −€2,229 vs its control (SE €441), −€1,025 vs the rule (SE €864).
  - Podgorica (n = 389): €30,784 → **€24,246**.
  - Other listings: no change.
  - The median absolute error falls from €27.0k to €23.8k; RMSE does not improve (€104.9k vs €103.3k).
- **Conclusion:** promising but exploratory. It needs confirmation on new adverts, ideally not dominated by one platform.

### C1: Combination
Pre-registered rule: only F1 qualified, so C1 = F1. There is no additional finding.

## 5. Large errors (out-of-fold, 1,098 listings)

| | R0 rule | R1 Ridge log | B3 hybrid | F1/C1 | R2 Random Forest |
|---|---|---|---|---|---|
| Errors > €200k | 41 | 47 | 42 | 46 | 50 |
| 95th percentile abs. error | €156.6k | €169.2k | €163.7k | €159.6k | €182.4k |
| Pooled RMSE | €103.3k | €105.3k | €103.7k | €104.9k | €105.6k |
| Median abs. error | €27.0k | €27.3k | €27.5k | **€23.8k** | €31.0k |
| Mean error, flats ≥ €500k (n = 46) | −€296k | −€306k | −€308k | −€308k | −€217k |

![Bias by price band](figures/rx_03_bias_by_price_band.png)

- All methods strongly underestimate expensive flats.
- The Random Forest is the least biased there, but it is worse overall: more large errors, and it overestimates cheap flats.
- No approach controls large errors clearly better than the rule.

## 6. Answers to the 12 questions

| # | Answer |
|---|---|
| 1 | Is predicting €/m² better? **No.** Log €/m² ≈ log price (the same model); plain €/m² is worse. |
| 2 | Does the hybrid beat the rule? **No.** B3 ties; B1, B2 and B4 are worse on MAE; tuning chose maximal shrinkage. |
| 3 | Does estimating missing rooms help? **No.** It is estimable, but it adds nothing to the price estimate. |
| 4 | Does the area–rooms relationship add value? **No evidence.** |
| 5 | Do city-specific area effects help? **No.** |
| 6 | Does finer location help? **Yes, weakly and mainly in Podgorica** (exploratory, platform-dependent). |
| 7 | Which features contribute? **Area ≫ city > neighbourhood (Podgorica).** |
| 8 | Which method controls large errors best? **None clearly**; B1/B2 are about 1% better in RMSE. The test-set "trees are better" impression did not replicate. |
| 9 | Best CV MAE? **F1** (€49,502 ± 4,452), then R0 (€50,527 ± 6,297). |
| 10 | Is the extra complexity justified? **No, not for the final model.** |
| 11 | Best research question? See Section 7. |
| 12 | Recommendation? See Section 8. |

## 7. Recommended research question

> **Can machine learning improve apartment asking-price estimation in Montenegro compared with a simple city price-per-square-metre rule, and how much does location data quality contribute?**

**Answer from both phases:**
- With the property information available (area, rooms, city), **no**: a transparent city €/m² rule is as accurate on average.
- **Location data quality is what matters**: cleaning the city field was worth the most, and neighbourhood information helps where it is well covered.
- It must be stated openly that the question was **refined after the first results**. The student must approve the wording.

## 8. Recommendation for the Capstone

1. **Keep the completed, validated Capstone unchanged in its method and chosen model** (the city €/m² rule).
2. **Correct one statement.** Wherever the final project says that tree models control large errors better, rephrase it as: *"on the test sample the tree models had lower RMSE, but this did not replicate in cross-validation on the development data"*. This affects the TL;DR and section 8 of `02_modelling.ipynb`, the README "Key result", and the study guide. **Not changed yet; awaiting approval.**
3. **Optionally** add a short appendix or "next steps" note on these exploratory results:
   - hybrid, €/m² targets, rooms imputation and city–area interactions gave no gain;
   - neighbourhood location helped in Podgorica.

   Add it only if the student wants it and can explain it.
4. **Possible pre-registered next study** (not run): a neighbourhood-level €/m² rule (neighbourhood median if ≥ 10 training listings, otherwise city), tested on **newly collected** adverts.

## 9. Limitations
- Exploratory: all evidence comes from cross-validation on data that had already been explored. Independent confirmation needs new adverts.
- Five folds give a small sample of fold differences. "Signal" (gain > 1 SE) is a heuristic, not a statistical test.
- 15 configurations were compared, so with this many comparisons one weak signal can appear by chance.
- The rooms-validation masking uses known values, which are not the same as the truly missing ones (not missing at random).
- Neighbourhood information is dominated by one platform with a capped sample.

## 10. Integrity of the completed project

- **Checksums:** a SHA-256 manifest of all **101 files** in `valora_ai/` was taken before the extension and again after it. The two manifests are **identical** (`checks/valora_ai_manifest_BEFORE.sha256`, `..._AFTER.sha256`). The final notebooks, README, documentation, results, figures and model were not modified.
- **Tests:** the final project's full test suite was run on a **separate copy**, which was deleted afterwards: **70 passed, 0 failed** (333 s, including the slow from-scratch re-execution).
- **Other:** no Git operations, nothing published, no other projects accessed.

## Files

| File | Content |
|---|---|
| `EXPERIMENT_PLAN.md` | Pre-registered plan and decision rules (checksum in `checks/plan_fixed.txt`) |
| `research_extension.ipynb` | Reproducible notebook (every code cell explained) |
| `lib/rx.py` | Experiment components |
| `lib/valora_*.py` | Copies of the final helpers, so that importing never writes into the final project |
| `results/all_results.csv` | Complete results table (also `results_table.md`) |
| `results/rooms_masking_validation.csv`, `rooms_subset_mae.csv` | Rooms results |
| `results/oof_errors_by_*.csv` | Out-of-fold error analysis |
| `results/large_error_summary.csv` | Large errors |
| `results/selection_extension.json` | Selection rule applied to all configurations |
| `figures/rx_01_rooms_estimation_error.png` | Rooms estimation error by area |
| `figures/rx_02_paired_difference_vs_rule.png` | Paired difference against the rule |
| `figures/rx_03_bias_by_price_band.png` | Bias by price band |
| `checks/methodology_checks.md` | Leakage and methodology checks, and deviations |
| `checks/valora_ai_manifest_BEFORE.sha256`, `..._AFTER.sha256` | Final-project checksums |
| `checks/final_project_tests_in_copy.txt` | Result of the 70 final-project tests, run in a separate copy |
