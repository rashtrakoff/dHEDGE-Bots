require("dotenv").config();

module.exports = {
    apps: [
        {
            name: "Base-rETH-PERP-skewbot",
            script: "silverback",
            args: "run skewbot_v1 --network base:mainnet:alchemy",
            env: {
                VIEWER_ADDRESS: "0x6928347462F0a9eA96bD5eDc6DaCCE3F8a44d147",
                VAULT_ADDRESS:
                    "0x95Fa1ddc9a78273f795e67AbE8f1Cd2Cd39831fF",
                NETWORK: "base:mainnet:alchemy",
                MARKET_NAME: "Base-rETH-PERP",
                SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
                WEB3_BASE_MAINNET_ALCHEMY_PROJECT_ID: process.env.WEB3_BASE_MAINNET_ALCHEMY_PROJECT_ID,
            },
            interpreter: "none", // Use "none" to run the command directly
            watch: false,
            auto_restart: true,
        },
        {
            name: "OP-WBTC-PERP-skewbot",
            script: "silverback",
            args: "run skewbot_v2 --network optimism:mainnet:alchemy",
            env: {
                VIEWER_ADDRESS: "0x1F1A5f8c2d133b0c663cf85943B8E73ec143DB16",
                CONTROLLER_ADDRESS:
                    "0x59525b9b23ADc475EF91d98dAe06B568BA574Ce5",
                NETWORK: "optimism:mainnet:alchemy",
                MARKET_NAME: "OP-WBTC-PERP",
                SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
                WEB3_OPTIMISM_MAINNET_ALCHEMY_PROJECT_ID: process.env.WEB3_OPTIMISM_MAINNET_ALCHEMY_PROJECT_ID,
            },
            interpreter: "none", // Use "none" to run the command directly
            watch: false,
            auto_restart: true,
        },
    ],
};
