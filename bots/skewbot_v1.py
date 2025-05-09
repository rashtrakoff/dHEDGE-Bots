import os
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

from ape import Contract, chain, networks
from ape.types import ContractLog
from silverback import SilverbackBot, StateSnapshot
from slack_sdk import WebClient

# Replace command-line arguments with environment variables
VIEWER_CONTRACT_ADDRESS = os.getenv("VIEWER_ADDRESS")
VAULT_CONTRACT_ADDRESS = os.getenv("VAULT_ADDRESS")
NETWORK_CHOICE = os.getenv("NETWORK")
MARKET_NAME = os.getenv("MARKET_NAME")

# Validate the provided environment variables
if not VIEWER_CONTRACT_ADDRESS or not VIEWER_CONTRACT_ADDRESS.startswith("0x") or len(VIEWER_CONTRACT_ADDRESS) != 42:
    raise ValueError("Invalid Viewer contract address")
if not VAULT_CONTRACT_ADDRESS or not VAULT_CONTRACT_ADDRESS.startswith("0x") or len(VAULT_CONTRACT_ADDRESS) != 42:
    raise ValueError("Invalid Vault contract address")
if not NETWORK_CHOICE:
    raise ValueError("Network is required")
if not MARKET_NAME:
    raise ValueError("Market name is required")

# Initialize contracts dynamically
with networks.parse_network_choice(NETWORK_CHOICE) as provider:
    VIEWER_CONTRACT = Contract(VIEWER_CONTRACT_ADDRESS, abi="abi/Viewer-v1.json")
    VAULT_CONTRACT = Contract(VAULT_CONTRACT_ADDRESS, abi="abi/FlatcoinVault-v1.json")

# Initialize the bot
bot = SilverbackBot()

# Log the market name
logging.info(f"Market Name: {MARKET_NAME}")

# Global variables
SLACK_CHANNEL = os.getenv("FM_BOT_SLACK_CHANNEL")
WARNING_THRESHOLD = 5  # 5% skew difference
CRITICAL_THRESHOLD = 10  # 10% skew difference
STEP_SIZE = 1  # 1% skew difference
THRESHOLD_EMOJI = {
    "normal": ":large_green_circle:",
    "warning": ":large_yellow_circle:",
    "critical": ":red_circle:",
}
DIRECTION_EMOJI = {
    "increased": ":arrow_up:",
    "decreased": ":arrow_down:",
}


@bot.on_startup()
def bot_startup(_):
    set_logging_settings()
    logging.info(f"Skew bot started at {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    logging.info(f"Slack bot alerts channel: {SLACK_CHANNEL}")

    # 1. Initialize slack client.
    bot.state.slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    # 2. Get the current skew from the contract.
    bot.state.skew = get_current_skew_percent()

    logging.info(f"Skew percent at startup: {bot.state.skew}%")


@bot.on_(VAULT_CONTRACT.FundingFeesSettled)
def on_funding_fees_settled(log: ContractLog):
    logging.info(f"Funding fees settlement event occurred: {log}")

    # 1. Get the current skew percentage from the contract upto 4 decimal places.
    current_skew_percent = get_current_skew_percent()
    abs_current_skew = abs(current_skew_percent)

    # 2. Calculate the absolute skew percentage difference to 1 decimal place.
    skew_difference = round(abs(current_skew_percent - bot.state.skew), 1)

    # 3. If the skew difference is greater than `STEP_SIZE` percent, send a slack message.
    if skew_difference >= STEP_SIZE:
        if abs_current_skew > CRITICAL_THRESHOLD:
            range = "critical"
        elif (
            abs_current_skew > WARNING_THRESHOLD
            and abs_current_skew < CRITICAL_THRESHOLD
        ):
            range = "warning"
        else:
            range = "normal"

        if abs_current_skew > abs(bot.state.skew):
            direction = "increased"
        else:
            direction = "decreased"


        skew_bias = "long" if current_skew_percent < 0 else "short"

        # 3.1 Determine the current skew status and send a slack message accordingly.
        message = f"{THRESHOLD_EMOJI[range]} {DIRECTION_EMOJI[direction]} [{MARKET_NAME}] Market skew at {current_skew_percent:.2f} {skew_bias}%"
        logging.info(f"[{MARKET_NAME}] Current skew: {current_skew_percent}%")

        # 3.2 Update the skew in the bot state only when skew percentage has changed
        #    beyond a certain threshold.
        bot.state.skew = current_skew_percent

        # 3.3 Send slack message.
        response = bot.state.slack_client.chat_postMessage(
            channel=SLACK_CHANNEL, text=message
        )

        if response.get("ok", False):
            logging.info("Slack message sent successfully")
        else:
            logging.error(
                f"Error sending slack message: {response.get('error', 'Unknown error')}"
            )

def set_logging_settings():
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Set log levels
    stdout_handler.setLevel(logging.INFO)
    stderr_handler.setLevel(logging.ERROR)

    # Create formatters and add them to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

def get_current_skew_percent():
    return round(VIEWER_CONTRACT.getMarketSkewPercentage() / 1e16, 4)
