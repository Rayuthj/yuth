# TradingView Trendline Tools

Two Pine Script v6 scripts for TradingView:

| File | Type | What it does |
|---|---|---|
| [`tradingview/auto_trendlines.pine`](tradingview/auto_trendlines.pine) | Indicator | Draws trendlines automatically on 3 pivot levels (minor, intermediate, major) and marks breaks with arrows and alerts. |
| [`tradingview/trendline_breakout_strategy.pine`](tradingview/trendline_breakout_strategy.pine) | Strategy | Trades trendline breakouts with an ATR stop and a 3R target. Backtest it in the Strategy Tester. |

## Install (about 1 minute)

1. Open any chart on TradingView and click **Pine Editor** at the bottom.
2. Delete what is in the editor, paste the full contents of one `.pine` file, and click **Save**.
3. Click **Add to chart**. For the strategy, open the **Strategy Tester** tab to see the results.
4. Optional alerts (indicator): **Alerts → Create alert → Condition: Auto Trendlines**, then choose e.g. *Bullish trendline break*.

## Auto Trendlines indicator

How lines are built:

1. Pivot highs and lows are found on 3 levels: minor (pivot length 5, thin), intermediate (10, medium), and major (20, thick).
2. Each new pivot is connected to up to 3 earlier pivots of the same kind (highs to highs, lows to lows).
3. A line is kept only if no candle **closed** through it between its first anchor and now.
4. Valid lines extend to the right until price closes through them. A break is marked with an arrow (bigger arrow = bigger level), and the broken line turns dashed.

Line colors: red is resistance (through highs) and green is support (through lows).
Solid lines are classic trendlines: falling resistance and rising support.
Dotted lines are channel lines (rising resistance, falling support), shown when **Line types = All slopes**.

Settings to adjust:

- **Lines per new pivot / Pivots remembered**: raise these for more lines, lower them for a cleaner chart.
- **Line types**: switch to *Classic only* to see only textbook trendlines.
- **Min touches**: 3 keeps only lines with at least one more pivot on them (stronger, fewer lines).
- **Line must not be crossed by**: *Wick* is stricter than *Close*.
- **Break buffer (x ATR)**: require a close this far past the line to count a break (filters small fake-outs).
- Turn off levels you don't need (e.g. Minor on low timeframes).

## Trendline Breakout strategy

Default rules:

| | |
|---|---|
| Lines | Pivot length 10, classic lines only (falling resistance / rising support), at least 2 touches |
| Long | Candle closes above a falling resistance trendline |
| Short | Candle closes below a rising support trendline |
| Entry | Next candle's open, one trade at a time |
| Stop loss | 2 × ATR(14) from the signal close |
| Take profit | 3R (3 × the stop distance = 6 × ATR) |
| Size | Risk 1% of equity per trade, capped at 100% of equity in position value |
| Costs | 0.05% commission per side + 1 tick slippage (change these in *Properties* for your broker) |

Options: long/short only, EMA trend filter, ATR trailing stop instead of a fixed target, risk %, max position size.

**Stocks preset:** *Direction = Long only* plus *Trend filter: only trade with the EMA* on (EMA 200).
In the research this had fewer trades but a higher average profit per trade (see below).

## How the strategy was chosen

`research/trendline_backtest.py` re-implements the same trendline engine in Python. It tested 384 strategy variants (data shown below).
The variants covered:

- breakout vs bounce entries
- pivot length 5, 10, or 20
- classic vs all line types
- 2 or 3 minimum touches
- with or without the EMA 200 trend filter
- long-only vs both directions
- 4 exit methods

| Dataset | Timeframe | Years |
|---|---|---|
| GOOG, NVDA, ORCL, YHOO (split-adjusted) | Daily | 1995–2014 |
| EUR/USD | 1 hour | 2017–2018 |
| Stock index | 5 min | Jan 2006 |

Results are in **R** (1R = the amount risked per trade; +0.2R per trade at 1% risk ≈ +0.2% per trade).
Each dataset was split: first 60% to choose settings (in-sample), last 40% only to check them (out-of-sample).

**Why compare with random entries:** on stocks that rose a lot, almost any long entry with these exits makes money.
Every variant was compared against random entries made at the same rate, with the same filters and exits.
"Edge" is how much better the trendline signals did than random entries.

**How the default was picked:** variants with fewer than 100 in-sample trades were dropped, and the rest were ranked by in-sample edge.
From the top group (in-sample edge +0.3R or more), the default is the one with the most trades that also trades both directions.
It is close to the best in-sample (+0.32R vs +0.41R for the top variant) on twice the trades. Its out-of-sample results were the most consistent of that group.

Default strategy (pivot 10, classic, breakout, both directions, 2 ATR stop, 3R target):

| | Trades | Avg per trade | Edge vs random | Datasets profitable | Datasets beating random |
|---|---|---|---|---|---|
| In-sample | 229 | +0.31R | +0.32R | 5 / 6 | 5 / 6 |
| Out-of-sample | 171 | **+0.16R** | +0.31R | **6 / 6** | **6 / 6** |

Stocks preset (same, long only + EMA 200 filter):

| | Trades | Avg per trade | Edge vs random | Datasets profitable | Datasets beating random |
|---|---|---|---|---|---|
| In-sample | 104 | +0.76R | +0.33R | 6 / 6 | 5 / 6 |
| Out-of-sample | 83 | **+0.37R** | +0.35R | **6 / 6** | **6 / 6** |

What the tests showed:

- **Trade breakouts, not bounces.** With the same settings, bounce entries lost money (−0.24R per trade out-of-sample) while breakouts made +0.16R.
- **Bigger pivots work better.** Pivot length 10–20 beat 5. Short pivots make many weak lines.
- **A 2 ATR stop with a 3R target was the best exit overall.** The ATR trailing stop was close behind on trending stocks.
- The win rate is low (about 30–40%). The strategy makes money because winners are 3× the size of losers, so expect losing streaks.
- The worst out-of-sample losing stretch (largest drop from a peak) was about 4.5–11R per dataset, which is about 4.5–11% at 1% risk.

### Limits — read before trading real money

- The edge is **modest** (+0.16R per trade out-of-sample on default settings). Costs, slippage, and the market you pick matter a lot.
- The data covers only 4 stocks, 1 currency pair, and 1 index. Crypto and gold were not tested (no data was available).
  The stocks were chosen with hindsight; they all survived and grew.
- The Python engine follows the Pine logic, but TradingView's Strategy Tester fills orders differently in small ways. Trust TradingView's numbers on **your** symbol and timeframe.
- Before going live: run the Strategy Tester on your market, look at at least 100 trades, then paper trade.
- This is research, not financial advice.

## Re-running the research

```bash
pip install numpy pandas
python3 research/trendline_backtest.py --out results.csv
```

This downloads the datasets into `research/data/` and prints the top variants, ranked on in-sample data only.
