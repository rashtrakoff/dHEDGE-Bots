module.exports = {
  apps: [
    {
      name: "skewbot",
      script: "silverback",
      args: "run skewbot --network base:mainnet:alchemy",
      interpreter: "none", // Use "none" to run the command directly
      watch: false,
      env: {
        SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
        SKEWBOT_SLACK_CHANNEL: process.env.SKEWBOT_SLACK_CHANNEL,
      },
      auto_restart: true,
    },
  ],
};