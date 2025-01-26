#!/bin/bash

# Start the PM2 process and all the bots
pm2 start ecosystem.config.js

# Add a cron job to run the check_liquidatable_positions script daily at midnight
# Define the cron job command
CRON_JOB="0 0 * * * /home/rashtrakoff/Projects/dHEDGE-Bots/.venv/bin/ape run check_liquidatable_positions --network base:mainnet:alchemy >> /home/rashtrakoff/cronjob.log 2>&1"

# Check if the cron job already exists and add it if it doesn't
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") || (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
