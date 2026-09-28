from datetime import datetime, timedelta
import random
from database import get_db, init_db

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        print("Data already seeded.")
        conn.close()
        return

    # 1. Categories
    default_categories = [
        # Needs (50%)
        ("Housing & Rent", "need", 1200.0, "home", "#3b82f6"),
        ("Groceries", "need", 450.0, "shopping-cart", "#10b981"),
        ("Utilities & Bills", "need", 200.0, "zap", "#f59e0b"),
        ("Healthcare & Meds", "need", 150.0, "activity", "#ec4899"),
        ("Transportation", "need", 250.0, "truck", "#6366f1"),
        
        # Wants (30%)
        ("Dining & Cafes", "want", 300.0, "coffee", "#f97316"),
        ("Shopping & Gear", "want", 250.0, "shopping-bag", "#a855f7"),
        ("Entertainment & Media", "want", 150.0, "film", "#8b5cf6"),
        ("Personal & Grooming", "want", 100.0, "scissors", "#06b6d4"),
        
        # Savings / Debt (20%)
        ("Emergency Fund", "saving", 400.0, "shield", "#14b8a6"),
        ("Investments", "saving", 350.0, "trending-up", "#10b981"),
        ("Debt Repayment", "saving", 100.0, "credit-card", "#64748b")
    ]
    cursor.executemany(
        "INSERT INTO categories (name, group_type, monthly_budget, icon, color) VALUES (?, ?, ?, ?, ?)",
        default_categories
    )
    
    # 2. Monthly Config for current month
    today = datetime.now()
    current_month_str = today.strftime("%Y-%m")
    cursor.execute(
        "INSERT OR REPLACE INTO monthly_config (month, monthly_income, needs_target_pct, wants_target_pct, savings_target_pct) VALUES (?, ?, ?, ?, ?)",
        (current_month_str, 3850.0, 50.0, 30.0, 20.0)
    )

    # 3. Savings Goals
    goals = [
        ("Emergency Buffer", 3000.0, 1850.0, (today + timedelta(days=120)).strftime("%Y-%m-%d"), "shield", "#10b981"),
        ("Next-Gen M-Series Laptop", 1600.0, 850.0, (today + timedelta(days=90)).strftime("%Y-%m-%d"), "laptop", "#6366f1"),
        ("Summer Mountain Trip", 900.0, 420.0, (today + timedelta(days=150)).strftime("%Y-%m-%d"), "compass", "#f59e0b")
    ]
    cursor.executemany(
        "INSERT INTO savings_goals (name, target_amount, current_amount, target_date, icon, color) VALUES (?, ?, ?, ?, ?, ?)",
        goals
    )

    # 4. Subscriptions
    subs = [
        ("Netflix Premium 4K", 22.99, "monthly", "Entertainment & Media", (today + timedelta(days=8)).strftime("%Y-%m-%d"), 0, "active"),
        ("Spotify Family", 16.99, "monthly", "Entertainment & Media", (today + timedelta(days=14)).strftime("%Y-%m-%d"), 0, "active"),
        ("City Gym Membership", 45.00, "monthly", "Healthcare & Meds", (today + timedelta(days=3)).strftime("%Y-%m-%d"), 1, "active"),
        ("GitHub Copilot / AI Cloud", 10.00, "monthly", "Shopping & Gear", (today + timedelta(days=19)).strftime("%Y-%m-%d"), 1, "active"),
        ("Unused Streaming Trial", 9.99, "monthly", "Entertainment & Media", (today + timedelta(days=5)).strftime("%Y-%m-%d"), 0, "review")
    ]
    cursor.executemany(
        "INSERT INTO subscriptions (name, cost, billing_cycle, category, next_due_date, is_essential, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        subs
    )

    # 5. Transactions for current month (realistic spread across days)
    transactions = [
        # Income
        (today.replace(day=1).strftime("%Y-%m-%d"), 1925.0, "income", "Salary", "Primary Employer Direct Deposit", "Bi-weekly paycheck", "Direct Deposit", 1),
        (today.replace(day=15).strftime("%Y-%m-%d"), 1925.0, "income", "Salary", "Primary Employer Direct Deposit", "Bi-weekly paycheck", "Direct Deposit", 1),
        
        # Housing & Utilities
        (today.replace(day=2).strftime("%Y-%m-%d"), 1150.0, "expense", "Housing & Rent", "Downtown Property Mgmt", "Monthly Rent", "Bank Transfer", 1),
        (today.replace(day=4).strftime("%Y-%m-%d"), 85.40, "expense", "Utilities & Bills", "Edison Power & Light", "Electricity bill", "Auto-debit", 1),
        (today.replace(day=6).strftime("%Y-%m-%d"), 65.00, "expense", "Utilities & Bills", "FiberFast Internet", "Broadband internet", "Card", 1),
        
        # Groceries
        (today.replace(day=3).strftime("%Y-%m-%d"), 112.45, "expense", "Groceries", "Trader Joe's", "Weekly fresh produce & staples", "Card", 0),
        (today.replace(day=10).strftime("%Y-%m-%d"), 88.30, "expense", "Groceries", "Whole Foods Market", "Organic veggies and proteins", "Card", 0),
        (today.replace(day=17).strftime("%Y-%m-%d"), 104.15, "expense", "Groceries", "Sprouts Farmers Market", "Mid-month grocery run", "Card", 0),
        (today.replace(day=23).strftime("%Y-%m-%d"), 65.20, "expense", "Groceries", "Target Groceries", "Pantry restock", "Card", 0),

        # Dining & Cafes
        (today.replace(day=5).strftime("%Y-%m-%d"), 14.50, "expense", "Dining & Cafes", "Blue Bottle Coffee", "Latte & pastry", "Apple Pay", 0),
        (today.replace(day=8).strftime("%Y-%m-%d"), 38.00, "expense", "Dining & Cafes", "Ramen Nagi", "Dinner with teammate", "Card", 0),
        (today.replace(day=12).strftime("%Y-%m-%d"), 18.25, "expense", "Dining & Cafes", "Chipotle Mexican Grill", "Burrito bowl lunch", "Card", 0),
        (today.replace(day=19).strftime("%Y-%m-%d"), 52.60, "expense", "Dining & Cafes", "Italian Trattoria", "Friday night dinner", "Card", 0),
        (today.replace(day=24).strftime("%Y-%m-%d"), 9.50, "expense", "Dining & Cafes", "Starbucks", "Morning iced matcha", "Apple Pay", 0),

        # Transportation
        (today.replace(day=7).strftime("%Y-%m-%d"), 48.00, "expense", "Transportation", "Chevron Gas", "Full tank refill", "Card", 0),
        (today.replace(day=14).strftime("%Y-%m-%d"), 24.50, "expense", "Transportation", "Uber Ride", "Commute to meeting", "Apple Pay", 0),
        (today.replace(day=21).strftime("%Y-%m-%d"), 46.20, "expense", "Transportation", "Shell Gas Station", "Weekly gas fill", "Card", 0),

        # Shopping
        (today.replace(day=9).strftime("%Y-%m-%d"), 49.99, "expense", "Shopping & Gear", "Amazon.com", "Desk accessories & cable organizer", "Card", 0),
        (today.replace(day=16).strftime("%Y-%m-%d"), 75.00, "expense", "Shopping & Gear", "Uniqlo", "Autumn apparel", "Card", 0),

        # Healthcare
        (today.replace(day=11).strftime("%Y-%m-%d"), 45.00, "expense", "Healthcare & Meds", "City Gym", "Gym membership", "Auto-debit", 1),
        (today.replace(day=20).strftime("%Y-%m-%d"), 25.00, "expense", "Healthcare & Meds", "CVS Pharmacy", "Vitamins & prescription", "Card", 0),

        # Savings deposits
        (today.replace(day=2).strftime("%Y-%m-%d"), 250.00, "expense", "Emergency Fund", "High Yield Savings", "Monthly emergency buffer deposit", "Transfer", 1),
        (today.replace(day=16).strftime("%Y-%m-%d"), 200.00, "expense", "Investments", "Vanguard Index ETF", "Automated S&P 500 DCA", "Transfer", 1)
    ]

    cursor.executemany(
        """
        INSERT INTO transactions (date, amount, type, category, merchant, note, payment_method, is_recurring)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        transactions
    )

    # 6. Sample affordability query
    sample_eval = (
        "Sony WH-1000XM5 Noise Cancelling Headphones",
        348.00,
        "Shopping & Gear",
        "nice_to_have",
        "Caution",
        58,
        "Purchasing this $348 item will consume 74% of your remaining Shopping budget ($470 total allocated). You will have $75 left in shopping for the remaining 6 days.",
        "Consider splitting this into 2 installments or deferring until next week's paycheck to keep your savings target protected."
    )
    cursor.execute(
        """
        INSERT INTO affordability_history (item_name, price, category, urgency, verdict, affordability_score, analysis, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_eval
    )

    conn.commit()
    conn.close()
    print("PocketSmart AI database populated with realistic seed data.")

if __name__ == "__main__":
    seed_database()
