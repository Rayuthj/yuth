# ThunderTrend_RetestEA backtest on real XAUUSD ticks

`ea_engine.py` replays every real tick through a line-by-line Python port of
`../ea/ThunderTrend_RetestEA.mq5` with an MT5-style order model.
`reference_check.py` is an independent slow port used to verify the fast engine
trade-for-trade.

```bash
pip install numpy pandas numba matplotlib requests
python download_dukascopy.py --data-dir ../data --start 2021-09-01 --end 2026-10-01
python reference_check.py --data-dir ../data --warmup 2022-02-01 --start 2022-03-01 --end 2022-04-01
python run_backtest.py --data-dir ../data --out ../results --warmup 2021-09-01 --start 2021-10-01 --end 2026-10-01 --spread-points 26
```

Assumptions (edit `DEFAULTS` in `run_backtest.py`):
- Data: Dukascopy XAUUSD bid/ask ticks (UTC). M5 bars are built from Bid, like MT5.
- Contract: 100 oz per lot, lot step 0.01, min 0.01, max 100.
- Account: $10,000 deposit, 1:100 leverage, 50% stop-out (MT5 tester defaults).
- Costs: the real tick spread, or a fixed spread with `--spread-points` (26 points = $0.26
  on a 2-digit gold quote). No commission, no swap, no extra slippage.
- Fills: market orders at the current Bid/Ask, TP at the TP price, SL at the first
  tick through it (gaps fill worse). Orders with SL on the wrong side of the market,
  or without enough free margin, are rejected; the EA still clears its setup, as in MT5.
- The first month (`--warmup`) is only used to warm up the EMA(200) and LWMA(21).
