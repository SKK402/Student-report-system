const pool = require("./db");

pool.query("SELECT NOW()", (err, res) => {
  if (err) {
    console.error("Database connection error", err);
  } else {
    console.log("Connected to PostgreSQL:", res.rows);
  }
  pool.end();
});
