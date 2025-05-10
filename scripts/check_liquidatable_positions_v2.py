import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from ape import Contract, chain, networks
from ape.types import ContractLog
from ape_ethereum import multicall
from ape.cli import ConnectedProviderCommand
from slack_sdk import WebClient
import click

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Global variables
SLACK_CHANNEL = os.getenv("FM_BOT_SLACK_CHANNEL")
CHUNK_SIZE = 10  # Number of positions to check at a time
SLACK_CLIENT = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# Define the CLI using click
@click.command(cls=ConnectedProviderCommand)
@click.option('--leverage-module-address', type=str, required=True, help='Leverage module contract address')
@click.option('--liquidation-module-address', type=str, required=True, help='Liquidation module contract address')
@click.option('--market-name', type=str, required=True, help='Market name')
def cli(leverage_module_address, liquidation_module_address, market_name):
    # Assign arguments to variables
    global LEVERAGE_MODULE_ADDRESS, LIQUIDATION_MODULE_ADDRESS, MARKET_NAME
    LEVERAGE_MODULE_ADDRESS = leverage_module_address
    LIQUIDATION_MODULE_ADDRESS = liquidation_module_address
    MARKET_NAME = market_name

    # Validate the provided addresses
    if not LEVERAGE_MODULE_ADDRESS.startswith("0x") or len(LEVERAGE_MODULE_ADDRESS) != 42:
        raise ValueError("Invalid Leverage module address")
    if not LIQUIDATION_MODULE_ADDRESS.startswith("0x") or len(LIQUIDATION_MODULE_ADDRESS) != 42:
        raise ValueError("Invalid Liquidation module address")

    global LEVERAGE_MODULE, LIQUIDATION_MODULE
    LEVERAGE_MODULE = Contract(LEVERAGE_MODULE_ADDRESS, abi="abi/LeverageModule-v2.json")
    LIQUIDATION_MODULE = Contract(LIQUIDATION_MODULE_ADDRESS, abi="abi/LiquidationModule-v2.json")

    # Execute the main logic
    positions, total_positions = get_liquidatable_positions()

    text = f"[{MARKET_NAME}] Checked {total_positions} positions and found {len(positions)} liquidatable positions"
    formatted_positions = " ".join(map(str, positions))

    if len(positions) > 0:
        text += f": \n\n {formatted_positions}"

    SLACK_CLIENT.chat_postMessage(channel=SLACK_CHANNEL, text=text)


def get_liquidatable_positions():
    logging.info(
        f"[{MARKET_NAME}] Checking liquidatable positions at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 1. Get the total number of positions.
    total_positions = LEVERAGE_MODULE.totalSupply()
    logging.info(f"Total positions: {total_positions}")

    # 2. Calculate the number of times looping is required after accounting for batched calls.
    total_chunks = (
        total_positions // CHUNK_SIZE + 1
        if total_positions % CHUNK_SIZE > 0
        else total_positions // CHUNK_SIZE
    )
    extra_loop_required = total_positions % CHUNK_SIZE > 0

    # 3. Batch calls to get the token IDs of all positions.
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

    # 4. Batch calls to check if the positions are liquidatable.
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

    # 5. Filter out the liquidatable positions.
    liquidatable_positions = [
        positions[i]
        for i in range(len(liquidation_statuses))
        if liquidation_statuses[i]
    ]

    logging.info(f"[{MARKET_NAME}] Checked {total_positions} positions")
    logging.info(f"[{MARKET_NAME}] Found {len(liquidatable_positions)} liquidatable positions")

    return liquidatable_positions, total_positions


# Main script entry point
# if __name__ == "__main__":
#     main()
