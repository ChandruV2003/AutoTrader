# 50 / 200-day SMA crossover baseline
from AlgorithmImports import *

class BaselineSMACross(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(1993, 1, 29)
        self.SetCash(10_000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.fast   = self.SMA(self.symbol, 50,  Resolution.Daily)
        self.slow   = self.SMA(self.symbol, 200, Resolution.Daily)

        self.SetWarmUp(200)

    def OnData(self, data: Slice):
        if self.IsWarmingUp or not data.ContainsKey(self.symbol):
            return

        if self.fast.Current.Value > self.slow.Current.Value and not self.Portfolio.Invested:
            self.SetHoldings(self.symbol, 1)
        elif self.fast.Current.Value < self.slow.Current.Value and self.Portfolio.Invested:
            self.Liquidate()
