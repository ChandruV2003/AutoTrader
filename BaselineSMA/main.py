from AlgorithmImports import *

class BaselineSMA(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2012, 1, 1)
        self.SetCash(10_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.fast = self.SMA(self.spy, 50, Resolution.Daily)
        self.slow = self.SMA(self.spy, 200, Resolution.Daily)
        self.SetWarmUp(200)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        self.atr = self.ATR(self.spy, 14, MovingAverageType.Simple)
        self.stop_pct = 2.0

    def OnData(self, data):
        if self.IsWarmingUp:
            return
        if self.fast.Current.Value > self.slow.Current.Value and not self.Portfolio.Invested:
            self.SetHoldings(self.spy, 1)
        elif self.fast.Current.Value < self.slow.Current.Value and self.Portfolio.Invested:
            self.Liquidate(self.spy)
