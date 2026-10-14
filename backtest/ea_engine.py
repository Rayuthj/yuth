"""Tick-by-tick replica of ThunderTrend_RetestEA.mq5 (v1.01) plus an MT5-style order model.

The EA logic is translated line for line, including its quirks:
  * `last_bar_time` is only updated when an order is sent, so OnTick runs on every tick
    of every bar except the rest of a bar in which an order was sent.
  * The breakout and the "retest" are checked on the same closed bar, so the EA can
    enter on the breakout candle itself.
  * `setup_state` and `last_bar_time` are updated even when the order is rejected.

Execution model (mirrors MT5 "Every tick based on real ticks"):
  * Bars are built from Bid prices; indicators use bar closes (PRICE_CLOSE).
  * On each tick the open position's SL/TP is checked first, then OnTick runs.
  * Sell fills at Bid and closes at Ask; Buy fills at Ask and closes at Bid.
  * TP fills at the TP price; SL fills at the first tick through it (gaps fill worse).
  * Orders are rejected for invalid stops (SL on the wrong side of the market) or
    insufficient free margin; the position is stopped out at the margin stop-out level.
"""
import numpy as np
from numba import njit

BAR_MS = 300_000  # M5

REASON_SL, REASON_TP, REASON_STOPOUT, REASON_END = 1, 2, 3, 4


def build_bars(t, bid):
    """M5 OHLC (Bid) bars from ticks. Returns bar arrays and each tick's bar index."""
    key = t // BAR_MS
    starts = np.concatenate(([0], np.flatnonzero(np.diff(key)) + 1))
    ends = np.append(starts[1:], len(t))
    bar_time = key[starts] * BAR_MS
    high = np.maximum.reduceat(bid, starts)
    low = np.minimum.reduceat(bid, starts)
    close = bid[ends - 1]
    tick_bar = np.repeat(np.arange(len(starts), dtype=np.int64), ends - starts)
    return bar_time, high, low, close, tick_bar


def lwma(x, period):
    """MT5 MODE_LWMA: weights 1 (oldest) .. period (newest)."""
    w = np.arange(1, period + 1, dtype=np.float64)
    out = np.full(len(x), np.nan)
    out[period - 1:] = np.convolve(x, w[::-1], "valid") / w.sum()
    return out


@njit(cache=True)
def ema(x, period):
    """MT5 MODE_EMA, seeded with the first price."""
    a = 2.0 / (period + 1.0)
    out = np.empty(len(x))
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * a + out[i - 1] * (1.0 - a)
    return out


@njit(cache=True)
def calc_lot_size(entry, sl, risk, tick_size, tick_value, vmin, vmax, vstep):
    """CalculateLotSize() from the EA."""
    d = abs(entry - sl)
    if d == 0:
        return vmin
    ticks_at_risk = d / tick_size
    lot = risk / (ticks_at_risk * tick_value)
    lot = np.floor(lot / vstep) * vstep
    if lot < vmin:
        lot = vmin
    if lot > vmax:
        lot = vmax
    digits = 2
    if vstep == 0.1:
        digits = 1
    if vstep == 1.0:
        digits = 0
    return round(lot, digits)


@njit(cache=True)
def simulate(t, bid, ask, tick_bar, bar_time, bar_high, bar_low, bar_close, wma, ema_,
             start_ms, end_ms, risk, lookback, rr, contract, tick_size, tick_value,
             vmin, vmax, vstep, leverage, deposit, stop_out_pct, commission_per_lot, digits):
    n_bars = len(bar_time)
    cap = 200_000
    tr_open_t = np.zeros(cap, np.int64)
    tr_close_t = np.zeros(cap, np.int64)
    tr_dir = np.zeros(cap, np.int8)
    tr_reason = np.zeros(cap, np.int8)
    tr_lots = np.zeros(cap)
    tr_entry = np.zeros(cap)
    tr_sl = np.zeros(cap)
    tr_tp = np.zeros(cap)
    tr_exit = np.zeros(cap)
    tr_profit = np.zeros(cap)
    tr_spread = np.zeros(cap)
    ntr = 0
    rej_stops = 0
    rej_money = 0

    bal_curve = np.full(n_bars, np.nan)
    eq_curve = np.full(n_bars, np.nan)
    eq_min_curve = np.full(n_bars, np.nan)

    balance = deposit
    setup = 0
    last_bar_time = -1
    pos = 0
    p_entry = 0.0
    p_sl = 0.0
    p_tp = 0.0
    p_lots = 0.0
    p_margin = 0.0
    peak_eq = deposit
    max_eq_dd = 0.0
    max_eq_dd_pct = 0.0
    peak_bal = deposit
    max_bal_dd = 0.0
    max_bal_dd_pct = 0.0
    last_i = -1

    for i in range(len(t)):
        ti = t[i]
        if ti < start_ms:
            continue
        if ti >= end_ms:
            break
        last_i = i
        b = bid[i]
        a = ask[i]
        k = tick_bar[i]

        # ---- 1. tester: SL / TP / stop-out on the open position ----
        if pos != 0:
            reason = 0
            px = 0.0
            if pos == 1:
                if b <= p_sl:
                    reason = REASON_SL
                    px = b
                elif b >= p_tp:
                    reason = REASON_TP
                    px = p_tp
                else:
                    eq = balance + (b - p_entry) * contract * p_lots
                    if eq * 100.0 <= p_margin * stop_out_pct:
                        reason = REASON_STOPOUT
                        px = b
            else:
                if a >= p_sl:
                    reason = REASON_SL
                    px = a
                elif a <= p_tp:
                    reason = REASON_TP
                    px = p_tp
                else:
                    eq = balance + (p_entry - a) * contract * p_lots
                    if eq * 100.0 <= p_margin * stop_out_pct:
                        reason = REASON_STOPOUT
                        px = a
            if reason != 0:
                profit = round((px - p_entry) * pos * contract * p_lots, 2)
                profit -= commission_per_lot * p_lots
                balance += profit
                tr_close_t[ntr] = ti
                tr_exit[ntr] = px
                tr_profit[ntr] = profit
                tr_reason[ntr] = reason
                ntr += 1
                pos = 0
                if balance > peak_bal:
                    peak_bal = balance
                if peak_bal - balance > max_bal_dd:
                    max_bal_dd = peak_bal - balance
                    max_bal_dd_pct = max_bal_dd / peak_bal * 100.0

        # ---- 2. EA OnTick ----
        if bar_time[k] != last_bar_time and k >= lookback and k >= 2:
            k1 = k - 1
            k2 = k - 2
            c1 = bar_close[k1]
            w1 = wma[k1]
            w2 = wma[k2]
            e1 = ema_[k1]
            e2 = ema_[k2]
            is_down = (e1 < e2) and (w1 < w2) and (c1 < e1)
            is_up = (e1 > e2) and (w1 > w2) and (c1 > e1)
            if is_down and bar_close[k2] > w2 and c1 < w1:
                setup = -1
            if is_up and bar_close[k2] < w2 and c1 > w1:
                setup = 1
            if setup == -1 and c1 > w1:
                setup = 0
            if setup == 1 and c1 < w1:
                setup = 0

            for side in (-1, 1):
                if setup != side or pos != 0:
                    continue
                if side == -1:
                    if not (bar_high[k1] >= w1 and c1 < w1):
                        continue
                    sl = bar_high[k - lookback]
                    for j in range(k - lookback + 1, k):
                        if bar_high[j] > sl:
                            sl = bar_high[j]
                    entry = b
                    tp = entry - (sl - entry) * rr
                    valid = sl > a and tp < a
                else:
                    if not (bar_low[k1] <= w1 and c1 > w1):
                        continue
                    sl = bar_low[k - lookback]
                    for j in range(k - lookback + 1, k):
                        if bar_low[j] < sl:
                            sl = bar_low[j]
                    entry = a
                    tp = entry + (entry - sl) * rr
                    valid = sl < b and tp > b
                lots = calc_lot_size(entry, sl, risk, tick_size, tick_value, vmin, vmax, vstep)
                margin = lots * contract * entry / leverage
                if not valid:
                    rej_stops += 1
                elif margin > balance:
                    rej_money += 1
                else:
                    pos = side
                    p_entry = entry
                    p_sl = sl
                    p_tp = round(tp, digits)
                    p_lots = lots
                    p_margin = margin
                    tr_open_t[ntr] = ti
                    tr_dir[ntr] = side
                    tr_lots[ntr] = lots
                    tr_entry[ntr] = entry
                    tr_sl[ntr] = sl
                    tr_tp[ntr] = p_tp
                    tr_spread[ntr] = a - b
                setup = 0
                last_bar_time = bar_time[k]

        # ---- equity / drawdown bookkeeping ----
        if pos == 1:
            eq = balance + (b - p_entry) * contract * p_lots
        elif pos == -1:
            eq = balance + (p_entry - a) * contract * p_lots
        else:
            eq = balance
        if eq > peak_eq:
            peak_eq = eq
        if peak_eq - eq > max_eq_dd:
            max_eq_dd = peak_eq - eq
            max_eq_dd_pct = max_eq_dd / peak_eq * 100.0
        if np.isnan(eq_min_curve[k]) or eq < eq_min_curve[k]:
            eq_min_curve[k] = eq
        bal_curve[k] = balance
        eq_curve[k] = eq

    # close anything still open at the end of the test
    if pos != 0 and last_i >= 0:
        px = bid[last_i] if pos == 1 else ask[last_i]
        profit = round((px - p_entry) * pos * contract * p_lots, 2) - commission_per_lot * p_lots
        balance += profit
        tr_close_t[ntr] = t[last_i]
        tr_exit[ntr] = px
        tr_profit[ntr] = profit
        tr_reason[ntr] = REASON_END
        ntr += 1
        bal_curve[tick_bar[last_i]] = balance
        eq_curve[tick_bar[last_i]] = balance

    return (tr_open_t[:ntr], tr_close_t[:ntr], tr_dir[:ntr], tr_lots[:ntr], tr_entry[:ntr],
            tr_sl[:ntr], tr_tp[:ntr], tr_exit[:ntr], tr_profit[:ntr], tr_reason[:ntr],
            tr_spread[:ntr], bal_curve, eq_curve, eq_min_curve,
            rej_stops, rej_money, max_eq_dd, max_eq_dd_pct, max_bal_dd, max_bal_dd_pct, balance)
