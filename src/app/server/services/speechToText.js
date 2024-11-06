// CALL API ENV KEY HERE
require("dotenv").config();

// Use your API key
// const apiKey = process.env.[INSERT NAME]


// Handles all interactions with the OpenAI API, such as making transcription or analysis calls.
const axios = require("axios");

exports.transcribeAudio = async (audioData) => {
  // Logic for making an API request to OpenAI to transcribe audio
  const response = await axios.post(
    // "https://api.openai.com/v1/speech/transcribe", WRONG
    {
      data: audioData,
    },
    {
      headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
    }
  );
  return response.data.transcription;
};
