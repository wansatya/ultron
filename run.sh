#!/bin/bash
# Quick start script for Ultron

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN environment variable is not set"
    echo ""
    echo "Please set your Telegram bot token:"
    echo "  export TELEGRAM_BOT_TOKEN='your-token-here'"
    echo ""
    echo "To get a token, message @BotFather on Telegram"
    exit 1
fi

# Run Ultron
echo "Starting Ultron..."
python -m ultron.main
