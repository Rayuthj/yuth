"""
Research backtester for the TradingView trendline scripts in ../tradingview/.

It re-implements the same trendline engine used by the Pine scripts
(pivot detection -> connect pivots -> validate -> extend -> break) and compares
several ways to trade those trendlines on public OHLC datasets. Results are in
R-multiples (1R = initial risk per trade) so different markets are comparable.

Usage:
    python3 research/trendline_backtest.py            # downloads data, runs grid
    python3 research/trendline_backtest.py --data DIR # use CSVs already in DIR

This is a research approximation of TradingView's broker emulator, not a
replacement for the Strategy Tester. Always confirm in TradingView.
"""

import argparse
import itertools
import os
import sys
import urllib.request
from dataclasses import dataclass

import numpy as np
import pandas as pd

DATASETS = {
    # name: (url, round-trip cost as a fraction of price)
    "GOOG_D": ("https://raw.githubusercontent.com/kernc/backtesting.py/master/backtesting/test/GOOG.csv", 0.001),
    "NVDA_D": ("https://raw.githubusercontent.com/mementum/backtrader/master/datas/nvda-1999-2014.txt", 0.001),
    "ORCL_D": ("https://raw.githubusercontent.com/mementum/backtrader/master/datas/orcl-1995-2014.txt", 0.001),
    "YHOO_D": ("https://raw.githubusercontent.com/mementum/backtrader/master/datas/yhoo-1996-2014.txt", 0.001),
    "EURUSD_H1": ("https://raw.githubusercontent.com/kernc/backtesting.py/master/backtesting/test/EURUSD.csv", 0.00015),
    "INDEX_M5": ("https://raw.githubusercontent.com/mementum/backtrader/master/datas/2006-min-005.txt", 0.0002),
}


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def load(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    if "Adj Close" in df.columns:  # split/dividend-adjust OHLC so splits are not fake breaks
        f = df["Adj Close"] / df["Close"]
        for c in ("Open", "High", "Low", "Close"):
            df[c] = df[c] * f
    df = df[(df["High"] > 0) & (df["Low"] > 0)].reset_index(drop=True)
    return {k: df[k].to_numpy(float) for k in ("Open", "High", "Low", "Close")}


def fetch(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    for name, (url, _) in DATASETS.items():
        path = os.path.join(data_dir, name + ".csv")
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)


# ----------------------------------------------------------------------------
# Indicators (same definitions as Pine's ta.atr / ta.ema)
# ----------------------------------------------------------------------------
def atr(h, l, c, n=14):
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    out = np.full_like(c, np.nan)
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def ema(x, n):
    out = np.empty_like(x)
    a = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


# ----------------------------------------------------------------------------
# Trendline engine (mirrors the Pine implementation)
# ----------------------------------------------------------------------------
@dataclass
class Line:
    x1: int
    y1: float
    slope: float
    x2: int          # second anchor bar
    touches: int
    is_res: bool


def detect_events(d, piv=5, mode="all", wick=False, tol=0.1, max_conn=3,
                  memory=10, max_span=300, min_touches=2, max_age=150, buf=0.0, max_active=40):
    """Walk bar by bar; return per-bar trendline events.

    bull_break[t]  close crossed above an active resistance line on bar t
    bear_break[t]  close crossed below an active support line on bar t
    bull_bounce[t] bar t tagged an active support line and closed bullish above it
    bear_bounce[t] bar t tagged an active resistance line and closed bearish below it
    """
    o, h, l, c = d["Open"], d["High"], d["Low"], d["Close"]
    n = len(c)
    a = atr(h, l, c)
    hi_src = h if wick else c
    lo_src = l if wick else c
    ev = {k: np.zeros(n, bool) for k in ("bull_break", "bear_break", "bull_bounce", "bear_bounce")}
    active = []
    ph, pl = [], []  # stored pivots: (bar, price)

    for t in range(n):
        if np.isnan(a[t]):
            continue
        # 1) update active lines with this bar
        keep = []
        for ln in active:
            v = ln.y1 + ln.slope * (t - ln.x1)
            if ln.is_res:
                if c[t] > v + buf * a[t]:
                    ev["bull_break"][t] = True
                    continue
                if h[t] >= v - tol * a[t] and c[t] < v and c[t] < o[t]:
                    ev["bear_bounce"][t] = True
            else:
                if c[t] < v - buf * a[t]:
                    ev["bear_break"][t] = True
                    continue
                if l[t] <= v + tol * a[t] and c[t] > v and c[t] > o[t]:
                    ev["bull_bounce"][t] = True
            if t - ln.x2 <= max_age:
                keep.append(ln)
        active = keep

        # 2) new pivots confirmed on this bar -> new lines
        p = t - piv
        if p - piv < 0:
            continue
        tolv = tol * a[t]
        for is_res in (True, False):
            src = h if is_res else l
            win_l = src[p - piv:p]
            win_r = src[p + 1:t + 1]
            if is_res:
                is_piv = src[p] > win_l.max() and src[p] >= win_r.max()
            else:
                is_piv = src[p] < win_l.min() and src[p] <= win_r.min()
            if not is_piv:
                continue
            store = ph if is_res else pl
            xb, yb = p, src[p]
            made = 0
            for j in range(len(store) - 1, -1, -1):
                if made >= max_conn:
                    break
                xa, ya = store[j]
                if xb - xa > max_span:
                    break
                if mode == "classic" and ((is_res and ya <= yb) or (not is_res and ya >= yb)):
                    continue
                slope = (yb - ya) / (xb - xa)
                xs = np.arange(xa + 1, t + 1)
                lv = ya + slope * (xs - xa)
                if is_res and np.any(hi_src[xa + 1:t + 1] > lv + tolv):
                    continue
                if not is_res and np.any(lo_src[xa + 1:t + 1] < lv - tolv):
                    continue
                touches = 2 + sum(1 for (xk, yk) in store[j + 1:]
                                  if abs(yk - (ya + slope * (xk - xa))) <= tolv)
                if touches < min_touches:
                    continue
                active.append(Line(xa, ya, slope, xb, touches, is_res))
                made += 1
                same = [k for k, a_ln in enumerate(active) if a_ln.is_res == is_res]
                if len(same) > max_active:  # same per-side cap as the Pine scripts
                    active.pop(same[0])
            store.append((xb, yb))
            if len(store) > memory:
                store.pop(0)
    return ev, a


# ----------------------------------------------------------------------------
# Trade simulation: signal on bar close, fill next bar open, stop-first intrabar
# ----------------------------------------------------------------------------
def simulate(d, ev, a, signal="breakout", trend=None, side="both", sl_atr=2.0,
             rr=2.0, trail_atr=None, cost=0.001, start=0, end=None):
    o, h, l, c = d["Open"], d["High"], d["Low"], d["Close"]
    n = len(c) if end is None else end
    ma = ema(c, trend) if trend else None
    if signal == "breakout":
        long_sig, short_sig = ev["bull_break"], ev["bear_break"]
    else:
        long_sig, short_sig = ev["bull_bounce"], ev["bear_bounce"]
    trades = []
    t = max(start, 1)
    while t < n - 1:
        go_long = long_sig[t] and side in ("both", "long") and (ma is None or c[t] > ma[t])
        go_short = short_sig[t] and side in ("both", "short") and (ma is None or c[t] < ma[t])
        if not (go_long or go_short) or np.isnan(a[t]):
            t += 1
            continue
        dirn = 1 if go_long else -1
        stop = c[t] - dirn * sl_atr * a[t]
        tp = c[t] + dirn * rr * sl_atr * a[t] if rr else None
        entry = o[t + 1]
        risk = dirn * (entry - stop)
        if risk <= 0:  # opened beyond the stop: the stop fills at that same open
            trades.append(-cost * entry / (sl_atr * a[t]))
            t += 1
            continue
        ext = entry
        exit_px = None
        k = t + 1
        while k < n:
            if trail_atr:
                ext = max(ext, h[k]) if dirn == 1 else min(ext, l[k])
            # stop first (conservative), then target
            if dirn == 1:
                if l[k] <= stop:
                    exit_px = min(o[k], stop)
                elif tp is not None and h[k] >= tp:
                    exit_px = max(o[k], tp)
            else:
                if h[k] >= stop:
                    exit_px = max(o[k], stop)
                elif tp is not None and l[k] <= tp:
                    exit_px = min(o[k], tp)
            if exit_px is not None:
                break
            if trail_atr and not np.isnan(a[k]):
                new_stop = ext - dirn * trail_atr * a[k]
                stop = max(stop, new_stop) if dirn == 1 else min(stop, new_stop)
            k += 1
        if exit_px is None:
            exit_px = c[n - 1]
            k = n - 1
        r = dirn * (exit_px - entry) / risk - cost * entry / risk
        trades.append(r)
        t = k  # like TradingView, a new signal may fire on the bar a trade exits
    return np.array(trades)


def stats(r):
    if len(r) == 0:
        return dict(n=0, win=np.nan, avgR=np.nan, pf=np.nan, totR=0.0, ddR=0.0)
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq).max()
    gains, losses = r[r > 0].sum(), -r[r < 0].sum()
    return dict(n=len(r), win=(r > 0).mean(), avgR=r.mean(),
                pf=gains / losses if losses > 0 else np.inf, totR=r.sum(), ddR=dd)


# ----------------------------------------------------------------------------
# Experiment
# ----------------------------------------------------------------------------
DETECT_GRID = dict(piv=[5, 10, 20], mode=["all", "classic"], wick=[False], min_touches=[2, 3])
TRADE_GRID = dict(
    signal=["breakout", "bounce"],
    trend=[None, 200],
    side=["both", "long"],
    exit=[("fixed", 1.5, 1.5), ("fixed", 2.0, 2.0), ("fixed", 2.0, 3.0), ("trail", 2.0, 3.0)],
)
IS_FRACTION = 0.6  # first 60% of every dataset is in-sample, last 40% out-of-sample
RANDOM_SEEDS = 10  # random-entry baseline runs per test (same signal rate, filters and exits)


def random_baseline(d, ev, a, tcfg, cost, start, end, seeds=RANDOM_SEEDS):
    """Average R of random entries at the same signal rate. Beating this means the
    trendline adds information beyond market drift and the exit rules."""
    n = len(d["Close"])
    key_l, key_s = ("bull_break", "bear_break") if tcfg["signal"] == "breakout" else ("bull_bounce", "bear_bounce")
    rate_l, rate_s = ev[key_l].mean(), ev[key_s].mean()
    out = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        rl, rs = rng.random(n) < rate_l, rng.random(n) < rate_s
        rev = {key_l: rl, key_s: rs}
        r = simulate(d, rev, a, cost=cost, start=start, end=end, **tcfg)
        if len(r):
            out.append(r.mean())
    return float(np.mean(out)) if out else np.nan


def run(data_dir):
    data = {k: load(os.path.join(data_dir, k + ".csv")) for k in DATASETS}
    rows = []
    dkeys, tkeys = list(DETECT_GRID), list(TRADE_GRID)
    for dvals in itertools.product(*DETECT_GRID.values()):
        dcfg = dict(zip(dkeys, dvals))
        events = {k: detect_events(v, **dcfg) for k, v in data.items()}
        for tvals in itertools.product(*TRADE_GRID.values()):
            tcfg = dict(zip(tkeys, tvals))
            kind, sl, x = tcfg.pop("exit")
            tcfg.update(sl_atr=sl, rr=None if kind == "trail" else x,
                        trail_atr=x if kind == "trail" else None)
            for name, d in data.items():
                ev, a = events[name]
                split = int(len(d["Close"]) * IS_FRACTION)
                for part, (s, e) in {"IS": (0, split), "OOS": (split, None)}.items():
                    cost = DATASETS[name][1]
                    r = simulate(d, ev, a, cost=cost, start=s, end=e, **tcfg)
                    st = stats(r)
                    st["edge"] = st["avgR"] - random_baseline(d, ev, a, tcfg, cost, s, e)
                    rows.append(dict(**dcfg, **{k: v for k, v in tcfg.items()},
                                     exit=f"{kind} sl{sl} x{x}", data=name, part=part, **st))
    return pd.DataFrame(rows)


MIN_IS_TRADES = 100  # ignore variants with too few in-sample trades to judge


def summarize(df):
    """Pool trades across datasets per variant. Columns ending in _IS / _OOS:
    trades, R (avg R per trade), edge (avg R minus random entries), profitable and
    beats (datasets with positive total R / positive edge, out of 6)."""
    cfg = ["piv", "mode", "min_touches", "signal", "trend", "side", "exit"]
    df = df.copy()
    df["trend"] = df["trend"].fillna(0).astype(int)
    df["edge_x_n"] = df["edge"].fillna(0) * df["n"]
    g = df.groupby(cfg + ["part"]).agg(
        trades=("n", "sum"), totR=("totR", "sum"), edgeSum=("edge_x_n", "sum"),
        profitable=("totR", lambda s: int((s > 0).sum())),
        beats=("edge", lambda s: int((s > 0).sum()))).reset_index()
    g["R"] = g["totR"] / g["trades"]
    g["edge"] = g["edgeSum"] / g["trades"]
    wide = g.pivot_table(index=cfg, columns="part",
                         values=["trades", "R", "edge", "profitable", "beats"]).reset_index()
    wide.columns = ["_".join(c).strip("_") for c in wide.columns]
    wide = wide[wide["trades_IS"] >= MIN_IS_TRADES]
    # rank on in-sample only; out-of-sample columns are reported, never optimized on
    cols = cfg + [f"{m}_{p}" for m in ("trades", "R", "edge", "profitable", "beats") for p in ("IS", "OOS")]
    return wide.sort_values("edge_IS", ascending=False)[cols]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "data"))
    ap.add_argument("--out", default=None, help="write the full results table to this CSV")
    args = ap.parse_args()
    fetch(args.data)
    res = run(args.data)
    if args.out:
        res.to_csv(args.out, index=False)
    pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 80)
    s = summarize(res)
    print(s.head(20).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    sys.exit(0)
