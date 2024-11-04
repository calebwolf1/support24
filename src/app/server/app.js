const express = require("express");
const routes = require("."); // Import your routes
const errorHandler = require("./middleware/error-handler");

const app = express();

app.use(express.json()); // Parse incoming JSON requests
app.use("/api", routes); // Mount all routes under the /api prefix
app.use(errorHandler); // Custom error handling middleware

module.exports = app;

// Key Differences Between layout.js and app.js
// Purpose:
// layout.js structures the UI layout of the React frontend, helping to build a consistent look and feel for the user interface.
// app.js configures the server and handles backend functionality, defining routes and middleware for the Express API.
// Location and Scope:
// layout.js is part of the frontend, designed for React and user-facing elements.
// app.js is part of the backend, handling server logic and not visible to the end user.
// Usage:
// layout.js is used to wrap page components in React and provide a consistent UI layout.
// app.js is used to configure and initialize the Express server, handling API endpoints and data processing.
