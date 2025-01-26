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
        FM_BOT_SLACK_CHANNEL: process.env.FM_BOT_SLACK_CHANNEL,
      },
      auto_restart: true,
    },
    {
      name: "check_liquidatable_positions",
      script: "ape",
      args: "run check_liquidatable_positions --network base:mainnet:alchemy",
      interpreter: "none", // Use "none" to run the command directly
      watch: false,
      cron_restart: "0 0 * * *", // Restart every day at midnight
      env: {
        SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
        FM_BOT_SLACK_CHANNEL: process.env.FM_BOT_SLACK_CHANNEL,
      },
    }
  ],
};