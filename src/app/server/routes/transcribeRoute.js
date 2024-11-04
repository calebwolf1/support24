// Defines endpoints related to speech transcription, which will use controller methods to perform actions.
const express = require('express');
const { transcribeSpeech } = require('../controllers/transcribeController');

const router = express.Router();

router.post('/', transcribeSpeech);    // POST /api/transcribe

module.exports = router;