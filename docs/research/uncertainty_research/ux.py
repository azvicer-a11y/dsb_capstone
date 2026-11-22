"""Prediction-interval methods G1-G4 (exploratory). Everything learned is fitted inside the given training data."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import QuantileRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import valora_model as vm

SEED = 42
INPUTS = ['area_m2', 'rooms', 'city_clean']
MIN_CITY = 10
COMPLEXITY = {'G1': 1, 'G2a': 1, 'G2b': 1, 'G2c': 1, 'G3a': 2, 'G4a': 2, 'G3b': 3, 'G4b': 3}
LABELS = {'G1': 'Empirical city €/m² quantiles', 'G2a': 'Conformal, absolute residual', 'G2b': 'Conformal, relative residual',
          'G2c': 'Conformal, log residual', 'G3a': 'Linear quantile regression', 'G3b': 'Quantile gradient boosting',
          'G4a': 'CQR on linear QR', 'G4b': 'CQR on quantile GB'}
QCROSS = {'count': 0}          # quantile-crossing counter (reported)


def conformal_quantile(scores, alpha):
    """Finite-sample split-conformal quantile: k-th smallest score, k = ceil((n+1)(1-alpha))."""
    s = np.sort(np.asarray(scores, dtype=float))
    n = len(s)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if k > n else s[k - 1]


def fit_cal_split(train):
    """Group-aware 75 / 25 split of a training set into fit and calibration parts."""
    fit_idx, cal_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=SEED)
                            .split(train, groups=train['repeat_group']))
    return train.iloc[fit_idx], train.iloc[cal_idx]


# ---------------------------------------------------------------- base learners
def _rule(train):
    return vm.CityPricePerM2Baseline('city_clean', min_count=MIN_CITY).fit(train, train['price_eur'].to_numpy(float))


def _qr_pipeline(q):
    ct = ColumnTransformer([
        ('num', Pipeline([('imp', SimpleImputer(strategy='median', add_indicator=True)), ('sc', StandardScaler())]), ['log_area', 'rooms']),
        ('city', OneHotEncoder(handle_unknown='infrequent_if_exist', min_frequency=MIN_CITY, sparse_output=False), ['city_clean'])])
    return Pipeline([('ct', ct), ('qr', QuantileRegressor(quantile=q, alpha=0.0, solver='highs'))])


def _qgb_pipeline(q):
    return vm.make_model_pipeline('D: clean city + engineered', HistGradientBoostingRegressor(
        loss='quantile', quantile=q, learning_rate=0.05, max_iter=200, max_leaf_nodes=8, min_samples_leaf=40, random_state=SEED))


def _fit_quantiles(kind, train, qs):
    """Fit one model per quantile on log price; return a predict function giving log-quantiles."""
    X = train[INPUTS].assign(log_area=np.log(train['area_m2']))
    ylog = np.log(train['price_eur'].to_numpy(float))
    models = {q: (_qr_pipeline(q) if kind == 'qr' else _qgb_pipeline(q)).fit(X if kind == 'qr' else train[INPUTS], ylog) for q in qs}

    def predict(df):
        Xd = df[INPUTS].assign(log_area=np.log(df['area_m2']))
        return {q: m.predict(Xd if kind == 'qr' else df[INPUTS]) for q, m in models.items()}
    return predict


def _ordered(lo, hi):
    cross = lo > hi
    QCROSS['count'] += int(cross.sum())
    return np.where(cross, hi, lo), np.where(cross, lo, hi)


# ---------------------------------------------------------------- methods
def predict_interval(method, train, test, alpha):
    """Return (lower, upper, central) in EUR for the rows of `test`."""
    area = test['area_m2'].to_numpy(float)
    if method == 'G1':
        rule = _rule(train)
        ppm = train['price_eur'] / train['area_m2']
        counts = train['city_clean'].value_counts()
        ok = [c for c in counts.index[counts >= MIN_CITY] if c != 'Unknown']
        qlo = ppm.groupby(train['city_clean']).quantile(alpha / 2).reindex(ok)
        qhi = ppm.groupby(train['city_clean']).quantile(1 - alpha / 2).reindex(ok)
        glo, ghi = ppm.quantile(alpha / 2), ppm.quantile(1 - alpha / 2)
        lo = test['city_clean'].map(qlo).fillna(glo).to_numpy(float) * area
        hi = test['city_clean'].map(qhi).fillna(ghi).to_numpy(float) * area
        return lo, hi, rule.predict(test)

    if method in ('G2a', 'G2b', 'G2c'):
        fit, cal = fit_cal_split(train)
        rule = _rule(fit)
        yc, pc = cal['price_eur'].to_numpy(float), rule.predict(cal)
        pt = rule.predict(test)
        if method == 'G2a':
            q = conformal_quantile(np.abs(yc - pc), alpha)
            return np.maximum(pt - q, 1.0), pt + q, pt
        if method == 'G2b':
            q = conformal_quantile(np.abs(yc - pc) / pc, alpha)
            return np.maximum(pt * (1 - q), 1.0), pt * (1 + q), pt
        q = conformal_quantile(np.abs(np.log(yc) - np.log(pc)), alpha)
        return pt * np.exp(-q), pt * np.exp(q), pt

    kind = 'qr' if method in ('G3a', 'G4a') else 'qgb'
    qs = (alpha / 2, 0.5, 1 - alpha / 2)
    if method in ('G3a', 'G3b'):
        pr = _fit_quantiles(kind, train, qs)(test)
        lo, hi = _ordered(pr[qs[0]], pr[qs[2]])
        return np.exp(lo), np.exp(hi), np.exp(pr[0.5])
    # CQR (G4a, G4b)
    fit, cal = fit_cal_split(train)
    predict = _fit_quantiles(kind, fit, qs)
    pc = predict(cal)
    clo, chi = _ordered(pc[qs[0]], pc[qs[2]])
    ylc = np.log(cal['price_eur'].to_numpy(float))
    Q = conformal_quantile(np.maximum(clo - ylc, ylc - chi), alpha)
    pt = predict(test)
    lo, hi = _ordered(pt[qs[0]], pt[qs[2]])
    return np.exp(lo - Q), np.exp(hi + Q), np.exp(pt[0.5])


# ---------------------------------------------------------------- metrics
def interval_metrics(y, lo, hi, center, alpha):
    y = np.asarray(y, float)
    covered = (y >= lo) & (y <= hi)
    width = hi - lo
    score = width + (2 / alpha) * (lo - y) * (y < lo) + (2 / alpha) * (y - hi) * (y > hi)
    def pinball(pred, tau):
        d = y - pred
        return np.maximum(tau * d, (tau - 1) * d)
    return {'coverage': covered.mean(), 'mean_width': width.mean(), 'median_width': np.median(width),
            'median_rel_width': np.median(width / center), 'interval_score': score.mean(),
            'pinball': 0.5 * (pinball(lo, alpha / 2).mean() + pinball(hi, 1 - alpha / 2).mean()),
            'central_mae': np.mean(np.abs(y - center)),
            'miss_above_%': 100 * np.mean(y > hi), 'miss_below_%': 100 * np.mean(y < lo)}
