#!/bin/bash
# Automated Weekly Model Retraining Script
# This script can be scheduled using cron

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV="$SCRIPT_DIR/venv"  # Virtual environment path
LOG_FILE="$SCRIPT_DIR/retraining.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "[$DATE] Starting automated model retraining..." >> "$LOG_FILE"

# Activate virtual environment if it exists
if [ -d "$PYTHON_ENV" ]; then
    source "$PYTHON_ENV/bin/activate"
    echo "[$DATE] Activated virtual environment" >> "$LOG_FILE"
fi

# Run retraining script
cd "$SCRIPT_DIR"
python auto_retrain_model.py >> "$LOG_FILE" 2>&1

RETURN_CODE=$?

if [ $RETURN_CODE -eq 0 ]; then
    echo "[$DATE] Retraining completed successfully" >> "$LOG_FILE"
    
    # Optional: Restart ML service (if using systemd or similar)
    # systemctl restart ml-prediction-service
    
    # Optional: Send notification (email, Slack, etc.)
    # curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
    #   -d "{\"text\":\"Model retraining completed successfully\"}"
else
    echo "[$DATE] Retraining failed with exit code $RETURN_CODE" >> "$LOG_FILE"
    
    # Optional: Send error notification
    # curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
    #   -d "{\"text\":\"Model retraining failed! Check logs.\"}"
fi

exit $RETURN_CODE

