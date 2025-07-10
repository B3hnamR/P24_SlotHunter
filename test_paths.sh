#!/bin/bash

# Test script to check paths
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
VENV_DIR="$PROJECT_DIR/venv"
CONFIG_FILE="$PROJECT_DIR/config/config.yaml"

echo "🔍 Testing paths..."
echo "PROJECT_DIR: $PROJECT_DIR"
echo "ENV_FILE: $ENV_FILE"
echo "VENV_DIR: $VENV_DIR"
echo "CONFIG_FILE: $CONFIG_FILE"
echo ""

echo "📁 Checking files..."
if [ -f "$ENV_FILE" ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file NOT found"
fi

if [ -d "$VENV_DIR" ]; then
    echo "✅ venv directory found"
else
    echo "❌ venv directory NOT found"
fi

if [ -f "$CONFIG_FILE" ]; then
    echo "✅ config.yaml found"
else
    echo "❌ config.yaml NOT found"
fi

echo ""
echo "📋 Directory contents:"
ls -la "$PROJECT_DIR" | head -10