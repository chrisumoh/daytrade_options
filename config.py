"""
config.py
---------
Central place for all settings. Nothing in here places trades by itself —
it just holds values that main.py reads.
"""

import os
from dotenv import load_dotenv

# Reads the .env file in this same folder and loads ALPACA_API_KEY, etc.
# into the environment so os.getenv() below can find them.
load_dotenv()

# --- Alpaca credentials (filled in from your .env file) ---
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

# IMPORTANT: keep this True. It points the bot at Alpaca's paper-trading
# environment, which uses fake money. Only change this after you fully
# understand and have tested the strategy.
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "True") == "True"

# --- Strategy settings ---
# Stocks the bot will look at. Add or remove tickers as you like.
WATCHLIST = ["SPY", "AAPL", "TSLA", "QQQ"]

# Moving-average windows used for the signal (in trading days).
SHORT_WINDOW = 20
LONG_WINDOW = 50

# How many days out to look for an option expiration when placing a trade.
# 7 means "roughly a week from today."
TARGET_DAYS_TO_EXPIRATION = 7

# Number of option contracts to buy per trade (1 contract = 100 shares).
CONTRACTS_PER_TRADE = 1
