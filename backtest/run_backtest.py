"""Backtest ThunderTrend_RetestEA on real Dukascopy XAUUSD ticks and write the report.

Usage:
    python download_dukascopy.py --data-dir ../data --start 2021-09-01 --end 2026-10-01
    python run_backtest.py --data-dir ../data --out ../results \
        --warmup 2021-09-01 --start 2021-10-01 --end 2026-10-01
"""
import argparse
import datetime as dt
import json
import os

import numpy as np
import pandas as pd

import ea_engine as eng

PRICE_DIVISOR = 1000.0  # Dukascopy XAUUSD prices are in 0.001 points

# EA inputs + symbol/account spec. Symbol spec follows a typical MT5 XAUUSD contract
# (100 oz per lot, 0.01 lot step); account follows the MT5 tester defaults.
DEFAULTS = dict(
    risk=250.0, lookback=10, rr=2.0, fast=21, slow=200,             # EA inputs
    contract=100.0, tick_size=0.001, tick_value=0.1, digits=3,      # 1 lot = 100 oz
    vmin=0.01, vmax=100.0, vstep=0.01,
    deposit=10_000.0, leverage=100.0, stop_out=50.0, commission=0.0,
)


def to_ms(d):
    return int(dt.datetime.combine(d, dt.time(), tzinfo=dt.timezone.utc).timestamp()) * 1000


def load_ticks(data_dir, sym, start, end):
    ts, bids, asks = [], [], []
    y, m = start.year, start.month
    while (y, m) < (end.year, end.month) or (y, m) == (end.year, end.month) and end.day > 1:
        path = os.path.join(data_dir, "npz", f"{sym}_{y:04d}_{m:02d}.npz")
        z = np.load(path)
        ts.append(z["t"]); bids.append(z["bid"]); asks.append(z["ask"])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    t = np.concatenate(ts)
    bid = np.concatenate(bids) / PRICE_DIVISOR
    ask = np.concatenate(asks) / PRICE_DIVISOR
    keep = (t >= to_ms(start)) & (t < to_ms(end))
    t, bid, ask = t[keep], bid[keep], ask[keep]
    if np.any(np.diff(t) < 0):
        raise ValueError("ticks are not in time order")
    med = float(np.median(bid))
    if not 500 < med < 20_000:
        raise ValueError(f"median bid {med} looks wrong for XAUUSD; check PRICE_DIVISOR")
    return t, bid, ask


def run(t, bid, ask, start_ms, end_ms, p):
    bar_time, high, low, close, tick_bar = eng.build_bars(t, bid)
    wma = eng.lwma(close, p["fast"])
    ema = eng.ema(close, p["slow"])
    out = eng.simulate(t, bid, ask, tick_bar, bar_time, high, low, close, wma, ema,
                       start_ms, end_ms, p["risk"], p["lookback"], p["rr"], p["contract"],
                       p["tick_size"], p["tick_value"], p["vmin"], p["vmax"], p["vstep"],
                       p["leverage"], p["deposit"], p["stop_out"], p["commission"], p["digits"])
    keys = ["open_t", "close_t", "dir", "lots", "entry", "sl", "tp", "exit", "profit", "reason",
            "spread", "bal_curve", "eq_curve", "eq_min_curve", "rej_stops", "rej_money",
            "max_eq_dd", "max_eq_dd_pct", "max_bal_dd", "max_bal_dd_pct", "final_balance"]
    res = dict(zip(keys, out))
    res["bar_time"] = bar_time
    return res


def max_streak(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def trades_frame(res):
    reasons = {eng.REASON_SL: "stop loss", eng.REASON_TP: "take profit",
               eng.REASON_STOPOUT: "stop out", eng.REASON_END: "end of test"}
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(res["open_t"], unit="ms"),
        "type": np.where(res["dir"] == 1, "buy", "sell"),
        "lots": res["lots"],
        "entry": res["entry"],
        "sl": res["sl"],
        "tp": res["tp"],
        "spread_at_entry": res["spread"].round(3),
        "close_time_utc": pd.to_datetime(res["close_t"], unit="ms"),
        "exit": res["exit"],
        "exit_reason": [reasons[r] for r in res["reason"]],
        "profit": res["profit"].round(2),
    })
    df["sl_distance"] = (df["entry"] - df["sl"]).abs().round(3)
    df["balance"] = (DEFAULTS["deposit"] + df["profit"].cumsum()).round(2)
    return df


def summarize(df, res, p, n_ticks, start, end):
    pr = df["profit"]
    wins, losses = pr[pr > 0], pr[pr <= 0]
    net = float(pr.sum())
    s = {
        "period": f"{start} to {end}",
        "ticks_used": int(n_ticks),
        "initial_deposit": p["deposit"],
        "final_balance": round(float(res["final_balance"]), 2),
        "total_net_profit": round(net, 2),
        "gross_profit": round(float(wins.sum()), 2),
        "gross_loss": round(float(losses.sum()), 2),
        "profit_factor": round(float(wins.sum() / -losses.sum()), 2) if len(losses) and losses.sum() else None,
        "expected_payoff": round(float(pr.mean()), 2) if len(pr) else None,
        "total_trades": int(len(df)),
        "win_rate_pct": round(100 * len(wins) / len(df), 2) if len(df) else None,
        "long_trades": int((df["type"] == "buy").sum()),
        "long_win_pct": round(100 * float((pr[df["type"] == "buy"] > 0).mean()), 2) if (df["type"] == "buy").any() else None,
        "short_trades": int((df["type"] == "sell").sum()),
        "short_win_pct": round(100 * float((pr[df["type"] == "sell"] > 0).mean()), 2) if (df["type"] == "sell").any() else None,
        "largest_win": round(float(wins.max()), 2) if len(wins) else None,
        "largest_loss": round(float(losses.min()), 2) if len(losses) else None,
        "avg_win": round(float(wins.mean()), 2) if len(wins) else None,
        "avg_loss": round(float(losses.mean()), 2) if len(losses) else None,
        "max_consecutive_wins": max_streak((pr > 0).tolist()),
        "max_consecutive_losses": max_streak((pr <= 0).tolist()),
        "balance_drawdown_max": round(float(res["max_bal_dd"]), 2),
        "balance_drawdown_max_pct": round(float(res["max_bal_dd_pct"]), 2),
        "equity_drawdown_max": round(float(res["max_eq_dd"]), 2),
        "equity_drawdown_max_pct": round(float(res["max_eq_dd_pct"]), 2),
        "recovery_factor": round(net / float(res["max_eq_dd"]), 2) if res["max_eq_dd"] else None,
        "orders_rejected_invalid_stops": int(res["rej_stops"]),
        "orders_rejected_no_money": int(res["rej_money"]),
        "exits": df["exit_reason"].value_counts().to_dict(),
        "median_sl_distance_usd": round(float(df["sl_distance"].median()), 3) if len(df) else None,
        "median_spread_at_entry_usd": round(float(df["spread_at_entry"].median()), 3) if len(df) else None,
        "median_lots": round(float(df["lots"].median()), 2) if len(df) else None,
        "max_lots": round(float(df["lots"].max()), 2) if len(df) else None,
        "settings": p,
    }
    yearly = df.groupby(df["close_time_utc"].dt.year).agg(
        trades=("profit", "size"), net_profit=("profit", "sum"),
        win_rate_pct=("profit", lambda x: 100 * (x > 0).mean()))
    s["yearly"] = {int(y): {"trades": int(r.trades), "net_profit": round(float(r.net_profit), 2),
                            "win_rate_pct": round(float(r.win_rate_pct), 1)}
                   for y, r in yearly.iterrows()}
    return s


def plot(res, s, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter

    surface, ink, ink2, muted, grid, base = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
    blue, orange, red = "#2a78d6", "#eb6834", "#e34948"

    ok = ~np.isnan(res["bal_curve"])
    x = pd.to_datetime(res["bar_time"][ok], unit="ms")
    bal = res["bal_curve"][ok]
    eq = res["eq_min_curve"][ok]
    dd = np.maximum.accumulate(np.maximum(bal, eq)) - eq

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": ink,
                         "axes.labelcolor": ink2, "xtick.color": muted, "ytick.color": muted})
    fig = plt.figure(figsize=(13, 9.5), facecolor=surface)
    gs = fig.add_gridspec(3, 1, height_ratios=[3.2, 1.1, 1.4], hspace=0.42)
    money = FuncFormatter(lambda v, _: f"-${abs(v)/1000:,.0f}K" if v < 0 and abs(v) >= 1000
                          else (f"${v/1000:,.0f}K" if abs(v) >= 1000 else f"${v:,.0f}"))

    def style(ax):
        ax.set_facecolor(surface)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(base)
        ax.grid(axis="y", color=grid, linewidth=1)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)

    ax = fig.add_subplot(gs[0])
    style(ax)
    ax.plot(x, eq, color=orange, linewidth=1.0, label="Equity (lowest per bar)", solid_joinstyle="round")
    ax.plot(x, bal, color=blue, linewidth=2.0, label="Balance", solid_joinstyle="round")
    ax.axhline(s["initial_deposit"], color=base, linewidth=1)
    ax.yaxis.set_major_formatter(money)
    ax.legend(loc="upper left", frameon=False, labelcolor=ink2)
    ax.annotate(f"${bal[-1]:,.0f}", (x[-1], bal[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", color=ink, fontsize=10, fontweight="bold")
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=ink, pad=28)
    pf = s["profit_factor"]
    ax.text(0, 1.03, (f"Net {s['total_net_profit']:+,.0f} USD   ·   {s['total_trades']:,} trades   ·   "
                      f"win rate {s['win_rate_pct']}%   ·   profit factor {pf}   ·   "
                      f"max equity drawdown {s['equity_drawdown_max']:,.0f} USD ({s['equity_drawdown_max_pct']}%)"),
            transform=ax.transAxes, color=ink2, fontsize=10)

    ax2 = fig.add_subplot(gs[1], sharex=ax)
    style(ax2)
    ax2.fill_between(x, -dd, 0, color=red, alpha=0.12, linewidth=0)
    ax2.plot(x, -dd, color=red, linewidth=1.0)
    ax2.yaxis.set_major_formatter(money)
    ax2.set_title("Drawdown from peak equity (USD)", loc="left", fontsize=11, color=ink2)
    for a in (ax, ax2):
        a.xaxis.set_major_locator(mdates.YearLocator())
        a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax3 = fig.add_subplot(gs[2])
    style(ax3)
    years = list(s["yearly"].keys())
    vals = [s["yearly"][y]["net_profit"] for y in years]
    cols = [blue if v >= 0 else red for v in vals]
    ax3.bar([str(y) for y in years], vals, color=cols, width=0.35)
    ax3.axhline(0, color=base, linewidth=1)
    ax3.yaxis.set_major_formatter(money)
    for i, v in enumerate(vals):
        ax3.annotate(f"{v:+,.0f}", (i, v), xytext=(0, 4 if v >= 0 else -4), textcoords="offset points",
                     ha="center", va="bottom" if v >= 0 else "top", color=ink2, fontsize=9)
    ax3.set_title("Net profit by year (USD, by close date; partial years at the edges)",
                  loc="left", fontsize=11, color=ink2)
    pad = max(abs(v) for v in vals) * 0.25 if vals else 1
    ax3.set_ylim(min(0, min(vals, default=0)) - pad, max(0, max(vals, default=0)) + pad)
    ax3.set_xlim(-0.75, max(len(years), 3) - 0.25)

    fig.text(0.125, 0.015, ("Real Dukascopy XAUUSD ticks, every tick replayed. Bars from Bid. Real spread; "
                            "no commission or swap. $10,000 deposit, 1:100 leverage, 100 oz/lot."),
             color=muted, fontsize=8.5)
    fig.savefig(path, dpi=140, facecolor=surface, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--warmup", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = ap.parse_args()

    p = dict(DEFAULTS)
    t, bid, ask = load_ticks(args.data_dir, "XAUUSD", args.warmup, args.end)
    start_ms, end_ms = to_ms(args.start), to_ms(args.end)
    n_ticks = int(((t >= start_ms) & (t < end_ms)).sum())
    print(f"loaded {len(t):,} ticks ({n_ticks:,} in the test window)", flush=True)
    res = run(t, bid, ask, start_ms, end_ms, p)
    df = trades_frame(res)
    s = summarize(df, res, p, n_ticks, args.start, args.end)

    os.makedirs(args.out, exist_ok=True)
    df.to_csv(os.path.join(args.out, "trades.csv"), index=False)
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(s, f, indent=2, default=str)
    plot(res, s, os.path.join(args.out, "equity_curve.png"),
         f"ThunderTrend_RetestEA · XAUUSD M5 · {args.start} to {args.end}")
    print(json.dumps({k: v for k, v in s.items() if k != "settings"}, indent=2, default=str))


if __name__ == "__main__":
    main()
