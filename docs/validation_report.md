# Validation report

How the final project was checked, and what the checks showed. Every claim comes from a logged execution, never from saved notebook outputs alone.

## 1. Environment

| Item | Value |
|---|---|
| OS | Windows 11 Pro (10.0.26200), 16 logical CPUs, 15.3 GB RAM (≈ 3.6–4 GB free during work) |
| Python | 3.11.9, project-local virtual environment (no global packages changed) |
| Main libraries | pandas 3.1.1, numpy 2.4.6, scikit-learn 1.9.1, scipy 1.17.1, matplotlib 3.11.2, joblib 1.6.0, jupyter 1.1.1, notebook 7.6.5, ipykernel 7.4.0, nbconvert 7.17.2, nbformat 5.11.1, nbclient 0.11.0, pytest 9.2.0 (pinned in `requirements.txt`) |
| `pip check` | No broken requirements (development venv, earlier clean-copy venv and final package venv) |
| Parallelism | At most 2 processes per model |

## 2. Final package test (fresh folder, fresh environment)

The packaged project (`SUBMISSION_PROJECT/` from the reviewed package) was unzipped into a **separate folder** and run from scratch.

| Step | Result |
|---|---|
| 1. Unzip | 139 project files; no data files, no listing-level outputs, no private map, no model file, no venv or caches |
| 2. New virtual environment | `py -3.11 -m venv`, installed **only** from `requirements.txt`; `pip check`: *No broken requirements found*; Python 3.11.9 |
| 3. Local data copy | The two raw CSVs copied into `data/raw/` (as described in `data/README.md`) |
| 4. `01_eda.ipynb`, fresh kernel | Executed without errors in **12 s** |
| 5. `02_modelling.ipynb`, separate fresh kernel | Executed without errors in **208 s** |
| 6. All tests (`pytest -m ""`) | **133 passed, 0 failed** (214 s, including the slow from-scratch test) |
| 7. Comparison with the validated project | **67 of 67** generated files match: **60 byte-identical**, including the processed data and all 25 figures; **7 numerically identical** (relative tolerance 1e-9; only timing columns and float formatting differ) |
| 8. Absolute paths and personal data in the executed notebooks | None found |

- **Run times vary with machine load.** Earlier validations measured 29 s and 556 s.
- **Privacy scan:** before zipping, every shipped text file and notebook was scanned for absolute paths, user names, e-mail addresses, appraisal file paths, listing URLs, platform IDs and agent names. **0 hits** (the privacy test file itself, which contains the search patterns, is excluded from this scan).
- **Completeness check:** every project file that is not deliberately excluded must be in the package.

**Packaging bug found by this test.** The first build of the reviewed package excluded `data/reference/settlement_mapping.csv` by mistake. A new exclusion pattern `data/*.csv` (meant for the legacy raw-data location) also matched the subfolder file, because Python's `fnmatch` lets `*` cross `/`; `.gitignore` does not. EDA in the fresh folder therefore stopped. Fix:
- the packaging script now names the two legacy files explicitly;
- the build includes the completeness check above;
- the package was rebuilt and the whole test above was repeated.

**One change after this test:** this validation report was updated with these results and the package was rebuilt. The rebuilt ZIP differs from the tested ZIP only in documentation: this report and, in the reviewed package, the private editorial notes (checked file by file).

## 3. Automatic tests

| Suite | What it checks | Tests |
|---|---|---|
| `test_data.py` | Raw-file checksums; provenance (the mislabelled simulated rows can never count as real); cleaning counts; re-post rule; studios; feature engineering without infinities; 13 location rules; mapping file; repeat groups; no private columns in the export; reproducible export | 40 |
| `test_leakage.py` | No target-derived inputs; train/test and repeat groups disjoint; CV folds group-disjoint and never touching test rows; imputation and encoding fitted on training rows only; baseline uses training prices only; protocol saved | 8 |
| `test_modelling.py` | Metric formulas; selection rule; identical folds for all models; finite predictions; results recomputed from saved predictions; CV mean and std; final model follows the pre-registered rule and is not the test winner; saved model reloads identically | 11 |
| `test_intervals.py` | Coverage, width, interval-score and pinball formulas on known numbers; wider intervals never lower coverage; bounds positive, finite and ordered for G1 and G3a at both levels; **no lower/upper crossing**; the documented rare median-outside-range cases are pinned exactly; methods ignore the price of the rows they predict; fitting uses training rows only; CV interval results recomputed from saved out-of-fold predictions; **identical to the research phase**; test results recomputed from saved predictions; protocol file checksum equals the locked value; interval test set = the 278 primary test listings, disjoint from development by record and by repeat group; point-method selection unchanged | 19 |
| `test_notebooks.py` | All 13 / 12 template sections in order; "What this code does / Why we need it" before every code cell; no template leftovers; one clean top-to-bottom execution without errors; modelling reads only the processed CSV; all figures and result files exist; **slow:** copy the project, delete all generated files, run 01 and 02 in fresh kernels, and compare the processed data and key results (including interval results) | 10 + 1 slow |
| `test_privacy.py` | `.gitignore` covers both raw-data locations (current and legacy) and every listing-level output; no shared result table contains internal IDs, platform IDs or URLs; notebook outputs show no internal IDs, URLs or local paths; the notebooks and public documents contain no third-person wording and no references to the assistance process (outside the README acknowledgements) and no application promises; every relative link in the public documents resolves | 44 |
| **Total** | | **133** (132 fast + 1 slow) |

**Results on the development copy:** fast suite **132 passed, 0 failed** (11.3 s); slow suite **1 passed, 0 failed** (574 s, from-scratch re-execution in a temporary copy and comparison of processed data, point and interval results).

## 4. Pre-registration and the test set

| Item | Value |
|---|---|
| Point-estimation protocol | `docs/results/protocol.json`, written by the notebook before any model is fitted |
| Interval test protocol | `docs/interval_test_protocol.md`, locked 2026-11-20 10:22:49 UTC, SHA-256 `e574889e3f833e80a5cd43befe208b43c8a22243861df549fb0160895eed8aef` (checked by `test_intervals.py`) |
| Test-set history | Seen in my original notebooks. Used once for the point-method test (section 8.2), and once for the pre-registered interval check (section 8.9). No method, setting or threshold was changed after either |

## 5. Determinism
- All randomness uses fixed seeds (`random_state=42`).
- `valora_apartments_clean.csv` is byte-identical between all runs (SHA-256 `64d0339e54dd5185…`).
- The modelling results (`cv_results.csv`, `test_results.csv`, `selection.json`, interval results) were identical across every execution, apart from timing columns.

## 6. Honest notes on the process

1. **Development smoke test.** While building the pipelines, one 5-fold grouped cross-validation was run on **all 1,376 primary listings**, including the rows that later became the test set, to check that the code worked. Only CV errors were looked at. The candidate list, feature sets and selection rule were already fixed and were not changed.
2. **The test set is internal.** It had been seen in the original notebooks. All test results are retrospective internal checks, not independent validation.
3. **Notebooks are generated by build scripts,** kept in the local workspace outside the project. Explanatory text is written from the executed outputs and checked against the result files. Statements corrected after checking:
   - bathrooms exist only on Estitor;
   - the CV-vs-test gap is not caused by a more expensive test set;
   - **"tree models control large errors better"** was seen on the test set only and did not replicate in cross-validation. It was corrected everywhere.
4. **Test failures during development**, both caused by over-claims in the tests themselves, not by the data:
   - `test_exact_reposts_rule` failed after a pandas-3 NA comparison change in the test. It was fixed with `astype(object).fillna`; its expectation was not weakened.
   - `test_quantile_regression_has_no_crossing_and_median_inside` failed. The **bounds** never cross, but because the three quantiles are fitted separately, the **median** fell slightly outside its own range in 1 of 278 test listings (Berane, a city without development listings) and in 3 of 2,196 CV cases. The test was split:
     - a strict test that the bounds never cross;
     - a test that pins the exact documented counts.

     The finding is reported in notebook section 8.9.
5. **Settlement verification:** the mapping was checked against the official Monstat 2023 register. Its review status is recorded in `data/reference/settlement_mapping.csv`.
6. **Final editorial pass.** Wording, voice, privacy rules and the project structure were revised, and both notebooks were re-executed. Every generated result, figure and processed file was compared with the previously validated version: **59 byte-identical, 8 numerically identical, 0 different**. The only non-numeric difference is a renamed review-status column in the settlement mapping table. No model, setting, split, metric or data rule was changed.
7. **Warning output with a local path (found by the packaging scan).**
   - **What happened:** after the editorial re-execution, the tuning cell printed a known scikit-learn/joblib `UserWarning` about parallel workers (`sklearn.utils.parallel.delayed should be used with ...Parallel`). It does not appear on every run. The warning text contained the absolute path of the local virtual environment.
   - **Gap in the new test:** `test_privacy.py` did not catch it, because its path pattern expected a doubled backslash.
   - **Fix:**
     - the test pattern was corrected; it then failed on that notebook, as it should;
     - exactly this warning message is now filtered in the modelling setup cell, with an explanation in the notebook;
     - the notebook was re-executed.
   - **Results** stayed identical to the validated version.
8. **Not tested:** Google Colab, macOS and Linux.

## 7. Reproducibility status

**Status: REPRODUCED.**

- From the shipped package plus the author's two raw CSV files, a new environment built only from `requirements.txt` regenerated:
  - byte-identical processed data and figures;
  - numerically identical point-estimation and interval results;
  - the same model choice.
- All 133 automatic tests passed.

**Conditions:**
- the raw CSV files must be obtained from the author (not shipped, for privacy and data-rights reasons);
- tested only on Windows 11 with Python 3.11.9 and the pinned versions;
- the saved joblib model is regenerated locally and loads only with compatible library versions and with `src/` on the Python path.
