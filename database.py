import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vietlearn.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vietnamese TEXT NOT NULL,
            french TEXT NOT NULL,
            category TEXT DEFAULT '',
            difficulty INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS review_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vocab_id INTEGER NOT NULL,
            correct INTEGER DEFAULT 0,
            incorrect INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 0,
            FOREIGN KEY (vocab_id) REFERENCES vocabulary(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#6366f1'
        );
    """)
    conn.commit()
    conn.close()
