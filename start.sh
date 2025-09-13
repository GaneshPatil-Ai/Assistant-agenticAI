#!/bin/bash

# LangGraph Supervisor-Worker System Startup Script

set -e

echo "🚀 Starting LangGraph Supervisor-Worker System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.example"
    echo "   cp .env.example .env"
    echo "   Then edit .env and add your OpenAI API key"
    exit 1
fi

# Validate configuration
echo "✅ Configuration validated"

# Check if running in production mode
if [ "$1" = "production" ]; then
    echo "🏭 Starting in production mode with Gunicorn..."
    gunicorn -c gunicorn.conf.py api:app
else
    echo "🔬 Starting in development mode..."
    python run.py
fi