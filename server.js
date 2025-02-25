require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { Pool } = require("pg");

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// PostgreSQL Connection
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: parseInt(process.env.DB_PORT, 10) || 5432,
});

pool.connect()
  .then(() => console.log("Connected to PostgreSQL ✅"))
  .catch(err => console.error("Connection Error ❌", err));

// Health Check Route
app.get("/", (req, res) => {
  res.send("Backend is working! 🚀");
});

// 📌 API to get all students
app.get("/students", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM students");
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "No students found" });
    }
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching students:", err);
    res.status(500).json({ error: "Database Error", details: err.message });
  }
});

// 📌 API to get all reports
app.get("/reports", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM reports");
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "No reports found" });
    }
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching reports:", err);
    res.status(500).json({ error: "Database Error", details: err.message });
  }
});

// 📌 API to get attendance data
app.get("/attendance", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM attendance");
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "No attendance records found" });
    }
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching attendance:", err);
    res.status(500).json({ error: "Database Error", details: err.message });
  }
});

// 📌 API to get marks
app.get("/marks", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM marks");
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "No marks found" });
    }
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching marks:", err);
    res.status(500).json({ error: "Database Error", details: err.message });
  }
});

// 📌 API to get subjects
app.get("/subjects", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM subjects");
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "No subjects found" });
    }
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching subjects:", err);
    res.status(500).json({ error: "Database Error", details: err.message });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
