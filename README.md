
### Design Principles

- Strategy logic lives **only in Python**
- Execution is handled **only by MT5**
- No file-based IPC
- No Expert Advisor strategy logic
- Python crash ≠ MT5 crash
- Deterministic, debuggable execution flow

---

## 📈 Trading Strategy

### Indicators
- **EMA 200**
- **ATR (Average True Range)**

### Timeframe
- **M1 (1-minute, candle-close logic)**

### Entry Logic
- **BUY** when price closes above EMA200  
- **SELL** when price closes below EMA200  

### Continuation Logic
- Trade only after:
  - Trend is established
  - Pullback occurs toward EMA200
  - Price resumes in trend direction

### Risk & Safety Controls
- One trade at a time
- Cooldown after trade close
- ATR-based volatility filtering
- EMA proximity filter
- ATR-based trailing stop-loss

---

## ⚙️ Technology Stack

- **MetaTrader 5**
- **Official MetaTrader5 Python API**
- **Python 3.11**
- Demo account (safe testing)

No third-party or unofficial MT5 libraries are used.

---

## 🚀 Features Implemented

✅ Direct MT5 connection via official Python API  
✅ Real-time candle-close processing  
✅ EMA200 calculation  
✅ ATR-based volatility filter  
✅ Trend continuation logic  
✅ ATR-based trailing stop-loss  
✅ State machine (`WAITING → IN_TRADE → COOLDOWN`)  
✅ Debug-friendly logging  
✅ GitHub security-compliant (no secrets)

---

## 🚧 Intentional Limitations

This repository is a **prototype**, not a production trading system.

Not included (by design):

- Risk-based position sizing
- Portfolio / multi-symbol trading
- News filtering
- Session filtering
- Machine learning
- High-frequency execution

These are planned for future iterations.

---

## 🧪 Usage (Demo / Test Environment)

### Prerequisites
- MetaTrader 5 (running, demo account)
- Python **3.11**
- `pip install MetaTrader5`

### Run the bot
```bash
python main.py
