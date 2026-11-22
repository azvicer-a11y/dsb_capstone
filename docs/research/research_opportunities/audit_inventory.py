"""Research-opportunity audit: DESCRIPTIVE inventory only (no model is trained).

Price-based statistics use only the 1,098 development listings of the final project;
the 278 test listings are excluded so they cannot influence the choice of a research question.
Run from the local workspace root (the folder that contains valora_ai/):  python -I -B -X utf8 research_opportunities/audit_inventory.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, 'research_opportunities/lib')
import valora_prep as vp  # noqa: E402

pd.set_option('display.width', 200); pd.set_option('display.max_rows', 200); pd.set_option('display.max_columns', 30)
OUT = Path('research_opportunities/results')
raw = vp.load_raw('valora_ai/data/raw/VALORA_AI_FINAL_COLAB.csv')
prov = vp.assign_provenance(raw)
settle, not_applied = vp.load_settlement_mapping('valora_ai/data/reference/settlement_mapping.csv')
real, flow = vp.clean_real_listings(raw, settle, not_applied)      # all 1,986 real rows, apartments cleaned
split = pd.read_csv('valora_ai/docs/results/split_assignment.csv')
test_ids = set(split.loc[split['split'] == 'test', 'record_id'])
dev_ids = set(pd.read_csv('valora_ai/docs/results/cv_folds.csv')['record_id'])

print('=== 1. COLUMN INVENTORY (real listings, n=1,986)')
r = raw[prov == vp.PROVENANCE_REAL]
inv = pd.DataFrame({'non_missing': r.notna().sum(), 'pct': (100 * r.notna().mean()).round(1), 'unique': r.nunique()})
inv = inv[inv['non_missing'] > 0].sort_values('pct', ascending=False)
print(inv.to_string()); inv.to_csv(OUT / 'column_inventory_real.csv')
print('\nplatform x column coverage (%):')
cov = r.groupby('izvor')[['sobe', 'kupatila', 'opis', 'lokacija', 'url']].apply(lambda g: (100 * g.notna().mean()).round(0))
print(cov)

print('\n=== 2. PROPERTY TYPE x PLATFORM (real)')
print(pd.crosstab(real['property_group'], real['platform'], margins=True))

print('\n=== 3. SALE vs RENT (real, all property types)')
rent = real['price_eur'] < vp.PRICE_MIN_SALE
print(pd.crosstab(real['property_group'], rent.map({True: 'rent (<€10k)', False: 'sale'}), margins=True))

print('\n=== 4. HOUSES: is a separate study feasible?')
h = real[real['property_group'] == 'House / villa'].copy()
h_title_price = vp.title_price(h['naslov'])
h['flag_rent'] = h['price_eur'] < vp.PRICE_MIN_SALE
h['flag_area_lt30'] = h['area_m2'] < 30
h['flag_area_decimal_parse'] = (h['area_m2'] % 1 != 0) & (h['area_m2'] < 10)      # e.g. '2.330 m2' parsed as 2.33
h['rooms'] = vp.rooms_from_listing(h)
hv = h[~h['flag_rent'] & ~h['flag_area_lt30']]
loc = hv.apply(lambda x: vp.resolve_city(x, settle, not_applied), axis=1, result_type='expand')
hv['city'] = loc[0]
print(f"real houses/villas: {len(h)} | rents: {h['flag_rent'].sum()} | area<30 m2 (parse/land issues): {h['flag_area_lt30'].sum()} | usable sale rows: {len(hv)}")
print('rooms known:', int(hv['rooms'].notna().sum()), '| bathrooms known:', int(hv['kupatila'].notna().sum()),
      '| real land area column available:', bool(r['land_area_m2'].notna().any()), '(land_area_m2 non-missing in real rows:', int(r['land_area_m2'].notna().sum()), ')')
print('house city coverage:', hv['city'].value_counts().to_dict())
print('house area quantiles (m2):', hv['area_m2'].quantile([.05, .5, .95]).round(0).to_dict())
print('house platform:', hv['platform'].value_counts().to_dict())

print('\n=== 5. APARTMENTS: coverage by city / neighbourhood (primary, n=1,376; counts only)')
apt = real[real['population'] == 'primary'].copy()
print('city:', apt['city_clean'].value_counts().to_dict())
nbkey = apt['neighbourhood'].map(vp.norm)
nbkey = np.where(nbkey.isin(vp.MUNICIPALITY_LOOKUP.keys()) | (nbkey == ''), '-', nbkey)
apt['city_nb'] = apt['city_clean'] + '|' + nbkey
c = apt.loc[~apt['city_nb'].str.endswith('|-'), 'city_nb'].value_counts()
print(f'sub-city places: {len(c)}, with >=10 listings: {(c >= 10).sum()} ({c[c >= 10].sum()} listings), >=20: {(c >= 20).sum()}')
coastal = {'Herceg Novi', 'Kotor', 'Tivat', 'Budva', 'Bar', 'Ulcinj'}   # the six coastal municipalities
print('coastal vs continental listings:', apt['city_clean'].map(lambda x: 'Unknown' if x == 'Unknown' else ('coastal' if x in coastal else 'continental')).value_counts().to_dict())

print('\n=== 6. FEATURES AVAILABLE WITHOUT PRICE (for clustering) - development set')
dev = apt[apt['record_id'].isin(dev_ids)].copy()
assert not set(dev['record_id']) & test_ids and len(dev) == 1098
print(f"non-price features: area_m2 100% | city_clean known {100 * dev['city_clean'].ne('Unknown').mean():.1f}% | rooms known {100 * dev['rooms'].notna().mean():.0f}% | is_studio")
print(f"neighbourhood (sub-city) known: {100 * (~dev['neighbourhood'].map(vp.norm).isin(list(vp.MUNICIPALITY_LOOKUP.keys()) + [''])).mean():.0f}%")
print('Spearman(area, rooms) on known rooms:', round(dev[['area_m2', 'rooms']].dropna().corr(method='spearman').iloc[0, 1], 2))

print('\n=== 7. DEVELOPMENT-ONLY descriptive price structure (no model)')
dev['ppm'] = dev['price_eur'] / dev['area_m2']
dev['region'] = dev['city_clean'].map(lambda x: 'Unknown' if x == 'Unknown' else ('coastal' if x in coastal else 'continental'))
print(dev.groupby('region')['ppm'].describe(percentiles=[.1, .5, .9]).round(0))
g = dev[dev['city_clean'] != 'Unknown'].groupby('city_clean')['ppm']
disp = pd.DataFrame({'n': g.size(), 'median_ppm': g.median(), 'IQR/median_%': 100 * (g.quantile(.75) - g.quantile(.25)) / g.median(),
                     'p10': g.quantile(.1), 'p90': g.quantile(.9)}).query('n >= 20').round(0)
print('within-city dispersion of €/m2 (dev, n>=20):'); print(disp.sort_values('median_ppm'))
disp.to_csv(OUT / 'dev_within_city_dispersion.csv')
# How wide would an EMPIRICAL 80% range be (city p10-p90 €/m2 x area)? -> relative width only
print('empirical city 80% €/m2 range relative to median (p90-p10)/median %:', ((disp['p90'] - disp['p10']) / disp['median_ppm'] * 100).round(0).to_dict())

print('\n=== 8. KNOWN DATA-QUALITY LABELS (usable to validate anomaly detection)')
print(real['exclusion_reason'].replace('', '(kept)').value_counts().to_string())
print('source manual check flag on kept apartments:', apt['provjera'].map(lambda s: 'OK' if vp.norm(s).startswith('ok') else 'check').value_counts().to_dict())

print('\n=== 9. OTHER CANDIDATE DATA')
appr = raw[prov.str.startswith('Appraisal')]
print('appraisals:', len(appr), '| property types:', appr['property_type'].value_counts().to_dict())
print('appraisals with price & area:', int((appr['price_eur'].notna() & appr['area_m2'].notna()).sum()), '| valuation_year known:', int(appr['valuation_year'].notna().sum()))
print('dates for real listings: none (checked in EDA 7.9)')
