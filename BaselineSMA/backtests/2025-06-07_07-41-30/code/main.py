#!/usr/bin/env python3
from QuantConnect import Resolution
from QuantConnect.Indicators import MovingAverageType
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Data.Market import TradeBar
from QuantConnect.Indicators import RollingWindow

class BaselineSMA(QCAlgorithm):
    def Initialize(self):
        self.symbol = self.AddEquity("SPY", Resolution.Hour).Symbol
        self.price_history = RollingWindow
        self.macd = self.MACD(
            self.symbol, 12, 26, 9,
            MovingAverageType.Exponential, Resolution.Hour
        )

    def OnData(self, data):
        if not data.ContainsKey(self.symbol): return
        bar = data[self.symbol]
        if data.ContainsKey(self.symbol):
            bar = data[self.symbol]
            self.price_history.Add(bar)

        # bail until window is full & no None
        if not self.price_history.IsReady or any(b is None for b in self.price_history):
            return

        closes = [b.Close for b in self.price_history]
        sma_short = sum(closes[-10:]) / 10
        sma_long  = sum(closes) / len(closes)
        macd_diff = self.macd.Fast.Current.Value - self.macd.Signal.Current.Value

        if sma_short > sma_long and macd_diff > 0:
            self.SetHoldings(self.symbol, 1)
        else:
            self.Liquidate(self.symbol)
