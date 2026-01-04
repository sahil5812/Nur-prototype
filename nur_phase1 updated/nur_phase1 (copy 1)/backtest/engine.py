import time
import MetaTrader5 as mt5
from datetime import datetime

# ================= CONFIG =================
SYMBOL = "XAUUSD"
EMA_PERIOD = 200
TIMEFRAME_SLEEP = 0.1
COOLDOWN_SECONDS = 60

VOLUME = 0.01
DEVIATION = 20
# ==========================================

# ================= STATE ==================
STATE_WAITING = "WAITING"
STATE_IN_TRADE = "IN_TRADE"
STATE_COOLDOWN = "COOLDOWN"

state = STATE_WAITING
last_price = None
last_trade_time = None
prices = []

# critical flag: confirms at least one tick after entry
post_entry_tick_seen = False
# ==========================================


# ================= MT5 INIT ===============
def mt5_init():
    if not mt5.initialize():
        raise RuntimeError("❌ MT5 initialization failed")

    print(f"✅ MetaTrader5 loaded | version={mt5.__version__}")
    print("📡 Connected to MT5 terminal")


# ================= HELPERS =================
def get_price():
    tick = mt5.symbol_info_tick(SYMBOL)
    return tick.bid if tick else None


def calculate_ema(values, period):
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = v * k + ema * (1 - k)
    return ema


def position_exists():
    # NETTING-SAFE: only one position per symbol
    positions = mt5.positions_get(symbol=SYMBOL)
    return bool(positions)


def can_trade_again():
    if last_trade_time is None:
        return True
    return (time.time() - last_trade_time) >= COOLDOWN_SECONDS


# ================= ORDER EXECUTION =================
def send_order(order_type):
    tick = mt5.symbol_info_tick(SYMBOL)
    if not tick:
        return False

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
        print(f"❌ ORDER FAILED → retcode={result.retcode}")
        return False

    print("📤 ORDER EXECUTED")
    return True


# ================= MAIN ENGINE =================
def main():
    global state, last_price, last_trade_time, post_entry_tick_seen

    mt5_init()
    print("\n🔴 LIVE MODE — EMA200 + DEMO TRADING ENABLED")
    print("=" * 60)
    print("📡 Listening to MT5 live ticks...\n")

    while True:
        price = get_price()
        if price is None:
            time.sleep(TIMEFRAME_SLEEP)
            continue

        # tick de-duplication
        if price == last_price:
            time.sleep(TIMEFRAME_SLEEP)
            continue

        last_price = price
        prices.append(price)

        if len(prices) < EMA_PERIOD:
            continue

        ema = calculate_ema(prices[-EMA_PERIOD:], EMA_PERIOD)
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

        print(f"{now} | PRICE={price:.2f} | EMA200={ema:.2f} | STATE={state}")

        # ================= STATE MACHINE =================

        # 🟢 WAITING → ENTRY
        if state == STATE_WAITING:

            if not can_trade_again():
                time.sleep(TIMEFRAME_SLEEP)
                continue

            prev_price = prices[-2]

            if prev_price <= ema and price > ema:
                print("✅ BUY SIGNAL → EMA200 bullish cross")
                if send_order(mt5.ORDER_TYPE_BUY):
                    state = STATE_IN_TRADE
                    post_entry_tick_seen = False
                    print("🔒 STATE LOCKED → IN_TRADE")

            elif prev_price >= ema and price < ema:
                print("❌ SELL SIGNAL → EMA200 bearish cross")
                if send_order(mt5.ORDER_TYPE_SELL):
                    state = STATE_IN_TRADE
                    post_entry_tick_seen = False
                    print("🔒 STATE LOCKED → IN_TRADE")

        # 🔵 IN_TRADE → EXIT
        elif state == STATE_IN_TRADE:

            # wait for one tick after entry
            if not post_entry_tick_seen:
                post_entry_tick_seen = True
                time.sleep(TIMEFRAME_SLEEP)
                continue

            # reliable exit check
            if not position_exists():
                print("🟢 TRADE CLOSED → entering cooldown")
                state = STATE_COOLDOWN
                last_trade_time = time.time()

        # 🟡 COOLDOWN → WAITING
        elif state == STATE_COOLDOWN:

            if can_trade_again():
                print("🔄 Cooldown finished → WAITING")
                state = STATE_WAITING

        time.sleep(TIMEFRAME_SLEEP)
