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
                MARKET_NAME: "Base-rETH-PERP",
                SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
                FM_BOT_SLACK_CHANNEL: process.env.FM_BOT_SLACK_CHANNEL,
                WEB3_ALCHEMY_API_KEY: process.env.WEB3_ALCHEMY_API_KEY,
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
                MARKET_NAME: "OP-WBTC-PERP",
                SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
                FM_BOT_SLACK_CHANNEL: process.env.FM_BOT_SLACK_CHANNEL,
                WEB3_ALCHEMY_API_KEY: process.env.WEB3_ALCHEMY_API_KEY,
            },
            interpreter: "none", // Use "none" to run the command directly
            watch: false,
            auto_restart: true,
        },
        {
            name: "Arb-WBTC-OPT-skewbot",
            script: "silverback",
            args: "run skewbot_v2 --network arbitrum:mainnet:alchemy",
            env: {
                VIEWER_ADDRESS: "0x487CFb84C874036240BaEe66d6C3042316af9F34",
                CONTROLLER_ADDRESS:
                    "0x3c4472d7D0F17A7e9158595b4e91Fb673BF44C8c",
                MARKET_NAME: "Arb-WBTC-OPT",
                SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
                FM_BOT_SLACK_CHANNEL: process.env.FM_BOT_SLACK_CHANNEL,
                WEB3_ALCHEMY_API_KEY: process.env.WEB3_ALCHEMY_API_KEY,
            },
            interpreter: "none", // Use "none" to run the command directly
            watch: false,
            auto_restart: true,
        },
    ],
};
