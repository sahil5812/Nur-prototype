# 📌 Nur Trading Agent

**MT5 EMA200 Algorithmic Trading Prototype**  
Python ↔ MetaTrader 5 (Official API)

---

## 🧠 Project Overview

Nur Trading Agent is a **working prototype** of an algorithmic trading agent that demonstrates clean, stable integration between **Python-based strategy logic** and **MetaTrader 5** using the **official MetaTrader5 Python API**.

The system enforces strict separation of concerns:

- **Python** handles strategy logic, decision-making, and state management  
- **MetaTrader 5 Terminal** is the sole source of market data and trade execution  
- No file-based bridges, CSV polling, or unofficial APIs  
- No Expert Advisor strategy logic inside MT5  

This keeps the system deterministic, debuggable, and crash-isolated.

---

## 🧱 Design Principles

- Strategy logic lives **only in Python**
- Execution is handled **only by MT5**
- No file-based IPC (no CSVs, no command files)
- No Expert Advisor strategy logic
- Python crash ≠ MT5 crash
- Deterministic, debuggable execution flow
- Fewer moving parts → higher reliability

---

## 🏗️ System Architecture

```text
MetaTrader 5 Terminal
        ↓
Official MetaTrader5 Python API
        ↓
Nur Trading Agent (Python)
        ↓
Strategy Logic + State Machine
        ↓
Trade Execution (Demo)

```

-Key Architectural Rules

-Strategy logic never runs inside MT5

-MT5 is the single source of market truth

-Explicit agent state and reasoning at all times

-Python and MT5 failures are isolated

-Deterministic and debuggable execution flow

---

📈 Trading Strategy
Indicators

-EMA 200

-ATR (Average True Range)

-Timeframe

-M1 (1-minute candles)

-Candle-close logic only (no repainting)

## Entry Logic
```
BUY when price closes above EMA200

SELL when price closes below EMA200

One signal per crossover (no overtrading)
```
## Continuation Logic

```
-Trades are allowed only when:

-Trend is clearly established

-A pullback occurs toward EMA200

-Price resumes in the trend direction

-Risk & Safety Controls (Prototype Level)

-One trade at a time

-Explicit agent states:

WAITING → IN_TRADE → COOLDOWN

Cooldown after trade close

ATR-based volatility filter

EMA proximity filter

ATR-based trailing stop-loss

Duplicate trade prevention
```

## ⚙️ Technology Stack
---

- MetaTrader 5 Terminal

- Official MetaTrader5 Python API

- Python 3.11+

- Demo account only (safe testing)

- No third-party or unofficial MT5 libraries are used.

---

## 🚀 Features Implemented

✅ Direct live market data from MT5

✅ Real-time EMA200 calculation in Python

✅ ATR-based volatility filtering

✅ Trend continuation logic

✅ ATR-based trailing stop-loss

✅ Disciplined state-based trading agent

✅ BUY / SELL signal generation

✅ Demo-safe trade execution

✅ Silent behavior when no valid signals

✅ Debug-friendly logging

✅ GitHub-safe (no credentials or secrets)

✅ CSV / EA bridge fully removed

---
## 🚧 Intentional Limitations

- This repository is a prototype, not a production trading system.

- Not included (by design):

- Risk-based position sizing

- Portfolio / multi-symbol trading

- News filtering

- Session filtering

- Machine learning

- High-frequency execution

These are planned for future phases.

---

## 🧪 Usage (Demo / Test Environment)
- Prerequisites

 MetaTrader 5 (running)

- Logged into a demo account

- Python 3.11+

- Install dependency:

```
 pip install MetaTrader5
```
- Run the Agent
```
python main.py
```
---

## Runtime Behavior

- The agent will:

- Connect to MT5

- Listen to live market data

- Compute EMA200 in real time

- Wait patiently for valid conditions

- Execute demo trades when criteria are met

---

---

## 🔐 Security Note

- No API keys or secrets stored

- Uses only the official MT5 Python API

- Fully compliant with GitHub Push Protection

- Safe for public and academic repositories

🎓 Academic / Learning Use

- Suitable for:

- Algorithmic trading demonstrations

- MT5 + Python integration learning

- Trading system architecture studies

- College / academic submissions

- Agent-based system design examples

---

## 🟢 Project Status

✔ Live MT5 API integration complete

✔ Strategy validated with real market data

✔ Disciplined agent behavior confirmed

✔ Demo trade execution verified

✔ File-based IPC and EA logic removed

✔ Ready for GUI and higher-level agent features

---

📌 One-Line Summary

A disciplined EMA200 trading agent using Python and the official MetaTrader 5 API for real-time market interaction and demo trade execution.
This is now **README-grade**, reviewer-proof, and won’t make maintainers roll their eyes.
