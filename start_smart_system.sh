#!/bin/bash
# Smart Trading System Startup Script

echo "🧠 Starting Smart Trading System..."
echo "🎯 Integrated AI Trading with Continuous Learning"
echo "📊 Learns from every trade outcome"
echo "🚀 Adapts to market conditions"
echo "💰 Maximizes returns through intelligent learning"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Install required packages
echo "📦 Installing smart trading dependencies..."
pip install xgboost lightgbm scikit-learn selenium

# Create necessary directories
mkdir -p data models logs reports screenshots learning_data

# Start the smart trading system
echo "🔄 Starting smart trading system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo "📊 Reports will be saved in reports/ directory"
echo "📸 Screenshots will be saved to screenshots/ directory"
echo ""
echo "🧠 SMART TRADING FEATURES:"
echo "   - Continuous model improvement"
echo "   - Dynamic confidence thresholds"
echo "   - Learning from trade outcomes"
echo "   - Adaptive position sizing"
echo "   - Real-time performance optimization"
echo "   - Integrated browser automation"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Make sure you're logged into Webull or Robinhood"
echo "   - The system will automatically execute trades"
echo "   - All trades will be logged and screenshots taken"
echo "   - Models continuously learn and improve"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python smart_trading_system.py
