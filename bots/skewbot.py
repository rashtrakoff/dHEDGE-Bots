import os
import logging
from datetime import datetime

from ape import Contract, chain, networks
from ape.types import ContractLog
from silverback import SilverbackBot, StateSnapshot
from slack_sdk import WebClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Initialize the bot
bot = SilverbackBot()

# Global variables
SLACK_CHANNEL = os.environ["SKEWBOT_SLACK_CHANNEL"]
WARNING_THRESHOLD = 5  # 5% skew difference
CRITICAL_THRESHOLD = 10  # 10% skew difference
STEP_SIZE = 1  # 1% skew difference
VIEWER_CONTRACT_ADDRESS = (
    "0x6928347462F0a9eA96bD5eDc6DaCCE3F8a44d147"  # Viewer contract address on Base
)
VAULT_CONTRACT_ADDRESS = (
    "0x95Fa1ddc9a78273f795e67AbE8f1Cd2Cd39831fF"  # Vault contract address on Base
)
THRESHOLD_EMOJI = {
    "normal": ":green_circle:",
    "warning": ":yellow_circle:",
    "critical": ":red_circle:",
}
DIRECTION_EMOJI = {
    "increased": ":arrow_up:",
    "decreased": ":arrow_down:",
}

with networks.parse_network_choice("base:mainnet:alchemy") as provider:
    VIEWER_CONTRACT = Contract(VIEWER_CONTRACT_ADDRESS, abi="abi/Viewer.json")
    VAULT_CONTRACT = Contract(VAULT_CONTRACT_ADDRESS, abi="abi/FlatcoinVault.json")


@bot.on_startup()
def bot_startup(_):
    logging.info(f"Skew bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Initialize slack client.
    bot.state.slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

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
            and current_skew_percent < CRITICAL_THRESHOLD
        ):
            range = "warning"
        else:
            range = "normal"

        if abs_current_skew > abs(bot.state.skew):
            direction = "increased"
        else:
            direction = "decreased"

        # 3.1 Determine the current skew status and send a slack message accordingly.
        message = f"{THRESHOLD_EMOJI[range]} {DIRECTION_EMOJI[direction]} Market skew changed to {current_skew_percent}%"

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


def get_current_skew_percent():
    return round(VIEWER_CONTRACT.getMarketSkewPercentage() / 1e16, 4)
