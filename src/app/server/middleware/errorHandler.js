// A global error handler middleware to catch and handle errors consistently across the app.
module.exports = (err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Internal Server Error" });
};
