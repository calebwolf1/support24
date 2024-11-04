// Handles all interactions with the OpenAI API, such as making transcription or analysis calls.
const axios = require('axios');

exports.transcribeAudio = async (audioData) => {
  // Logic for making an API request to OpenAI to transcribe audio
  const response = await axios.post('https://api.openai.com/v1/speech/transcribe', {
    data: audioData,
  }, {
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
  });
  return response.data.transcription;
};