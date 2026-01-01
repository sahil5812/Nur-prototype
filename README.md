📌 Nur Trading Agent
MT5 EMA200 Algorithmic Trading Prototype (Python ↔ MetaTrader 5 API) 🧠
🧠 Project Overview

Nur Trading Agent is a working prototype of an algorithmic trading agent designed to demonstrate how Python-based strategy logic can interact with MetaTrader 5 (MT5) in a clean, stable, and professional way using the official MetaTrader 5 Python API.

The project follows a clear separation of concerns, where:

Python handles all decision-making, strategy logic, and state management

MetaTrader 5 Terminal acts as the market data source and trade execution engine

No file-based bridges, unsafe APIs, or unofficial hacks are used.

🎯 Core Objective

Implement a real-time EMA200 crossover strategy

Consume live market data directly from MT5

Execute demo trades safely

Maintain discipline, state awareness, and silence when no conditions are met

Provide a strong, extensible foundation for future agent behavior and GUI

🏗️ System Architecture (Updated)
MetaTrader 5 Terminal
        ↓
Official MetaTrader5 Python API
        ↓
Nur Trading Agent (Python)
        ↓
Strategy Logic + State Machine
        ↓
Trade Execution (Demo)

Key Architectural Principles

Strategy logic never runs inside MT5

Python does not use file-based IPC (no CSV, no command files)

MT5 remains the single source of market truth

Fewer moving parts → higher reliability

Clear agent state and reasoning

📈 Trading Strategy
Indicator

EMA 200

Timeframe

M1 (1-minute)

Logic

BUY when price crosses above EMA200

SELL when price crosses below EMA200

One signal per crossover (no overtrading)

Risk Controls (Prototype Level)

Fixed SL / TP (demo values)

Duplicate trade prevention

Explicit agent states (WAITING, IN_TRADE)

⚙️ Technology Stack

MetaTrader 5 Terminal

Python 3.11+

MetaTrader5 Official Python API

No Expert Advisors required for strategy

No CSV or file-based communication

🚀 Features Implemented

✅ Direct live market data from MT5
✅ Real-time EMA200 calculation in Python
✅ Disciplined state-based trading agent
✅ BUY / SELL signal generation
✅ Demo-safe trade execution
✅ Silent behavior when no valid signals
✅ GitHub-safe (no credentials or secrets)

🚧 Intentional Limitations

This repository is a prototype, not a production trading system.

Not included (by design):

Position sizing

Advanced money management

Multi-symbol trading

News filtering

High-frequency execution

Machine learning / optimization

These can be added in future phases.

🧪 Usage (Demo / Test Environment)

Open MetaTrader 5

Log in to a demo account

Keep MT5 running

Run the Python agent:

py -3.11 main.py


The agent will:

Connect to MT5

Listen to live market ticks

Compute EMA200

Wait patiently for valid crossovers

Execute demo trades when conditions are met

🔐 Security Note

No API keys or secrets are stored

Uses only the official MT5 Python API

Fully compliant with GitHub Push Protection rules

Safe for academic and public repositories

🎓 Academic / Learning Use

This project is suitable for:

Algorithmic trading demonstrations

MT5 + Python integration learning

Trading system architecture studies

College / academic submissions

Agent-based system design examples

🟢 Project Status

✔ Live MT5 API integration complete
✔ Strategy validated with real market data
✔ Disciplined agent behavior confirmed
✔ Demo trade execution verified
✔ CSV / EA bridge fully removed
✔ Ready for GUI and higher-level agent features

📌 One-Line Summary

A disciplined EMA200 trading agent using Python and the official MetaTrader 5 API for real-time market interaction and demo trade execution.
