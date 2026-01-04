"""
EMA200 Trading Engine (Candle Close, Disciplined)

CSV-based MT5 bridge engine using EMA200 crossover.
One trade per cross, cooldown protected.
"""

import time
import os
from datetime import datetime
from collections import deque
from typing import Tuple, Optional, List

# ================= PATHS =================
MARKET_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\market.csv"
COMMANDS_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\commands.csv"

# ================= CONFIG =================
SYMBOL = "XAUUSD"

EMA_PERIOD = 200
ALPHA = 2 / (EMA_PERIOD + 1)

COOLDOWN_SECONDS = 60
SLEEP_TIME = 0.5
# ========================================

# ================= STATE =================
STATE_WAITING = "WAITING"
STATE_COOLDOWN = "COOLDOWN"

state = STATE_WAITING
last_trade_time: Optional[float] = None

trend: Optional[str] = None  # "BULLISH" / "BEARISH"

ema: Optional[float] = None
current_minute: Optional[datetime] = None
minute_prices: List[float] = []

prev_close: Optional[float] = None
prev_ema: Optional[float] = None
prev_high: Optional[float] = None
prev_low: Optional[float] = None

last_seen: str = ""

recent_highs: deque = deque(maxlen=5)
recent_lows: deque = deque(maxlen=5)
# ========================================


def can_trade_again() -> bool:
    if last_trade_time is None:
        return True
    return (time.time() - last_trade_time) >= COOLDOWN_SECONDS


def parse_line(line: str) -> Tuple[datetime, float]:
    parts = line.split()
    ts = datetime.strptime(parts[0] + " " + parts[1], "%Y.%m.%d %H:%M:%S")
    bid = float(parts[-2])
    ask = float(parts[-1])
    return ts, (bid + ask) / 2


def write_command(action: str, sl: float, tp: float) -> None:
    with open(COMMANDS_FILE, "w") as f:
        f.write(f"{action},{SYMBOL},{sl:.2f},{tp:.2f}")
    print(f"📤 COMMAND SENT → {action} | SL={sl:.2f} TP={tp:.2f}")


print("🔴 EMA200 ENGINE STARTED (CANDLE CLOSE)")
print("Waiting for market data...\n")

while True:
    try:
        if not os.path.exists(MARKET_FILE):
            time.sleep(SLEEP_TIME)
            continue

        with open(MARKET_FILE, "r", encoding="utf-16") as f:
            data = f.read().strip()

        if not data or data == last_seen:
            time.sleep(SLEEP_TIME)
            continue

        last_seen = data
        ts, price = parse_line(data)
        minute = ts.replace(second=0)

        # ================= NEW CANDLE =================
        if current_minute and minute != current_minute:
            close_price = minute_prices[-1]
            high_price = max(minute_prices)
            low_price = min(minute_prices)

            # EMA UPDATE
            if ema is None:
                ema = close_price
            else:
                ema = ALPHA * close_price + (1 - ALPHA) * ema

            print(
                f"[{current_minute.strftime('%H:%M')}] "
                f"CLOSE={close_price:.2f} EMA200={ema:.2f} "
                f"STATE={state} TREND={trend}"
            )

            recent_highs.append(high_price)
            recent_lows.append(low_price)

            # ================= ENTRY LOGIC =================
            if (
                state == STATE_WAITING
                and can_trade_again()
                and prev_close is not None
                and prev_ema is not None
            ):
                # BUY CROSS
                if close_price > ema and prev_close <= prev_ema and trend != "BULLISH":
                    sl = prev_low
                    tp = max(recent_highs)
                    print("✅ BUY → EMA200 CROSS (CONFIRMED)")
                    write_command("BUY", sl, tp)

                    trend = "BULLISH"
                    state = STATE_COOLDOWN
                    last_trade_time = time.time()

                # SELL CROSS
                elif close_price < ema and prev_close >= prev_ema and trend != "BEARISH":
                    sl = prev_high
                    tp = min(recent_lows)
                    print("❌ SELL → EMA200 CROSS (CONFIRMED)")
                    write_command("SELL", sl, tp)

                    trend = "BEARISH"
                    state = STATE_COOLDOWN
                    last_trade_time = time.time()

            # Store previous candle
            prev_close = close_price
            prev_ema = ema
            prev_high = high_price
            prev_low = low_price

            minute_prices.clear()

        # ================= COOLDOWN =================
        if state == STATE_COOLDOWN and can_trade_again():
            print("🔄 COOLDOWN DONE → WAITING")
            state = STATE_WAITING

        current_minute = minute
        minute_prices.append(price)

        time.sleep(SLEEP_TIME)

    except KeyboardInterrupt:
        print("\nStopped")
        break
