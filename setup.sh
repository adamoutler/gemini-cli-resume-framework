#!/bin/bash
set -e

echo "Starting setup..."

# 0. Check for cv-data Submodule
if ! git submodule status | grep -q "cv-data"; then
    echo ""
    echo "=========================================================================="
    echo "🚨 SECURITY RECOMMENDATION 🚨"
    echo "The 'cv-data' directory is currently NOT a git submodule."
    echo "Your cv-data directory will contain highly sensitive personal information,"
    echo "including your phone number, email, work history, and private projects."
    echo ""
    echo "We STRONGLY RECOMMEND storing this data in a separate PRIVATE git repository"
    echo "and including it here as a submodule. This ensures you can safely version"
    echo "control the Resume Writer framework without accidentally publishing your"
    echo "personal data."
    echo "=========================================================================="
    echo ""
    # We output a specific token here that the Gemini agent can look for.
    echo "[GEMINI_HOOK: SUBMODULE_RECOMMENDED]"
    echo ""
fi

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
