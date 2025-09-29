#!/bin/bash

# Start the PM2 process and all the bots
pm2 start ecosystem.config.js

# Add a cron job to run the check_liquidatable_positions script daily at midnight

# Ensure the logs directory exists
mkdir -p ./logs

# Define the cron job commands
# Assuming the script is located in ~/Projects/dHEDGE-Bots
# NOTE: This is only for FM v1. Update the command as necessary for other versions or configurations.
CRON_JOB="0 0 * * * bash -c 'cd ~/Projects/dHEDGE-Bots && export $(cat .env | xargs) && source .venv/bin/activate && .venv/bin/ape run check_liquidatable_positions_v1 --network base:mainnet:alchemy  --leverage-module-address 0xdB0Cd65dcc7fE07003cE1201f91E1F966fA95768 --liquidation-module-address 0x981a29dC987136d23dF5a0f67d86f428Fb40E8Aa --market-name Base-rETH-PERP >> ./logs/check_liquidatable_positions.log_v1 2>&1'"

# Check if the cron job already exists and add it if it doesn't
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") || (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
