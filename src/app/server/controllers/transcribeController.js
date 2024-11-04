// Handles the transcription logic. This file manages the workflow, calling services or utilities as needed.
const { transcribeAudio } = require('../services/openaiService');

exports.transcribeSpeech = async (req, res, next) => {
  try {
    const audioData = req.body.audio;
    const transcription = await transcribeAudio(audioData);
    res.json({ transcription });
  } catch (error) {
    next(error);   // Pass error to the error handling middleware
  }
};