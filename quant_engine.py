"""
quant_engine.py – Starter Quant Engine Skeleton
------------------------------------------------
A minimal, modular framework you can extend for equities, crypto, or any
asset class.  The goal is to stay readable while giving you clear seams for
plug‑and‑play components (data, strategy, portfolio/risk, execution).

Usage
-----
$ python quant_engine.py  # runs a 50/200 SMA cross on SPY 2015‑2025

Next steps are in the chat – iterate freely!
"""

from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import yfinance as yf

###############################################################################
# DATA LAYER
###############################################################################

class DataProvider(ABC):
    """Abstract base for data sources (CSV, exchange API, DB, etc.)."""

    @abstractmethod
    def fetch(self, symbol: str, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:  # noqa: D401,E501
        """Return a *price* DataFrame indexed by datetime with at least `Close`."""
        raise NotImplementedError


class YahooDataProvider(DataProvider):
    """Quick & dirty equities/ETF data via yfinance (suffices for prototyping)."""

    def fetch(self, symbol: str, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:  # noqa: D401,E501
        df = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)  # noqa: E501
        if df.empty:
            raise ValueError(f"No data for {symbol} – check ticker or dates")
        return df


###############################################################################
# STRATEGY LAYER
###############################################################################

class Strategy(ABC):
    """Any trading idea that turns prices into signals (+1, 0, ‑1)."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Return a Series of +1 (long), 0 (flat), ‑1 (short) *positions*."""
        raise NotImplementedError


class MovingAverageCrossStrategy(Strategy):
    """Classic 50/200 simple moving‑average cross‑over."""

    def __init__(self, short_window: int = 50, long_window: int = 200):
        if short_window >= long_window:
            raise ValueError("short_window must be < long_window")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:  # noqa: D401,E501
        short_ma = data["Close"].rolling(self.short_window).mean()
        long_ma = data["Close"].rolling(self.long_window).mean()
        # Position: 1 when short MA > long MA, else 0
        position = (short_ma > long_ma).astype(int)
        # Trades: diff of position → +1 entry, ‑1 exit
        trades = position.diff().fillna(0)
        return trades  # align on data.index


###############################################################################
# PORTFOLIO / EXECUTION LAYER
###############################################################################

class Portfolio:
    """Very naive equity‑only portfolio (all‑in / all‑out)."""

    def __init__(self, initial_cash: float = 100_000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0  # units held
        self.history: list[float] = []  # equity curve

    def update(self, price: float, trade_signal: int):
        # Buy full notional
        if trade_signal == 1 and self.position == 0:
            self.position = self.cash / price
            self.cash = 0.0
        # Sell all
        elif trade_signal == -1 and self.position > 0:
            self.cash = self.position * price
            self.position = 0.0
        # Mark‑to‑market
        self.history.append(self.value(price))

    def value(self, price: float) -> float:
        return self.cash + self.position * price


###############################################################################
# BACKTEST DRIVER
###############################################################################

class Backtester:
    """Glue everything together and produce an equity curve DataFrame."""

    def __init__(self, data: DataProvider, strategy: Strategy, portfolio: Portfolio):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self, symbol: str, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:  # noqa: D401,E501
        prices = self.data.fetch(symbol, start, end)
        trades = self.strategy.generate_signals(prices)
        for time, row in prices.iterrows():
            trade_signal = trades.get(time, 0)
            self.portfolio.update(row["Close"], trade_signal)
        equity = pd.Series(self.portfolio.history, index=prices.index[: len(self.portfolio.history)], name="Equity")  # noqa: E501
        return equity.to_frame()


###############################################################################
# QUICK DEMO when run as `python quant_engine.py`
###############################################################################

if __name__ == "__main__":
    provider = YahooDataProvider()
    strat = MovingAverageCrossStrategy()
    pf = Portfolio(initial_cash=100_000)
    bt = Backtester(provider, strat, pf)
    equity_curve = bt.run("SPY", start=dt.datetime(2015, 1, 1), end=dt.datetime(2025, 1, 1))
    print(equity_curve.tail())
