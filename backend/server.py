import os
import sys
import json
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Local imports
from database import get_db, init_db
from seed_data import seed_database
from ai_engine import PocketSmartAI

PORT = int(os.environ.get("PORT", 8080))
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

ai_engine = PocketSmartAI(get_db)

class PocketSmartHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def read_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # 1. API routes
        if path == "/api/summary":
            target_month = params.get("month", [None])[0]
            summary = ai_engine.get_financial_summary(target_month)
            return self.send_json(summary)

        elif path == "/api/transactions":
            conn = get_db()
            cursor = conn.cursor()
            query = "SELECT * FROM transactions ORDER BY date DESC, id DESC"
            cursor.execute(query)
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self.send_json({"transactions": rows})

        elif path == "/api/categories":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY group_type, name")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self.send_json({"categories": rows})

        elif path == "/api/savings-goals":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM savings_goals ORDER BY target_date ASC, id ASC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self.send_json({"goals": rows})

        elif path == "/api/subscriptions":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subscriptions ORDER BY cost DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            
            # calculate total annual leakage
            annual_total = 0.0
            for s in rows:
                if s["status"] != "cancelled":
                    cost = float(s["cost"])
                    annual_total += (cost * 12) if s["billing_cycle"] == "monthly" else cost
                    
            return self.send_json({
                "subscriptions": rows,
                "annual_leakage": round(annual_total, 2),
                "monthly_leakage": round(annual_total / 12, 2)
            })

        elif path == "/api/affordability/history":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM affordability_history ORDER BY id DESC LIMIT 15")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self.send_json({"history": rows})

        # 2. Static file serving
        clean_path = path.lstrip("/")
        if not clean_path:
            clean_path = "index.html"
            
        file_path = os.path.abspath(os.path.join(FRONTEND_DIR, clean_path))
        if not file_path.startswith(FRONTEND_DIR) or not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(FRONTEND_DIR, "index.html")

        if os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        # 1. Affordability Evaluation
        if path == "/api/affordability":
            item_name = body.get("item_name", "Desired Item")
            price = body.get("price", 0.0)
            category = body.get("category", "Shopping & Gear")
            urgency = body.get("urgency", "nice_to_have")
            installments = body.get("installments", 1)
            
            result = ai_engine.evaluate_affordability(item_name, price, category, urgency, installments)
            return self.send_json(result)

        # 2. Natural Language Expense Parser
        elif path == "/api/parse-nl":
            text = body.get("text", "")
            parsed_data = ai_engine.parse_natural_language_expense(text)
            return self.send_json(parsed_data)

        # 3. Add Transaction
        elif path == "/api/transactions":
            date_str = body.get("date", datetime.now().strftime("%Y-%m-%d"))
            amount = float(body.get("amount", 0.0))
            tx_type = body.get("type", "expense")
            category = body.get("category", "Uncategorized")
            merchant = body.get("merchant", "")
            note = body.get("note", "")
            payment_method = body.get("payment_method", "Card")
            is_recurring = 1 if body.get("is_recurring") else 0
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (date, amount, type, category, merchant, note, payment_method, is_recurring)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, amount, tx_type, category, merchant, note, payment_method, is_recurring))
            tx_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return self.send_json({"success": True, "id": tx_id, "message": "Transaction recorded"})

        # 4. Add/Update Savings Goal
        elif path == "/api/savings-goals":
            name = body.get("name", "New Goal")
            target_amount = float(body.get("target_amount", 1000.0))
            current_amount = float(body.get("current_amount", 0.0))
            target_date = body.get("target_date", "")
            icon = body.get("icon", "target")
            color = body.get("color", "#10b981")
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO savings_goals (name, target_amount, current_amount, target_date, icon, color)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, target_amount, current_amount, target_date, icon, color))
            goal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return self.send_json({"success": True, "id": goal_id})

        # 5. Contribute / Update Goal Amount
        elif path.startswith("/api/savings-goals/") and path.endswith("/contribute"):
            try:
                goal_id = int(path.split("/")[3])
                delta = float(body.get("amount", 0.0))
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE savings_goals SET current_amount = MAX(0, current_amount + ?) WHERE id = ?", (delta, goal_id))
                conn.commit()
                conn.close()
                return self.send_json({"success": True, "message": "Goal updated"})
            except Exception as e:
                return self.send_json({"error": str(e)}, 400)

        # 6. Add Subscription
        elif path == "/api/subscriptions":
            name = body.get("name", "New Subscription")
            cost = float(body.get("cost", 9.99))
            billing_cycle = body.get("billing_cycle", "monthly")
            category = body.get("category", "Entertainment & Media")
            next_due = body.get("next_due_date", datetime.now().strftime("%Y-%m-%d"))
            status = body.get("status", "active")
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO subscriptions (name, cost, billing_cycle, category, next_due_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, cost, billing_cycle, category, next_due, status))
            sub_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return self.send_json({"success": True, "id": sub_id})

        # 7. AI Chat Advisory
        elif path == "/api/chat":
            message = body.get("message", "")
            api_key = body.get("api_key", None)
            res = ai_engine.chat_advisory(message, api_key)
            return self.send_json(res)

        # 8. Reset to sample seed data
        elif path == "/api/reset-data":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS transactions")
            cursor.execute("DROP TABLE IF EXISTS categories")
            cursor.execute("DROP TABLE IF EXISTS monthly_config")
            cursor.execute("DROP TABLE IF EXISTS savings_goals")
            cursor.execute("DROP TABLE IF EXISTS subscriptions")
            cursor.execute("DROP TABLE IF EXISTS affordability_history")
            conn.commit()
            conn.close()
            init_db()
            seed_database()
            return self.send_json({"success": True, "message": "Demo data reset successfully"})

        else:
            self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/transactions/"):
            try:
                tx_id = int(path.split("/")[3])
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
                conn.commit()
                conn.close()
                return self.send_json({"success": True, "deleted_id": tx_id})
            except Exception as e:
                return self.send_json({"error": str(e)}, 400)
                
        elif path.startswith("/api/subscriptions/"):
            try:
                sub_id = int(path.split("/")[3])
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM subscriptions WHERE id = ?", (sub_id,))
                conn.commit()
                conn.close()
                return self.send_json({"success": True, "deleted_id": sub_id})
            except Exception as e:
                return self.send_json({"error": str(e)}, 400)
                
        else:
            self.send_error(404, "Endpoint not found")

def run(port=PORT):
    init_db()
    seed_database()
    server_address = ("", port)
    httpd = HTTPServer(server_address, PocketSmartHandler)
    print(f"🚀 PocketSmart AI Server running at http://localhost:{port}/")
    print(f"📁 Serving frontend from {FRONTEND_DIR}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port)
