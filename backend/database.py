import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pocketsmart.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        group_type TEXT NOT NULL, -- 'need', 'want', 'saving'
        monthly_budget REAL NOT NULL DEFAULT 0.0,
        icon TEXT DEFAULT 'tag',
        color TEXT DEFAULT '#6366f1'
    )
    """)
    
    # 2. Transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, -- YYYY-MM-DD
        amount REAL NOT NULL,
        type TEXT NOT NULL, -- 'expense' or 'income'
        category TEXT NOT NULL,
        merchant TEXT,
        note TEXT,
        payment_method TEXT DEFAULT 'Card',
        is_recurring INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Monthly Budget Config
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_config (
        month TEXT PRIMARY KEY, -- YYYY-MM
        monthly_income REAL NOT NULL DEFAULT 4000.0,
        needs_target_pct REAL DEFAULT 50.0,
        wants_target_pct REAL DEFAULT 30.0,
        savings_target_pct REAL DEFAULT 20.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. Savings Goals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS savings_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL NOT NULL DEFAULT 0.0,
        target_date TEXT,
        icon TEXT DEFAULT 'target',
        color TEXT DEFAULT '#10b981',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 5. Subscriptions / Recurring Bills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cost REAL NOT NULL,
        billing_cycle TEXT DEFAULT 'monthly', -- 'monthly' or 'annual'
        category TEXT DEFAULT 'Entertainment',
        next_due_date TEXT,
        is_essential INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active' -- 'active', 'cancelled', 'review'
    )
    """)
    
    # 6. Affordability Recommendation Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS affordability_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        urgency TEXT NOT NULL,
        verdict TEXT NOT NULL, -- 'Safe', 'Caution', 'High Risk'
        affordability_score INTEGER NOT NULL, -- 0 to 100
        analysis TEXT,
        recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
