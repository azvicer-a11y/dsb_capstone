# Untouched original data

These files are copies of the files in the author's original project repository, **byte for byte**. They are never edited. `01_eda.ipynb` checks the checksum of the main file before using it.

| File | Provider/source URL | Obtained on | Collection period | License/terms | Checksum (SHA-256) |
|---|---|---|---|---|---|
| `VALORA_AI_FINAL_COLAB.csv` | Project author. Real rows: public adverts on realitica.com (incl. its Adriatic section) and estitor.com. Other rows: simulated, generated, and professional appraisal reports | Copied from the original repository ZIP on 2026-11-19 | **Not documented** (no date column) | **Not documented**; platform terms not checked; contains sensitive appraisal file paths | `d3ddafe175a736a91c8c276a821476a57bf73c2de346834058ce14cce5f973a3` |
| `valora_cleaned_step2.csv` | Project author (earlier cleaning step of the file above) | Same | Same | Same | `213990a84c326dc5525c1bf7c3655d6e700e99b20b8b82549d47da0e89d63424` |

## What the main file contains (6,913 rows × 59 columns)

| Provenance (how `01_eda.ipynb` classifies it) | Rows | Used? |
|---|---|---|
| Real online listings (`data_origin = REAL`, real platform, URL present) | 1,986 | Yes: the source of the analysis |
| Simulated (`data_origin = SIMULATED`), **mislabelled** as `data_source = "Online listing"`, `is_synthetic = False` | 2,000 | No |
| Synthetic, generated (`data_source = "Synthetic - generated"`) | 2,000 | No |
| Professional appraisals, "reviewed" label | 50 | No (different target: valuation, not asking price) |
| Professional appraisals, "unverified" label | 877 | No |

The "reviewed" and "unverified" labels belong to the dataset. Only 2 of the 50 "reviewed" rows say they were checked against the source PDF.
