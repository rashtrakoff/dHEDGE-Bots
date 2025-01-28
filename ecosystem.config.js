module.exports = {
  apps: [
    {
      name: "skewbot",
      script: "silverback",
      args: "run skewbot --network base:mainnet:alchemy",
      interpreter: "none", // Use "none" to run the command directly
      watch: false,
      auto_restart: true,
    },
  ],
};