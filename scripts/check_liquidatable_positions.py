import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from ape import Contract, chain, networks
from ape.types import ContractLog
from ape_ethereum import multicall
from slack_sdk import WebClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Global variables
SLACK_CHANNEL = os.getenv("FM_BOT_SLACK_CHANNEL")
CHUNK_SIZE = 10  # Number of positions to check at a time
LEVERAGE_MODULE_ADDRESS = "0xdB0Cd65dcc7fE07003cE1201f91E1F966fA95768"
LIQUIDATION_MODULE_ADDRESS = "0x981a29dC987136d23dF5a0f67d86f428Fb40E8Aa"
SLACK_CLIENT = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

with networks.parse_network_choice("base:mainnet:alchemy") as provider:
    LEVERAGE_MODULE = Contract(LEVERAGE_MODULE_ADDRESS, abi="abi/LeverageModule.json")
    LIQUIDATION_MODULE = Contract(
        LIQUIDATION_MODULE_ADDRESS, abi="abi/LiquidationModule.json"
    )


# Main script
def main():
    positions = get_liquidatable_positions()

    text = f"Checked all positions and found {len(positions)} liquidatable positions"
    formatted_positions = " ".join(map(str, positions))

    if len(positions) > 0:
        text += f": \n\n {formatted_positions}"

    SLACK_CLIENT.chat_postMessage(channel=SLACK_CHANNEL, text=text)


def get_liquidatable_positions():
    logging.info(
        f"Checking liquidatable positions at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 1. Get the total number of positions.
    total_positions = LEVERAGE_MODULE.totalSupply()
    logging.info(f"Total positions: {total_positions}")

    total_chunks = (
        total_positions // CHUNK_SIZE + 1
        if total_positions % CHUNK_SIZE > 0
        else total_positions // CHUNK_SIZE
    )
    extra_loop_required = total_positions % CHUNK_SIZE > 0

    positions = []
    for i in range(total_chunks):
        call = multicall.Call()

        for j in range(
            total_positions % CHUNK_SIZE
            if i == total_chunks - 1 and extra_loop_required
            else CHUNK_SIZE
        ):
            call.add(LEVERAGE_MODULE.tokenByIndex, i * CHUNK_SIZE + j)

        positions.extend(list(call()))

    liquidation_statuses = []
    for i in range(total_chunks):
        call = multicall.Call()

        for j in range(
            total_positions % CHUNK_SIZE
            if i == total_chunks - 1 and extra_loop_required
            else CHUNK_SIZE
        ):
            call.add(LIQUIDATION_MODULE.canLiquidate, positions[i * CHUNK_SIZE + j])

        liquidation_statuses.extend(list(call()))

    liquidatable_positions = [
        positions[i]
        for i in range(len(liquidation_statuses))
        if liquidation_statuses[i]
    ]

    logging.info(f"Found {len(liquidatable_positions)} liquidatable positions")

    return liquidatable_positions
