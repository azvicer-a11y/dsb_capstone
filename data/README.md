[README.md](https://github.com/user-attachments/files/35446483/README.md)

# VALORA AI: Better Data, Better Predictions
**From Montenegro-Wide Listings to Detailed Property Valuation in Budva**

This project is a self-contained research extension of the VALORA AI capstone. It tests whether **richer property-level data** can predict **appraised apartment values in Budva** better than a traditional price-per-square-meter baseline.

> **Result (outcome B, promising but uncertain):**
> - **The validated machine-learning procedure** (nested model selection) reached a cross-validated MAE of **€42,250**.
> - **The strongest baseline**, the year median €/m² × area, reached **€45,030**.
> - **The difference:** 6.2% lower error (€2,780), better in 8 of 10 repeats.
> - **The uncertainty:** the 95% interval of the improvement (−€2,806 to €8,584) includes zero.
> - **Conclusion:** with 80 appraisals in 73 independent clusters, the advantage cannot be confirmed, so the €/m² rule remains the recommended method.

Start with **[START_HERE.md](START_HERE.md)** (steps for Windows), then read **[docs/RESEARCH_STORY.md](docs/RESEARCH_STORY.md)**.

## Data

| File | Content |
|---|---|
| `data/raw/VALORA_Budva_appraisals_shareable.csv` | 81 appraisals (80 Budva, 1 Kotor), 26 columns, 2021-2026; property and report numbers replaced by neutral codes |
| `data/processed/budva_model_data.csv` | the 80 Budva properties with derived columns (written by notebook 01) |
| `data/manifest.json` | SHA-256 of the data files |

- **The target is the appraised market value** (`market_value_eur`), not an asking price or a sale price. The results are **not** comparable with the asking-price models of the original VALORA AI.
- **The data are shared privately** for this capstone and must not be published (see [docs/LIMITATIONS.md](docs/LIMITATIONS.md)).

## Notebooks (run in this order)

| Notebook | Content |
|---|---|
| `01_data_audit.ipynb` | target provenance, data dictionary, all quality checks, audit table, descriptive figures |
| `02_feature_engineering.ipynb` | feature sets A/B/C, redundancy, leakage rules, grouped folds |
| `03_model_comparison.ipynb` | 5 baselines + 18 candidates + nested selection, 10 × grouped 5-fold nested CV (about 15 minutes) |
| `04_final_evaluation.ipynb` | paired comparison, decision rule, sensitivity analyses, temporal check, error analysis, final chart |

## Documents

| Document | Content |
|---|---|
| [docs/RESEARCH_STORY.md](docs/RESEARCH_STORY.md) | the whole research logic, from the original project to the conclusion |
| [docs/MODEL_COMPARISON.md](docs/MODEL_COMPARISON.md) | all results, tables and interpretation |
| [docs/EVALUATION_PROTOCOL.md](docs/EVALUATION_PROTOCOL.md) | the protocol locked before modelling |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | the method in plain terms |
| [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | all columns, target provenance, audit findings |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | what the experiment cannot show |

## Project structure

```
START_HERE.md, README.md, requirements.txt, LICENSE
setup_windows.bat     creates .venv and installs the tested packages
verify_project.bat    checks everything and prints PASS or FAIL (verify_project.py)
open_notebooks.bat    opens Jupyter in notebooks/
data/                 raw (shareable copy), processed, manifest.json
notebooks/            01-04, executed
src/                  budva_data, budva_features, budva_models, budva_eval, budva_plots
results/              all result tables (CSV/JSON), protocol lock, key numbers
figures/              15 presentation figures (PNG)
docs/                 the documents above
tests/                automatic tests (data, leakage, grouping, notebooks, privacy)
PRIVATE_STUDY_MATERIAL/   study guide, talk, slides plan, defence Q&A, checklist (not part of the public project)
```

## Reproduce

- **Windows:** `setup_windows.bat` → `verify_project.bat` → `open_notebooks.bat`.
- **Manual:** `python -m venv .venv`, then `.venv\Scripts\python -m pip install -r requirements.txt`, then run the notebooks in order.
- **Tested with:** Python 3.11.9 and the pinned versions in `requirements.txt`.
- **Tests:**
  - `python -m pytest` runs the fast tests.
  - `python -m pytest -m slow` re-runs all four notebooks in a temporary copy, about 40 minutes.
