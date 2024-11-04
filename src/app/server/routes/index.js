// This file acts as a central router, combining other route files. 
// It organizes and consolidates route handling for easier management.
const express = require('express');
const transcribeRoutes = require('./transcribeRoutes');
const parseRoutes = require('./parseRoutes');
const factCheckRoutes = require('./factCheckRoutes');

const router = express.Router();

router.use('/transcribe', transcribeRoutes);    // e.g., /api/transcribe
router.use('/parse', parseRoutes);              // e.g., /api/parse
router.use('/fact-check', factCheckRoutes);     // e.g., /api/fact-check

module.exports = router;
