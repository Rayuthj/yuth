"""Download real XAUUSD tick data from Dukascopy and pack it into monthly .npz files.

Dukascopy serves one LZMA-compressed .bi5 file per UTC hour. Each record is 20 bytes,
big-endian: ms-offset-in-hour (u32), ask (u32), bid (u32), ask volume (f32), bid volume (f32).
XAUUSD prices are stored in points of 0.001.

Usage:
    python download_dukascopy.py --data-dir ../data --start 2021-09-01 --end 2026-10-01
"""
import argparse
import datetime as dt
import lzma
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import requests

URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m:02d}/{d:02d}/{h:02d}h_ticks.bi5"
RECORD = np.dtype([("t", ">u4"), ("ask", ">u4"), ("bid", ">u4"), ("av", ">f4"), ("bv", ">f4")])


def hours(start, end):
    """Every UTC hour in [start, end), skipping Saturdays (gold is closed all day)."""
    h = dt.datetime.combine(start, dt.time(), tzinfo=dt.timezone.utc)
    stop = dt.datetime.combine(end, dt.time(), tzinfo=dt.timezone.utc)
    while h < stop:
        if h.weekday() != 5:
            yield h
        h += dt.timedelta(hours=1)


def raw_path(data_dir, sym, h):
    return os.path.join(data_dir, "raw", sym, f"{h:%Y}", f"{h:%m}", f"{h:%d}", f"{h:%H}h_ticks.bi5")


def fetch(session, data_dir, sym, h):
    path = raw_path(data_dir, sym, h)
    if os.path.exists(path):
        return 0
    url = URL.format(sym=sym, y=h.year, m=h.month - 1, d=h.day, h=h.hour)  # month is 0-based
    delay = 2.0
    for attempt in range(8):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 404:
                body = b""
            elif r.status_code == 200:
                body = r.content
            else:
                raise RuntimeError(f"HTTP {r.status_code}")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".part"
            with open(tmp, "wb") as f:
                f.write(body)
            os.replace(tmp, path)
            return len(body)
        except Exception as e:  # network hiccup or throttling: back off and retry
            if attempt == 7:
                raise RuntimeError(f"{url}: {e}")
            time.sleep(delay)
            delay = min(delay * 2, 60)


def decode(path, hour_start_ms):
    with open(path, "rb") as f:
        body = f.read()
    if not body:
        return None
    rec = np.frombuffer(lzma.decompress(body), dtype=RECORD)
    t = hour_start_ms + rec["t"].astype(np.int64)
    return t, rec["bid"].astype(np.int32), rec["ask"].astype(np.int32)


def pack_months(data_dir, sym, start, end):
    """Combine the hourly files of each month into data/npz/{sym}_{YYYY}_{MM}.npz."""
    out_dir = os.path.join(data_dir, "npz")
    os.makedirs(out_dir, exist_ok=True)
    by_month = {}
    for h in hours(start, end):
        by_month.setdefault((h.year, h.month), []).append(h)
    for (y, m), hs in sorted(by_month.items()):
        out = os.path.join(out_dir, f"{sym}_{y:04d}_{m:02d}.npz")
        if os.path.exists(out):
            continue
        ts, bids, asks = [], [], []
        for h in hs:
            got = decode(raw_path(data_dir, sym, h), int(h.timestamp()) * 1000)
            if got is not None:
                ts.append(got[0]); bids.append(got[1]); asks.append(got[2])
        t = np.concatenate(ts) if ts else np.zeros(0, np.int64)
        bid = np.concatenate(bids) if bids else np.zeros(0, np.int32)
        ask = np.concatenate(asks) if asks else np.zeros(0, np.int32)
        np.savez(out, t=t, bid=bid, ask=ask)
        print(f"packed {y}-{m:02d}: {len(t):,} ticks", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args()

    todo = list(hours(args.start, args.end))
    print(f"{len(todo):,} hourly files to check", flush=True)
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=args.workers))
    done = total_bytes = 0
    t0 = time.time()
    with ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(fetch, session, args.data_dir, args.symbol, h) for h in todo]
        for fut in as_completed(futs):
            total_bytes += fut.result()
            done += 1
            if done % 2000 == 0 or done == len(todo):
                print(f"{done:,}/{len(todo):,} files, {total_bytes/1e6:,.0f} MB new, "
                      f"{time.time()-t0:,.0f}s", flush=True)
    pack_months(args.data_dir, args.symbol, args.start, args.end)


if __name__ == "__main__":
    sys.exit(main())
