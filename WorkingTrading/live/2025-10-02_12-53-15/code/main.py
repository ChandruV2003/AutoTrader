# Working Trading Algorithm - Technical Analysis Only
from AlgorithmImports import *

class WorkingTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetCash(10_000)
        
        # Add SPY equity
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # Technical indicators
        self.fast_sma = self.SMA(self.symbol, 20, Resolution.Daily)
        self.slow_sma = self.SMA(self.symbol, 50, Resolution.Daily)
        self.rsi = self.RSI(self.symbol, 14, MovingAverageType.Wilders)
        self.macd = self.MACD(self.symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)
        self.bb = self.BB(self.symbol, 20, 2, MovingAverageType.Simple, Resolution.Daily)
        
        # Risk management
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        self.max_position_size = 0.95  # Use 95% of portfolio
        
        self.SetWarmUp(50)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
    def OnData(self, data: Slice):
        if self.IsWarmingUp or not data.ContainsKey(self.symbol):
            return
            
        # Technical signals
        sma_bullish = self.fast_sma.Current.Value > self.slow_sma.Current.Value
        rsi_oversold = self.rsi.Current.Value < 30
        rsi_overbought = self.rsi.Current.Value > 70
        macd_bullish = self.macd.Current.Value > self.macd.Signal.Current.Value
        bb_oversold = self.bb.Current.Value < self.bb.LowerBand.Current.Value
        bb_overbought = self.bb.Current.Value > self.bb.UpperBand.Current.Value
        
        # Trading logic - more aggressive for better profitability
        should_buy = (sma_bullish and macd_bullish) or \
                    (sma_bullish and rsi_oversold) or \
                    (sma_bullish and bb_oversold)
        
        should_sell = (not sma_bullish) or \
                     (rsi_overbought) or \
                     (bb_overbought)
        
        # Execute trades
        if should_buy and not self.Portfolio.Invested:
            self.SetHoldings(self.symbol, self.max_position_size)
            self.Debug(f"BUY: SMA={sma_bullish}, RSI={self.rsi.Current.Value:.1f}, MACD={macd_bullish}")
            
        elif should_sell and self.Portfolio.Invested:
            self.Liquidate(self.symbol)
            self.Debug(f"SELL: SMA={sma_bullish}, RSI={self.rsi.Current.Value:.1f}")
        
        # Risk management - stop loss and take profit
        if self.Portfolio.Invested:
            entry_price = self.Portfolio[self.symbol].AveragePrice
            current_bar = data[self.symbol]
            if current_bar is None or current_bar.Close is None:
                return
            current_price = current_bar.Close
            
            # Stop loss
            if current_price <= entry_price * (1 - self.stop_loss_pct):
                self.Liquidate(self.symbol)
                self.Debug(f"STOP LOSS: Entry={entry_price:.2f}, Current={current_price:.2f}")
            
            # Take profit
            elif current_price >= entry_price * (1 + self.take_profit_pct):
                self.Liquidate(self.symbol)
                self.Debug(f"TAKE PROFIT: Entry={entry_price:.2f}, Current={current_price:.2f}")
