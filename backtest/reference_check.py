"""Independent, slow, line-by-line re-implementation of the EA used to verify ea_engine.py.

It shares no code with the fast engine: bars and both moving averages are built
incrementally tick by tick, the way the terminal would, and OnTick is translated literally.
Run it on a short window and it asserts that both produce the same trades.

Usage:
    python reference_check.py --data-dir ../data --warmup 2022-02-01 --start 2022-03-01 --end 2022-04-01
"""
import argparse
import datetime as dt
import math

import numpy as np

import run_backtest as rb
import ea_engine as eng


def reference(t, bid, ask, start_ms, end_ms, p):
    bars = []          # [time, high, low, close]
    emas = []          # EMA value of each *closed* bar, same index as bars
    a = 2.0 / (p["slow"] + 1.0)
    setup, last_bar_time = 0, None
    pos = None
    balance = p["deposit"]
    trades = []

    def lwma_at(idx):  # LWMA of closes ending at bar idx
        n = p["fast"]
        if idx - n + 1 < 0:
            return float("nan")
        num = sum(bars[idx - j][3] * (n - j) for j in range(n))
        return num / (n * (n + 1) / 2)

    for ti, b, s in zip(t.tolist(), bid.tolist(), ask.tolist()):
        bt = ti // eng.BAR_MS * eng.BAR_MS
        if not bars or bars[-1][0] != bt:
            if bars:  # previous bar just closed -> its EMA is final
                c = bars[-1][3]
                emas.append(c if not emas else c * a + emas[-1] * (1 - a))
            bars.append([bt, b, b, b])
        else:
            bars[-1][1] = max(bars[-1][1], b)
            bars[-1][2] = min(bars[-1][2], b)
            bars[-1][3] = b
        if ti < start_ms:
            continue
        if ti >= end_ms:
            break

        if pos is not None:
            d, entry, sl, tp, lots, opened = pos
            px = None
            if d == 1 and b <= sl:
                px = b
            elif d == 1 and b >= tp:
                px = tp
            elif d == -1 and s >= sl:
                px = s
            elif d == -1 and s <= tp:
                px = tp
            if px is not None:
                profit = round((px - entry) * d * p["contract"] * lots, 2)
                balance += profit
                trades.append((opened, ti, d, lots, entry, sl, tp, px, profit))
                pos = None

        # ---- OnTick, literally ----
        cur = len(bars) - 1
        if bars[cur][0] == last_bar_time or cur < p["lookback"]:
            continue
        r1, r2 = bars[cur - 1], bars[cur - 2]
        w1, w2 = lwma_at(cur - 1), lwma_at(cur - 2)
        e1, e2 = emas[cur - 1], emas[cur - 2]
        down = e1 < e2 and w1 < w2 and r1[3] < e1
        up = e1 > e2 and w1 > w2 and r1[3] > e1
        if down and r2[3] > w2 and r1[3] < w1:
            setup = -1
        if up and r2[3] < w2 and r1[3] > w1:
            setup = 1
        if setup == -1 and r1[3] > w1:
            setup = 0
        if setup == 1 and r1[3] < w1:
            setup = 0
        if setup == -1 and pos is None and r1[1] >= w1 and r1[3] < w1:
            sl = max(x[1] for x in bars[cur - p["lookback"]:cur])
            tp = b - (sl - b) * p["rr"]
            lots = eng.calc_lot_size.py_func(b, sl, p["risk"], p["tick_size"], p["tick_value"],
                                             p["vmin"], p["vmax"], p["vstep"])
            if sl > s and tp < s and lots * p["contract"] * b / p["leverage"] <= balance:
                pos = (-1, b, sl, round(tp, p["digits"]), lots, ti)
            setup, last_bar_time = 0, bars[cur][0]
        if setup == 1 and pos is None and r1[2] <= w1 and r1[3] > w1:
            sl = min(x[2] for x in bars[cur - p["lookback"]:cur])
            tp = s + (s - sl) * p["rr"]
            lots = eng.calc_lot_size.py_func(s, sl, p["risk"], p["tick_size"], p["tick_value"],
                                             p["vmin"], p["vmax"], p["vstep"])
            if sl < b and tp > b and lots * p["contract"] * s / p["leverage"] <= balance:
                pos = (1, s, sl, round(tp, p["digits"]), lots, ti)
            setup, last_bar_time = 0, bars[cur][0]
    return trades


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--warmup", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = ap.parse_args()

    t, bid, ask = rb.load_ticks(args.data_dir, "XAUUSD", args.warmup, args.end)
    start_ms, end_ms = rb.to_ms(args.start), rb.to_ms(args.end)
    p = rb.DEFAULTS
    ref = reference(t, bid, ask, start_ms, end_ms, p)
    res = rb.run(t, bid, ask, start_ms, end_ms, p)
    fast = list(zip(res["open_t"], res["close_t"], res["dir"], res["lots"], res["entry"],
                    res["sl"], res["tp"], res["exit"], res["profit"]))
    fast = [x for x, r in zip(fast, res["reason"]) if r != eng.REASON_END]
    print(f"reference trades: {len(ref)}   engine trades: {len(fast)}")
    mismatches = 0
    for x, y in zip(ref, fast):
        same = all(math.isclose(float(u), float(v), rel_tol=0, abs_tol=1e-6) for u, v in zip(x, y))
        if not same:
            mismatches += 1
            if mismatches <= 5:
                print("MISMATCH\n  ref:", x, "\n  eng:", tuple(map(float, y)))
    assert len(ref) == len(fast) and mismatches == 0, "engine does not match reference"
    print(f"OK: all {len(ref)} trades identical, net {sum(r[-1] for r in ref):,.2f}")


if __name__ == "__main__":
    main()
