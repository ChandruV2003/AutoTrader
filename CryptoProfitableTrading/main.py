# Profitable Crypto Trading Algorithm
from AlgorithmImports import *

class CryptoProfitableTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetCash(10_000)
        
        # Add crypto symbols
        self.btc = self.AddCrypto("BTCUSD", Resolution.Hour).Symbol
        self.eth = self.AddCrypto("ETHUSD", Resolution.Hour).Symbol
        
        # Technical indicators for BTC
        self.btc_fast_sma = self.SMA(self.btc, 20, Resolution.Hour)
        self.btc_slow_sma = self.SMA(self.btc, 50, Resolution.Hour)
        self.btc_rsi = self.RSI(self.btc, 14, MovingAverageType.Wilders)
        self.btc_macd = self.MACD(self.btc, 12, 26, 9, MovingAverageType.Exponential, Resolution.Hour)
        
        # Technical indicators for ETH
        self.eth_fast_sma = self.SMA(self.eth, 20, Resolution.Hour)
        self.eth_slow_sma = self.SMA(self.eth, 50, Resolution.Hour)
        self.eth_rsi = self.RSI(self.eth, 14, MovingAverageType.Wilders)
        self.eth_macd = self.MACD(self.eth, 12, 26, 9, MovingAverageType.Exponential, Resolution.Hour)
        
        # Risk management (more aggressive for crypto)
        self.stop_loss_pct = 0.08  # 8% stop loss (crypto is more volatile)
        self.take_profit_pct = 0.25  # 25% take profit (crypto moves more)
        self.max_position_size = 0.45  # 45% per crypto (90% total)
        
        self.SetWarmUp(50)
        self.SetBrokerageModel(BrokerageName.BinanceBrokerage, AccountType.Cash)
        
    def get_signals(self, symbol, fast_sma, slow_sma, rsi, macd):
        """Get trading signals for a symbol"""
        sma_bullish = fast_sma.Current.Value > slow_sma.Current.Value
        rsi_oversold = rsi.Current.Value < 30
        rsi_overbought = rsi.Current.Value > 70
        macd_bullish = macd.Current.Value > macd.Signal.Current.Value
        
        # More aggressive signals for crypto
        should_buy = (sma_bullish and macd_bullish) or \
                    (sma_bullish and rsi_oversold) or \
                    (macd_bullish and rsi_oversold)
        
        should_sell = (not sma_bullish) or \
                     (rsi_overbought) or \
                     (not macd_bullish and rsi.Current.Value > 60)
        
        return should_buy, should_sell
        
    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return
            
        # Process BTC
        if data.ContainsKey(self.btc):
            should_buy, should_sell = self.get_signals(
                self.btc, self.btc_fast_sma, self.btc_slow_sma, 
                self.btc_rsi, self.btc_macd
            )
            
            if should_buy and not self.Portfolio[self.btc].Invested:
                self.SetHoldings(self.btc, self.max_position_size)
                self.Debug(f"BTC BUY: SMA={self.btc_fast_sma.Current.Value > self.btc_slow_sma.Current.Value}, RSI={self.btc_rsi.Current.Value:.1f}")
                
            elif should_sell and self.Portfolio[self.btc].Invested:
                self.Liquidate(self.btc)
                self.Debug(f"BTC SELL: RSI={self.btc_rsi.Current.Value:.1f}")
            
            # Risk management for BTC
            if self.Portfolio[self.btc].Invested:
                entry_price = self.Portfolio[self.btc].AveragePrice
                current_price = data[self.btc].Close
                
                if current_price <= entry_price * (1 - self.stop_loss_pct):
                    self.Liquidate(self.btc)
                    self.Debug(f"BTC STOP LOSS: Entry={entry_price:.2f}, Current={current_price:.2f}")
                elif current_price >= entry_price * (1 + self.take_profit_pct):
                    self.Liquidate(self.btc)
                    self.Debug(f"BTC TAKE PROFIT: Entry={entry_price:.2f}, Current={current_price:.2f}")
        
        # Process ETH
        if data.ContainsKey(self.eth):
            should_buy, should_sell = self.get_signals(
                self.eth, self.eth_fast_sma, self.eth_slow_sma, 
                self.eth_rsi, self.eth_macd
            )
            
            if should_buy and not self.Portfolio[self.eth].Invested:
                self.SetHoldings(self.eth, self.max_position_size)
                self.Debug(f"ETH BUY: SMA={self.eth_fast_sma.Current.Value > self.eth_slow_sma.Current.Value}, RSI={self.eth_rsi.Current.Value:.1f}")
                
            elif should_sell and self.Portfolio[self.eth].Invested:
                self.Liquidate(self.eth)
                self.Debug(f"ETH SELL: RSI={self.eth_rsi.Current.Value:.1f}")
            
            # Risk management for ETH
            if self.Portfolio[self.eth].Invested:
                entry_price = self.Portfolio[self.eth].AveragePrice
                current_price = data[self.eth].Close
                
                if current_price <= entry_price * (1 - self.stop_loss_pct):
                    self.Liquidate(self.eth)
                    self.Debug(f"ETH STOP LOSS: Entry={entry_price:.2f}, Current={current_price:.2f}")
                elif current_price >= entry_price * (1 + self.take_profit_pct):
                    self.Liquidate(self.eth)
                    self.Debug(f"ETH TAKE PROFIT: Entry={entry_price:.2f}, Current={current_price:.2f}")
