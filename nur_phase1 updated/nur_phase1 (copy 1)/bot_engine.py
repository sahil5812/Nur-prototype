import time
import MetaTrader5 as mt5
from datetime import datetime

# ================= CONFIG =================
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M1

EMA_PERIOD = 200
ATR_PERIOD = 14

SLEEP_TIME = 0.2
COOLDOWN_SECONDS = 30

VOLUME = 0.01
DEVIATION = 20

EMA_MIN_BUFFER = 0.15          # how close price must come to EMA for pullback
ATR_MULTIPLIER = 0.5           # volatility filter
TRAIL_ATR_MULTIPLIER = 1.2     # trailing SL strength

DEBUG_MODE = True
# =========================================


# ================= STATES =================
STATE_WAITING = "WAITING"
STATE_IN_TRADE = "IN_TRADE"
STATE_COOLDOWN = "COOLDOWN"

TREND_NONE = "NONE"
TREND_BULLISH = "BULLISH"
TREND_BEARISH = "BEARISH"

state = STATE_WAITING
trend = TREND_NONE
pullback_seen = False

last_trade_time = None
last_candle_time = None
# =========================================


# ================= MT5 INIT ===============
if not mt5.initialize():
    raise RuntimeError("❌ MT5 init failed")

print(f"✅ MetaTrader5 loaded | version={mt5.__version__}")
print("📡 Connected to MT5 terminal")
print("\n🔴 LIVE MODE — EMA200 + ATR + CONTINUATION + TRAILING SL")
print("=" * 70)
# =========================================


# ================= HELPERS =================
def can_trade_again():
    if last_trade_time is None:
        return True
    return (time.time() - last_trade_time) >= COOLDOWN_SECONDS


def get_positions():
    return mt5.positions_get(symbol=SYMBOL)


def calculate_ema(values, period):
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = v * k + ema * (1 - k)
    return ema


def send_order(order_type):
    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": VOLUME,
        "type": order_type,
        "price": price,
        "deviation": DEVIATION,
        "comment": "EMA200 Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ ORDER FAILED → {result.retcode}")
        return False

    print("📤 ORDER EXECUTED")
    return True


def modify_sl(position, new_sl):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position.ticket,
        "sl": round(new_sl, 2),
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"🔁 TRAILING SL UPDATED → {new_sl:.2f}")


def trail_stop_loss(position, atr):
    tick = mt5.symbol_info_tick(SYMBOL)

    if position.type == mt5.ORDER_TYPE_BUY:
        price = tick.bid
        new_sl = price - atr * TRAIL_ATR_MULTIPLIER
        if position.sl == 0 or new_sl > position.sl:
            modify_sl(position, new_sl)

    elif position.type == mt5.ORDER_TYPE_SELL:
        price = tick.ask
        new_sl = price + atr * TRAIL_ATR_MULTIPLIER
        if position.sl == 0 or new_sl < position.sl:
            modify_sl(position, new_sl)
# =========================================


# ================= MAIN LOOP =================
while True:
    rates = mt5.copy_rates_from_pos(
        SYMBOL, TIMEFRAME, 0, EMA_PERIOD + ATR_PERIOD + 3
    )
    if rates is None or len(rates) < EMA_PERIOD + 3:
        time.sleep(SLEEP_TIME)
        continue

    last_closed = rates[-2]
    prev_closed = rates[-3]

    # candle-close only
    if last_candle_time == last_closed["time"]:
        time.sleep(SLEEP_TIME)
        continue
    last_candle_time = last_closed["time"]

    closes = [r["close"] for r in rates]
    ema = calculate_ema(closes[-EMA_PERIOD:], EMA_PERIOD)

    atr_values = [
        max(
            rates[i]["high"] - rates[i]["low"],
            abs(rates[i]["high"] - rates[i - 1]["close"]),
            abs(rates[i]["low"] - rates[i - 1]["close"]),
        )
        for i in range(-ATR_PERIOD, 0)
    ]
    atr = sum(atr_values) / ATR_PERIOD

    price = last_closed["close"]
    now = datetime.fromtimestamp(last_closed["time"]).strftime("%Y.%m.%d %H:%M")

    print(
        f"{now} | CLOSE={price:.2f} | EMA200={ema:.2f} | "
        f"STATE={state} | TREND={trend}"
    )

    # ================= WAITING =================
    if state == STATE_WAITING:

        if not can_trade_again():
            continue

        # ---- trend reset ----
        if trend == TREND_BULLISH and price < ema:
            trend = TREND_NONE
            pullback_seen = False
            if DEBUG_MODE:
                print("[DEBUG] Bullish trend broken")

        if trend == TREND_BEARISH and price > ema:
            trend = TREND_NONE
            pullback_seen = False
            if DEBUG_MODE:
                print("[DEBUG] Bearish trend broken")

        # ---- ATR filter ----
        if abs(price - ema) < atr * ATR_MULTIPLIER:
            if DEBUG_MODE:
                print("[DEBUG] ATR too low")
            continue

        # ================= EMA CROSS =================
        if prev_closed["close"] < ema and price > ema:
            print("✅ BUY CROSS → EMA200")
            if send_order(mt5.ORDER_TYPE_BUY):
                state = STATE_IN_TRADE
                trend = TREND_BULLISH
                pullback_seen = False

        elif prev_closed["close"] > ema and price < ema:
            print("❌ SELL CROSS → EMA200")
            if send_order(mt5.ORDER_TYPE_SELL):
                state = STATE_IN_TRADE
                trend = TREND_BEARISH
                pullback_seen = False

        # ================= CONTINUATION =================
        elif trend == TREND_BULLISH:

            if abs(price - ema) < EMA_MIN_BUFFER:
                pullback_seen = True
                if DEBUG_MODE:
                    print("[DEBUG] Bullish pullback detected")

            elif pullback_seen and price > ema and prev_closed["close"] < price:
                print("🟢 BUY CONTINUATION")
                if send_order(mt5.ORDER_TYPE_BUY):
                    state = STATE_IN_TRADE
                    pullback_seen = False

            else:
                if DEBUG_MODE:
                    print("[DEBUG] Bullish trend → no pullback yet")

        elif trend == TREND_BEARISH:

            if abs(price - ema) < EMA_MIN_BUFFER:
                pullback_seen = True
                if DEBUG_MODE:
                    print("[DEBUG] Bearish pullback detected")

            elif pullback_seen and price < ema and prev_closed["close"] > price:
                print("🔴 SELL CONTINUATION")
                if send_order(mt5.ORDER_TYPE_SELL):
                    state = STATE_IN_TRADE
                    pullback_seen = False

            else:
                if DEBUG_MODE:
                    print("[DEBUG] Bearish trend → no pullback yet")

    # ================= IN_TRADE =================
    elif state == STATE_IN_TRADE:
        positions = get_positions()

        if not positions:
            print("🟢 TRADE CLOSED → COOLDOWN")
            last_trade_time = time.time()
            state = STATE_COOLDOWN
        else:
            for pos in positions:
                trail_stop_loss(pos, atr)

    # ================= COOLDOWN =================
    elif state == STATE_COOLDOWN:
        if can_trade_again():
            print("🔄 COOLDOWN DONE → WAITING")
            state = STATE_WAITING

    time.sleep(SLEEP_TIME)
