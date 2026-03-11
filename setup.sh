#!/bin/bash
set -e

echo "Starting setup..."

# 1. Install Node dependencies
if [ -f "package.json" ]; then
    echo "Installing root Node dependencies..."
    npm install
else
    echo "Warning: package.json not found."
fi

# Install Theme dependencies
if [ -d "custom-resume-theme" ] && [ -f "custom-resume-theme/package.json" ]; then
    echo "Installing custom-resume-theme dependencies..."
    (cd custom-resume-theme && npm install)
else
    echo "Warning: custom-resume-theme/package.json not found."
fi

# 2. Setup Python Virtual Environment
echo "Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate venv
source venv/bin/activate

# Install Python requirements
if [ -f "requirements.txt" ]; then
    echo "Installing Python requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Skipping pip install."
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo "Setup complete."
