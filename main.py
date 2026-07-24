"""
main.py
-------
Two modes:
  python main.py            -> just scans your watchlist and prints signals
  python main.py --trade    -> also places a paper options trade on any
                                bullish signal it finds

This is a starting point, not a proven strategy. Read it, tweak it, and
test it in paper mode for a long time before ever thinking about real money.
"""

import sys
from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetOptionContractsRequest,
    MarketOrderRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, ContractType

import config


def get_price_history(data_client, symbol, days=100):
    """Pulls daily price bars for one ticker and returns them as a DataFrame."""
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=days),
    )
    bars = data_client.get_stock_bars(request).df
    return bars


def check_signal(bars):
    """
    Very simple moving-average crossover:
    bullish if the short-term average is above the long-term average.
    Returns True/False.
    """
    closes = bars["close"]
    short_ma = closes.rolling(config.SHORT_WINDOW).mean().iloc[-1]
    long_ma = closes.rolling(config.LONG_WINDOW).mean().iloc[-1]
    return short_ma > long_ma


def find_atm_call(trading_client, symbol):
    """
    Looks up a near-the-money call option expiring roughly
    TARGET_DAYS_TO_EXPIRATION days out for the given stock.
    Returns the option contract symbol, or None if nothing found.
    """
    target_date = datetime.now() + timedelta(days=config.TARGET_DAYS_TO_EXPIRATION)

    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date=target_date.date(),
        type=ContractType.CALL,
        limit=5,
    )
    contracts = trading_client.get_option_contracts(request).option_contracts

    if not contracts:
        print(f"  No option contracts found for {symbol} near {target_date.date()}")
        return None

    # Just take the first one returned for now — a real strategy would
    # pick the strike closest to the current stock price.
    return contracts[0].symbol


def place_paper_trade(trading_client, option_symbol):
    """Submits a market order to buy one (or more) call contracts."""
    order_request = MarketOrderRequest(
        symbol=option_symbol,
        qty=config.CONTRACTS_PER_TRADE,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )
    try:
        order = trading_client.submit_order(order_request)
        print(f"  Paper order submitted: {order.id} for {option_symbol}")
    except Exception as e:
        if "market hours" in str(e).lower():
            print("  Market is closed right now (options orders only go through "
                  "9:30am-4pm ET, Mon-Fri). Try again during trading hours.")
        else:
            print(f"  Order failed: {e}")


def main():
    do_trade = "--trade" in sys.argv

    if not config.ALPACA_API_KEY or not config.ALPACA_SECRET_KEY:
        print("Missing ALPACA_API_KEY / ALPACA_SECRET_KEY.")
        print("Copy .env.example to .env and fill in your paper-trading keys.")
        return

    data_client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)
    trading_client = TradingClient(
        config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, paper=config.ALPACA_PAPER
    )

    account = trading_client.get_account()
    print(f"Connected to Alpaca ({'paper' if config.ALPACA_PAPER else 'LIVE'} account).")
    print(f"Account buying power: ${account.buying_power}\n")

    for symbol in config.WATCHLIST:
        print(f"Scanning {symbol}...")
        bars = get_price_history(data_client, symbol)

        if bars.empty or len(bars) < config.LONG_WINDOW:
            print("  Not enough price history yet, skipping.")
            continue

        bullish = check_signal(bars)
        print(f"  Signal: {'BULLISH' if bullish else 'no signal'}")

        if bullish and do_trade:
            option_symbol = find_atm_call(trading_client, symbol)
            if option_symbol:
                place_paper_trade(trading_client, option_symbol)

    print("\nDone.")


if __name__ == "__main__":
    main()
