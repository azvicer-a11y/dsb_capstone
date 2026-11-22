# Data quality audit

All numbers come from the executed `notebooks/01_eda.ipynb` and the tables in `data/processed/` and `docs/results/`. The tests in `tests/test_data.py` check the key counts.

## 1. Provenance: 6,913 raw rows

| Provenance | Rows | `data_source` | `data_origin` | `is_synthetic` | URL | Decision |
|---|---|---|---|---|---|---|
| Real online listing | 1,986 | Online listing | REAL | False | yes | **Used** |
| Simulated | 2,000 | **Online listing** | SIMULATED | **False** | no | Excluded: artificial |
| Synthetic (generated) | 2,000 | Synthetic - generated | (empty) | True | no | Excluded: artificial |
| Appraisal, "reviewed" label | 50 | Professional appraisal - reviewed | (empty) | False | no | Excluded: a different target (valuation, not asking price) |
| Appraisal, "unverified" label | 877 | Professional appraisal - unverified | (empty) | False | no | Excluded: as above |

**Critical finding:** the simulated rows look like real listings in `data_source` and `is_synthetic`. A row counts as real only if `data_origin = REAL`, `izvor` is a real platform, `data_source = Online listing`, `is_synthetic = False` **and** a URL exists. Tests check every combination.

Ten columns are completely empty, among them `Listing_ID`, `Property_Type`, `Bedrooms`, `Floor`, `Condition`, `Year_Built`, `Price_per_m2_EUR`, `Data_Source`, `Land_Area_m2` and `verified_area_m2`.

## 2. Cleaning flow

Rules are applied in this order. A row gets only the first reason it meets.

| # | Step | Before | After | Affected | Type of problem |
|---|---|---|---|---|---|
| 1–4 | Exclude simulated / synthetic / appraisal (reviewed) / appraisal (unverified) | 6,913 | 1,986 | 2,000 / 2,000 / 50 / 877 | Not market data |
| 5 | Not an apartment: house or villa | 1,986 | 1,536 | 450 | Different property type |
| 6 | Not an apartment: unclear or commercial | 1,536 | 1,473 | 63 | Different property type |
| 7 | Typed *stan*, but the title says house (*kuću*) | 1,473 | 1,466 | 7 | **Misclassified type** |
| 8 | Price < €10,000 (€1,450–2,750 for 25–78 m²) | 1,466 | 1,430 | 36 | **Rental, not a sale** |
| 9 | Title price differs from `price_eur` by > 5% | 1,430 | 1,428 | 2 | **Data error** |
| 10 | Area < 15 m² (one row: 1 m²) | 1,428 | 1,427 | 1 | **Invalid physical value** |
| 11 | Exact re-post | 1,427 | 1,380 | 47 | **Duplicate** |
| 12 | Price > €2M or area > 350 m² | 1,380 | **1,376** | 4 | **Valid but extreme**: kept in the file, outside the primary population |

### Exact re-posts (approved decision D3)
- **Original records:** 1,427 valid real apartment listings at this step. 95 apartments were in exact-content groups before the other rules, and some of those had already been removed as rentals.
- **Criterion:** same platform, price, area, rooms, location text, title, description and bathrooms. Only the URL and platform ID differ.
- **Removed:** 47.
- **Which record is kept:** the one with the smallest platform ID, i.e. the oldest posting.
- The rule is deterministic, and a test checks that the kept twin always has the smaller ID.

### Rentals
There is a gap from €2,750 to €37,000 with no listings at all, so €10,000 is not a fine-tuned threshold. My own manual check flags (`provjera`) already marked all 36 rows ("PROVJERITI: cijena", "PROVJERITI", "sumnjivo niska cijena").

### Valid luxury listings (decision D5)

| City | Area | Price | €/m² |
|---|---|---|---|
| Podgorica | 450 m² | €1,500,000 | 3,333 |
| Budva | 400 m² | €950,000 | 2,375 |
| Budva | 347 m² | €3,300,000 | 9,510 |
| Unknown | 353 m² | €850,000 | 2,408 |

None of these looks like an error. They are outside my original ranges and are analysed in a sensitivity run (modelling section 8.4).

## 3. Variables

| Variable | Finding | Decision |
|---|---|---|
| `price_eur` | Complete. Primary median €178,750; middle 50% €130,000–263,000; max €1.75M | Target |
| `area_m2` | Complete. Median 60 m². Two Realitica rows have decimal areas without area in the title, probably computed by the scraper; they are kept | Input |
| `sobe` → `rooms` | 22 Estitor studios (*garsonjera*) stored as missing → set to 0. 216 primary listings (16%) truly missing (Realitica titles without a room count) | Input; filled in the pipeline with the training median plus a "missing" indicator |
| `kupatila` | 386 values, **all from Estitor** | Not used (it would encode the platform) |
| `opis` | 37 real descriptions mention a price | Never used as a feature, never exported |
| `naslov` | Contains price, area and rooms (Realitica); agent names (Adriatic) | Used only for type and price consistency checks; never exported |
| `cijena_po_m2`, `price_per_m2_calculated` | Exactly price ÷ area | EDA only (target leakage) |
| `simulated_*` | Artificial | Never used |

## 4. Location

| Version (primary, n = 1,376) | Known | Unknown |
|---|---|---|
| Platform `city` field (`city_original`) | 708 | **668 (48.5%)** |
| Explicit location text (`city_explicit`) | 1,087 | **289 (21.0%)** |
| + 15 reviewed settlements (`city_clean`) | 1,343 | **33 (2.4%)** |

| `city_method` (clean version) | Estitor | Realitica | Realitica Adriatic | Total |
|---|---|---|---|---|
| Original valid city | 398 | 277 | 30 | 705 |
| Explicit location match | 0 | 382 | 0 | 382 |
| Reviewed settlement mapping | 0 | 256 | 0 | 256 |
| Ambiguous | 0 | 21 | 0 | 21 |
| Conflict | 3 | 0 | 0 | 3 |
| Unknown | 0 | 9 | 0 | 9 |

- **Remaining unknowns:** Luštica (7), Centar (7), Zelenika (6), Pržno (6), Zeta (3, Estitor conflict), Gomila (2), "6" (1), Prijevor (1).
- **Never contradicts the platform:** the cleaned city disagrees with the platform city in **0** listings where both are known.
- The earlier `city_clean` of `valora_cleaned_step2.csv` had 703 unknowns among 1,473 apartments.

### Settlement mapping table (decision D4)

Applied mappings (review status `pending author review` in the reference file). "Primary listings" counts the primary listings each mapping located.

| Settlement | Municipality | Primary listings | Evidence | Ambiguity |
|---|---|---|---|---|
| Đenovići | Herceg Novi | 41 | Monstat 2023 code 212067; seen with "Herceg Novi" 6× in data | unique |
| Igalo | Herceg Novi | 33 | Monstat 212105 | unique |
| Kumbor | Herceg Novi | 29 | Monstat 212148 | unique |
| Topla | Herceg Novi | 28 | Monstat 216704 | unique |
| Bijela | Herceg Novi | 27 | Monstat 212032 (whole-token match only) | unique exact name |
| Savina | Herceg Novi | 14 | Monstat 216682 | unique |
| Baošići | Herceg Novi | 11 | Monstat 212024 | unique |
| Meljine | Herceg Novi | 10 | Monstat 212172 | unique |
| Njivice | Herceg Novi | 7 | Monstat 215643 | unique |
| Kamenari | Herceg Novi | 6 | Monstat 216674 | unique |
| Bečići | Budva | 31 | Monstat 202029 | unique |
| Rafailovići | Budva | 13 | Monstat 216666 | unique |
| Petrovac | Budva | 3 | Monstat "Petrovac Centar" 216445; no other Petrovac | unique (via Petrovac Centar) |
| Sveti Stefan | Budva | 2 | Monstat 202312 | unique |
| Kamenovo | Budva | 1 | Monstat 216283 | unique |

Total located by the mapping: **256** primary listings (Herceg Novi 206, Budva 50).

Not applied:

| Name | Status | Reason |
|---|---|---|
| Pržno | Candidate | Unique in Monstat (Budva), but it was not in the approved list |
| Ratiševina | Candidate | Unique in Monstat (Herceg Novi), but it was not in the approved list |
| Zelenika | Ambiguous | Herceg Novi in Monstat, but these adverts also use it as a Podgorica neighbourhood |
| Prijevor | Ambiguous | Two Monstat settlements, in Budva and Herceg Novi |
| Luštica | Ambiguous | A settlement and also a peninsula name |
| Centar | Ambiguous | A generic word |
| Gomila | Unknown | Not in Monstat |

The full table with counts per mapping is in `docs/results/settlement_mapping_review.csv`. The source is the official Monstat settlement register "Spisak naselja Crne Gore 2023" (XLSX from monstat.org), with Wikipedia (en/sh) municipality pages as a secondary source.

## 5. Probable repeats (groups for splitting)

- **Rule:** same cleaned city + neighbourhood token + price + area.
- **Result:** 172 listings in 74 groups, the largest with 8 listings. By platform: 40 groups Estitor only, 16 Realitica only, 1 Realitica Adriatic only, **17 Estitor + Realitica**.
- **Possible wrong links:** 3 groups where the room counts disagree, and 4 groups with 4+ listings (probably identical units in one new building). Wrong links cannot leak information. They only keep rows together on one side of a split, which makes the test slightly stricter, so no rows are deleted.
- **Not attempted:** fuzzy matching (similar but not identical price or area). Some repeats with small changes may remain undetected; this is a limitation.

## 6. Sample limitations

- Estitor: **Podgorica only**, at most 20 adverts per neighbourhood (26 neighbourhoods). This reflects how the data were collected, not the market.
- Realitica Adriatic: only 30 coastal listings.
- Within Podgorica, the platforms differ somewhat (medians: Estitor €169,000 / 63 m²; Realitica €150,000 / 60 m²).
- City statistics describe **this sample of adverts**, not the Montenegrin market.
- **No dates:** no time trends and no ARIMA.
