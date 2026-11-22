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
