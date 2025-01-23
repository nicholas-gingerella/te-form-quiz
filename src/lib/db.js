// lib/db.js
const pgp = require('pg-promise')();

const cn = {
  connectionString: process.env.DATABASE_URL,
  // Needed when running in Docker
  max: 30,
  ssl: false
};

const db = pgp(cn);

module.exports = db;