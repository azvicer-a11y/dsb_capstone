# Privacy risks and data rights

This document lists what is sensitive in the VALORA AI data, how the project handles it, and which data-rights questions remain open. It reports **counts only**. No names, paths or text values are reproduced.

## 1. What is sensitive in the raw data

| Item | Where | Count | Risk |
|---|---|---|---|
| File paths of professional appraisal reports (`document`) | Raw file, appraisal rows only | **927** (877 "unverified", 50 "reviewed") | These are internal folder and file names of valuation reports. **445** contain a property type followed by a capitalised word, the typical pattern of an **owner's surname or a street name** (a narrower pattern found 179). **All 927 are treated as sensitive** |
| Verification notes (`notes`, `source_note`, `verification_status`) | Raw file, appraisal rows | 2 / 2 / 50 | Tied to confidential valuation documents |
| Advert titles (`naslov`) | Raw file | 3,986 (1,986 real) | **134** Realitica Adriatic titles begin with the name of an agent or agency, some of them personal names |
| Descriptions (`opis`) | Raw file | 549 | **37** real-listing descriptions mention a price (target leakage). No phone numbers, e-mails or links were found by the automatic patterns |
| URLs (`url`) and platform IDs (`listing_id`) | Raw file | 1,986 | Public adverts, but they make it easy to re-identify a property and its advertiser |

An automatic scan cannot prove that something is **absent** (for example names written without capitals). It only shows what it found.

## 2. How the project handles it

- **The processed file** `data/processed/valora_apartments_clean.csv` contains no URLs, platform IDs, titles, descriptions or appraisal fields. Each listing is identified only by an internal `record_id` (VAL-0001 …).
- **The link between `record_id` and the platform ID or URL** is written only to `data/private/`, which is excluded from Git.
- **The notebooks** never display titles, descriptions, URLs or appraisal columns. Tables of individual listings show city, area, rooms and prices, without internal IDs.
- **All appraisal rows are excluded** from the analysis.
- **Kept out of Git** (`.gitignore`): the raw data files, in both their current location (`data/raw/`) and the location used in the original repository (`data/`); every listing-level output (one row per advert or per internal ID); the private ID map; and the saved model.
- **Shared result tables** are aggregates.
- **Archive:** the archived original `01_EDA.ipynb` has its outputs cleared, because they printed listing URLs and platform IDs.
- **Automatic checks:** `tests/test_privacy.py` checks these rules (ignore patterns, no IDs combined with prices in shared result tables, no URLs or absolute paths in notebooks and documents).

## 3. Data rights: open questions

| Question | Status |
|---|---|
| Terms of use of Realitica and Estitor for automated collection | **Not documented** |
| Permission to redistribute the scraped listings | **Not documented** |
| Date or period of collection | **Not documented** (no date column) |
| Permission to use the professional appraisal reports | **Not documented** |
| Licence of the data | **None stated.** The MIT licence in `LICENSE` covers the **code only** |

No licences, dates or permissions are assumed.

## 4. Data in the original repository

The original project repository (`dsb_capstone-main`) contains both raw CSV files in its `data/` folder, including the appraisal document paths. If that repository is public, these paths are visible, and they remain in the **Git history** even if the files are deleted later.

- **`.gitignore` does not affect files that Git already tracks.** It only prevents new files from being added.
- **Removing a tracked file** requires deliberately untracking it.
- **Removing it from earlier commits** requires rewriting the history.

Both are decisions for the repository owner, together with the instructor. They are not part of this project's code.

## 5. What is shared

| Shared | Not shared |
|---|---|
| Notebooks with their outputs (aggregate tables, figures, a few illustrative rows with city, area and price only) | `data/raw/*.csv` and the legacy `data/*.csv` paths |
| Aggregate result tables, figures, and the settlement mapping table (built from the public Monstat register) | `data/processed/valora_apartments_clean.csv` and `exclusion_log.csv` (one row per advert) |
| Code, tests, documentation, archived research reports | Listing-level results: `split_assignment.csv`, `cv_folds.csv`, `test_predictions.csv`, `error_analysis_test.csv`, `luxury_predictions.csv`, `interval_cv_oof.csv`, `interval_test_predictions.csv` |
| My original notebooks (`archive/`; one with cleared outputs) | `data/private/`, `models/*.joblib`, virtual environments, caches |

All files that are not shared are recreated when the notebooks are run with a local copy of the raw data (see `data/README.md`).
