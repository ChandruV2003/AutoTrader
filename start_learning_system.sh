#!/bin/bash
# Advanced Learning System Startup Script

echo "🧠 Starting Advanced Learning System..."
echo "🎯 Continuously improving trading AI"
echo "📊 Learns from every trade outcome"
echo "🚀 Adapts to changing market conditions"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Install required packages for advanced learning
echo "📦 Installing advanced learning dependencies..."
pip install optuna xgboost lightgbm scikit-learn scipy

# Create necessary directories
mkdir -p data models logs learning_reports model_versions feature_analysis

# Check if required packages are installed
python -c "import optuna, xgboost, lightgbm, sklearn, scipy; print('✅ All packages installed successfully')"

if [ $? -ne 0 ]; then
    echo "❌ Some packages failed to install. Please check the error messages above."
    exit 1
fi

# Start the advanced learning system
echo "🔄 Starting advanced learning system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in model_versions/ directory"
echo "📊 Reports will be saved in learning_reports/ directory"
echo ""
echo "🧠 LEARNING FEATURES:"
echo "   - Continuous model improvement"
echo "   - Ensemble learning with multiple algorithms"
echo "   - Hyperparameter optimization"
echo "   - Market regime detection"
echo "   - Feature importance tracking"
echo "   - Performance degradation detection"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python advanced_learning_system.py
