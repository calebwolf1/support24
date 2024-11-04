// Contains configuration values, such as API keys and environment variables.
require('dotenv').config();

module.exports = {
  openaiApiKey: process.env.OPENAI_API_KEY,
  otherConfig: process.env.OTHER_CONFIG,
};