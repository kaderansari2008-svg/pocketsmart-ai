import re
import math
import json
import os
import calendar
from datetime import datetime, timedelta
import urllib.request
import urllib.error

class PocketSmartAI:
    def __init__(self, db_conn_factory):
        self.get_db = db_conn_factory

    def get_financial_summary(self, target_month=None):
        """Calculates current month cashflow, category expenditures, and 50/30/20 metrics."""
        now = datetime.now()
        if not target_month:
            target_month = now.strftime("%Y-%m")
            
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Monthly config
        cursor.execute("SELECT * FROM monthly_config WHERE month = ?", (target_month,))
        cfg = cursor.fetchone()
        if not cfg:
            cursor.execute("SELECT * FROM monthly_config ORDER BY month DESC LIMIT 1")
            cfg = cursor.fetchone()
        
        monthly_income = cfg["monthly_income"] if cfg else 3800.0
        needs_target_pct = cfg["needs_target_pct"] if cfg else 50.0
        wants_target_pct = cfg["wants_target_pct"] if cfg else 30.0
        savings_target_pct = cfg["savings_target_pct"] if cfg else 20.0
        
        # Actual transactions in target_month
        cursor.execute("""
            SELECT type, category, SUM(amount) as total
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY type, category
        """, (target_month,))
        tx_rows = cursor.fetchall()
        
        # Categories mapping
        cursor.execute("SELECT name, group_type, monthly_budget, color FROM categories")
        cat_rows = cursor.fetchall()
        categories_meta = {c["name"]: dict(c) for c in cat_rows}
        
        total_income = 0.0
        total_expenses = 0.0
        group_spending = {"need": 0.0, "want": 0.0, "saving": 0.0}
        category_spending = {}
        
        for name, meta in categories_meta.items():
            category_spending[name] = {
                "spent": 0.0,
                "budget": meta["monthly_budget"],
                "group_type": meta["group_type"],
                "color": meta["color"],
                "remaining": meta["monthly_budget"],
                "percent_used": 0.0
            }
            
        for r in tx_rows:
            t_type = r["type"]
            cat = r["category"]
            amt = float(r["total"]) if r["total"] else 0.0
            
            if t_type == "income":
                total_income += amt
            elif t_type == "expense":
                total_expenses += amt
                if cat in category_spending:
                    category_spending[cat]["spent"] += amt
                    b = category_spending[cat]["budget"]
                    category_spending[cat]["remaining"] = b - category_spending[cat]["spent"]
                    category_spending[cat]["percent_used"] = round((category_spending[cat]["spent"] / b * 100), 1) if b > 0 else 100.0
                    g_type = category_spending[cat]["group_type"]
                    group_spending[g_type] = group_spending.get(g_type, 0.0) + amt
                else:
                    category_spending[cat] = {
                        "spent": amt,
                        "budget": 0.0,
                        "group_type": "want",
                        "color": "#94a3b8",
                        "remaining": -amt,
                        "percent_used": 100.0
                    }
                    group_spending["want"] += amt
                    
        # If no income tx logged yet, fall back to expected monthly income
        effective_income = total_income if total_income > 0 else monthly_income
        net_savings = effective_income - total_expenses
        savings_rate = round((net_savings / effective_income * 100), 1) if effective_income > 0 else 0.0
        
        # Days remaining in current month
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        days_remaining = max(1, days_in_month - now.day)
        daily_burn_rate = round(total_expenses / max(1, now.day), 2)
        projected_monthly_spend = round(daily_burn_rate * days_in_month, 2)
        
        # Calculate Financial Health Score (0 - 100)
        # Factors:
        # 1. Savings rate (ideal >= 20% -> 30 pts)
        savings_score = min(30, max(0, int(savings_rate * 1.5)))
        # 2. Budget discipline: expense vs income (ideal expense < 85% of income -> 30 pts)
        exp_ratio = total_expenses / effective_income if effective_income > 0 else 1.0
        budget_score = int(max(0, min(30, (1.0 - exp_ratio) * 60))) if exp_ratio < 1.0 else 0
        # 3. Category adherence: penalty if categories are breached (20 pts)
        over_budget_cats = sum(1 for c in category_spending.values() if c["spent"] > c["budget"] and c["budget"] > 0)
        category_score = max(5, 20 - (over_budget_cats * 5))
        # 4. 50/30/20 balance (20 pts)
        needs_pct = (group_spending["need"] / effective_income * 100) if effective_income > 0 else 50
        needs_score = 20 if needs_pct <= 55 else max(5, int(20 - (needs_pct - 55)))
        
        health_score = min(100, max(15, savings_score + budget_score + category_score + needs_score))
        
        health_status = "Excellent" if health_score >= 80 else ("Good" if health_score >= 65 else ("Fair" if health_score >= 50 else "Attention Needed"))

        conn.close()
        return {
            "month": target_month,
            "effective_income": round(effective_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate_pct": savings_rate,
            "days_remaining": days_remaining,
            "daily_burn_rate": daily_burn_rate,
            "projected_monthly_spend": projected_monthly_spend,
            "health_score": health_score,
            "health_status": health_status,
            "fifty_thirty_twenty": {
                "needs": {
                    "spent": round(group_spending["need"], 2),
                    "target_pct": needs_target_pct,
                    "actual_pct": round((group_spending["need"] / effective_income * 100), 1) if effective_income > 0 else 0,
                    "target_amount": round(effective_income * (needs_target_pct / 100), 2)
                },
                "wants": {
                    "spent": round(group_spending["want"], 2),
                    "target_pct": wants_target_pct,
                    "actual_pct": round((group_spending["want"] / effective_income * 100), 1) if effective_income > 0 else 0,
                    "target_amount": round(effective_income * (wants_target_pct / 100), 2)
                },
                "savings": {
                    "spent": round(group_spending["saving"], 2),
                    "target_pct": savings_target_pct,
                    "actual_pct": round((group_spending["saving"] / effective_income * 100), 1) if effective_income > 0 else 0,
                    "target_amount": round(effective_income * (savings_target_pct / 100), 2)
                }
            },
            "category_spending": category_spending
        }

    def evaluate_affordability(self, item_name, price, category, urgency="nice_to_have", installments=1):
        """
        The Core PocketSmart AI Recommendation Evaluator:
        Assesses if the user can safely afford a proposed purchase based on real cashflow,
        category headroom, burn rate, and days left in the billing cycle.
        """
        try:
            price = float(price)
            installments = max(1, int(installments))
        except (ValueError, TypeError):
            return {"error": "Invalid price or installment count"}
            
        summary = self.get_financial_summary()
        effective_income = summary["effective_income"]
        total_expenses = summary["total_expenses"]
        net_savings = summary["net_savings"]
        days_remaining = summary["days_remaining"]
        category_spending = summary["category_spending"]
        
        # Monthly impact if split over installments
        monthly_cost = round(price / installments, 2)
        
        cat_info = category_spending.get(category, {
            "spent": 0.0,
            "budget": 200.0,
            "group_type": "want",
            "remaining": 200.0
        })
        cat_remaining = cat_info["remaining"]
        cat_budget = cat_info["budget"]
        
        # Scoring logic (0 to 100)
        # Base starts at 100
        score = 100
        reasons = []
        recommendations = []
        alternatives = []
        
        # 1. Total Liquidity / Cashflow Check
        if monthly_cost > net_savings:
            deficit = monthly_cost - net_savings
            score -= 45
            reasons.append(f"Exceeds your current monthly surplus by ${deficit:.2f}.")
        elif monthly_cost > (net_savings * 0.7):
            score -= 20
            reasons.append("Consumes over 70% of your remaining uncommitted savings buffer.")
        else:
            reasons.append(f"Fits within your projected monthly surplus (${net_savings:.2f} available).")
            
        # 2. Category Budget Headroom Check
        if monthly_cost > cat_remaining:
            cat_over = monthly_cost - cat_remaining
            score -= 30
            reasons.append(f"Exceeds remaining '{category}' category budget by ${cat_over:.2f}.")
        elif cat_budget > 0 and (monthly_cost / cat_budget) > 0.5:
            score -= 15
            reasons.append(f"Consumes more than 50% of the entire monthly '{category}' allowance.")
        else:
            reasons.append(f"Category '{category}' has sufficient room (${cat_remaining:.2f} left).")

        # 3. Urgency Weighting
        if urgency == "essential_need":
            score = min(100, score + 15)
            reasons.append("Flagged as an Essential Need: given priority consideration.")
        elif urgency == "impulse_want":
            score = max(0, score - 15)
            reasons.append("Flagged as an Impulse Want: subject to strict cooling-off evaluation.")
        else:
            reasons.append("Nice-to-Have purchase: evaluated against discretionary balance.")
            
        # 4. Billing Cycle Timing
        if days_remaining > 15 and monthly_cost > (net_savings * 0.5):
            score -= 10
            reasons.append(f"{days_remaining} days left until next month's refresh; front-loading spending raises mid-month cash crunch risk.")
            
        score = max(5, min(98, score))
        
        # Verdict Determination
        if score >= 75:
            verdict = "Safe to Buy"
            verdict_badge = "success"
            summary_sentence = f"Yes, you can comfortably afford the {item_name}!"
            recommendations.append("Your cashflow and category limits support this purchase without jeopardizing your savings.")
            recommendations.append("Tip: Pay in full rather than taking on interest-bearing financing.")
        elif score >= 50:
            verdict = "Caution / Stretch"
            verdict_badge = "warning"
            summary_sentence = f"You can afford the {item_name}, but it will stretch your discretionary funds."
            recommendations.append(f"Wait {min(days_remaining, 14)} days until the next billing cycle to avoid budget deficit.")
            tradeoff_amt = round(monthly_cost * 0.4, 2)
            recommendations.append(f"Trade-off: Temporarily reduce Dining & Cafes by ${tradeoff_amt:.2f} to offset this purchase.")
            alternatives.append(f"Consider looking for certified refurbished, open-box, or waiting for seasonal promotions.")
        else:
            verdict = "High Risk / Not Recommended"
            verdict_badge = "danger"
            summary_sentence = f"PocketSmart AI advises against purchasing the {item_name} right now."
            recommendations.append("This purchase will trigger a deficit in your monthly budget and eat into emergency reserves.")
            weekly_save = max(20.0, round(price / 6, 2))
            recommendations.append(f"Smart Goal: Create a dedicated savings bucket and set aside ${weekly_save:.2f}/week for 6 weeks.")
            alternatives.append("Explore high-value budget alternatives or defer this until your next bonus/income boost.")
            
        # Save to database log
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO affordability_history 
            (item_name, price, category, urgency, verdict, affordability_score, analysis, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_name, price, category, urgency, verdict, score,
            " ".join(reasons),
            " | ".join(recommendations)
        ))
        conn.commit()
        conn.close()
        
        return {
            "item_name": item_name,
            "price": price,
            "category": category,
            "urgency": urgency,
            "installments": installments,
            "monthly_cost": monthly_cost,
            "score": score,
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "summary_sentence": summary_sentence,
            "reasons": reasons,
            "recommendations": recommendations,
            "alternatives": alternatives,
            "budget_context": {
                "monthly_surplus": round(net_savings, 2),
                "category_remaining": round(cat_remaining, 2),
                "category_budget": round(cat_budget, 2),
                "days_remaining": days_remaining
            }
        }

    def parse_natural_language_expense(self, text):
        """
        Parses informal natural language or speech transcript into structured transaction:
        e.g. "Spent $45 on gas at Chevron yesterday"
             "Dinner at Ramen Nagi 38.50"
             "Salary deposit $2500"
        """
        text_lower = text.lower().strip()
        now = datetime.now()
        
        # 1. Detect Type (Income vs Expense)
        is_income = bool(re.search(r'\b(salary|paycheck|income|deposit|received|earned|got paid|stipend|bonus)\b', text_lower))
        tx_type = "income" if is_income else "expense"
        
        # 2. Extract Amount
        # matches $45, $45.50, 45 dollars, 45.50
        amount = 0.0
        amount_matches = re.findall(r'(?:\$|\bUSD\s*)?([0-9]+(?:[\.,][0-9]{1,2})?)\s*(?:dollars|bucks|\$)?', text, re.IGNORECASE)
        if amount_matches:
            # pick the most plausible monetary value
            for m in amount_matches:
                try:
                    val = float(m.replace(",", "."))
                    if val > 0:
                        amount = val
                        break
                except ValueError:
                    continue

        # 3. Categorization heuristic
        category = "Shopping & Gear" if not is_income else "Salary"
        cat_keywords = {
            "Groceries": ["grocery", "groceries", "supermarket", "trader joe", "whole foods", "safeway", "walmart", "target grocery", "sprouts", "costco", "aldi", "food shopping", "produce"],
            "Dining & Cafes": ["lunch", "dinner", "breakfast", "brunch", "coffee", "cafe", "starbucks", "latte", "chipotle", "restaurant", "burger", "pizza", "ramen", "bar", "drinks", "takeout", "doordash", "ubereats"],
            "Housing & Rent": ["rent", "mortgage", "lease", "apartment", "landlord", "hoa"],
            "Utilities & Bills": ["electric", "electricity", "water bill", "gas bill", "utility", "utilities", "wifi", "internet", "broadband", "power", "edison", "phone bill"],
            "Transportation": ["gas", "fuel", "chevron", "shell", "uber", "lyft", "metro", "subway", "train", "parking", "toll", "bus", "cab", "petrol"],
            "Healthcare & Meds": ["gym", "pharmacy", "medicine", "doctor", "dentist", "cvs", "walgreens", "hospital", "clinic", "health", "vitamin"],
            "Entertainment & Media": ["movie", "cinema", "netflix", "spotify", "hulu", "steam", "game", "concert", "theatre", "disney", "youtube premium"],
            "Investments": ["stocks", "etf", "vanguard", "crypto", "bitcoin", "investment", "shares", "roth ira", "401k"],
            "Emergency Fund": ["emergency fund", "savings buffer", "rainy day"]
        }
        
        for cat_name, keywords in cat_keywords.items():
            if any(k in text_lower for k in keywords):
                category = cat_name
                break
                
        # 4. Extract Merchant / Note
        merchant = ""
        # Priority 1: Explicit "at <Merchant>" or "from <Merchant>" (e.g. at Chipotle, from Apple)
        at_match = re.search(r'\b(?:at|from)\s+([A-Za-z0-9\'\.\-\s]+?)(?:\s+(?:yesterday|today|last night|\$[0-9]|\bfor\b)|$)', text, re.IGNORECASE)
        if at_match:
            merchant = at_match.group(1).strip()
        else:
            # Priority 2: "on <Merchant>" or "to <Merchant>" or "for <Merchant>"
            fallback_match = re.search(r'\b(?:on|to|for)\s+([A-Za-z0-9\'\.\-\s]+?)(?:\s+(?:yesterday|today|last night|\$[0-9])|$)', text, re.IGNORECASE)
            if fallback_match:
                merchant = fallback_match.group(1).strip()
                
        # Clean common prefixes/suffixes
        if merchant:
            merchant = re.sub(r'^(the|a|an)\s+', '', merchant, flags=re.IGNORECASE)
            merchant = re.sub(r'\s+(for|at|on|with|in)$', '', merchant, flags=re.IGNORECASE).strip()
            merchant = re.sub(r'\s+(yesterday|today|last night)$', '', merchant, flags=re.IGNORECASE).strip()
            merchant = re.sub(r'\s+(for|at|on|with|in)$', '', merchant, flags=re.IGNORECASE).strip()
        
        if not merchant or len(merchant) < 2:
            merchant = category
            
        # 5. Extract Date
        date_str = now.strftime("%Y-%m-%d")
        if "yesterday" in text_lower:
            date_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "2 days ago" in text_lower:
            date_str = (now - timedelta(days=2)).strftime("%Y-%m-%d")
            
        return {
            "raw_text": text,
            "type": tx_type,
            "amount": amount,
            "category": category,
            "merchant": merchant[:40] if merchant else category,
            "date": date_str,
            "note": text.strip()
        }

    def chat_advisory(self, user_message, api_key=None):
        """
        PocketSmart AI Conversational Financial Co-Pilot:
        Uses context-grounded financial intelligence based on actual database numbers.
        If Gemini API key is supplied, enhances with Gemini Generative AI.
        """
        summary = self.get_financial_summary()
        
        # Try Gemini API if key is available
        gemini_key = api_key or os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                prompt_content = f"""
You are PocketSmart AI, an empathetic, sharp, and highly practical personal finance co-pilot and budgeting advisor.
Here is the user's real-time financial state for this month:
- Effective Income: ${summary['effective_income']}
- Total Expenses: ${summary['total_expenses']}
- Net Savings: ${summary['net_savings']} (Savings Rate: {summary['savings_rate_pct']}%)
- Days Remaining in Month: {summary['days_remaining']}
- Daily Burn Rate: ${summary['daily_burn_rate']}
- Financial Health Score: {summary['health_score']}/100 ({summary['health_status']})
- 50/30/20 Rule:
  * Needs: {summary['fifty_thirty_twenty']['needs']['actual_pct']}% (Target: {summary['fifty_thirty_twenty']['needs']['target_pct']}%)
  * Wants: {summary['fifty_thirty_twenty']['wants']['actual_pct']}% (Target: {summary['fifty_thirty_twenty']['wants']['target_pct']}%)
  * Savings: {summary['fifty_thirty_twenty']['savings']['actual_pct']}% (Target: {summary['fifty_thirty_twenty']['savings']['target_pct']}%)
- Category Spending: {json.dumps({k: {'spent': v['spent'], 'budget': v['budget']} for k, v in summary['category_spending'].items()})}

User Question: "{user_message}"

Respond concisely, clearly, with exact numbers, encouraging tone, and 2-3 specific, actionable bullet points. Use markdown.
"""
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                req_data = json.dumps({"contents": [{"parts": [{"text": prompt_content}]}]}).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8) as res:
                    res_body = json.loads(res.read().decode("utf-8"))
                    text = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    return {"reply": text, "engine": "gemini-1.5-flash"}
            except Exception as e:
                # Fallback to local heuristic engine
                pass
                
        # Smart Built-in Contextual Advisor
        q = user_message.lower()
        surplus = summary["net_savings"]
        score = summary["health_score"]
        rate = summary["savings_rate_pct"]
        needs = summary["fifty_thirty_twenty"]["needs"]["actual_pct"]
        wants = summary["fifty_thirty_twenty"]["wants"]["actual_pct"]
        
        # Check over-budget categories
        over_budget = [k for k, v in summary["category_spending"].items() if v["spent"] > v["budget"] and v["budget"] > 0]
        
        if "save" in q or "saving" in q or "cut" in q:
            reply = f"""### 💡 PocketSmart AI Savings Blueprint

Here is how you can boost your savings right now:
* **Current Surplus:** You currently have **${surplus:.2f}** remaining in unspent income this month (Savings rate: **{rate}%**).
* **Category Leaks:** {'You have exceeded limits in ' + ', '.join(over_budget) if over_budget else 'Your core categories are well contained'}.
* **Action Step 1:** Audit recurring entertainment & dining subscriptions to trim at least **$40–$60** before next month.
* **Action Step 2:** Aim to bank your surplus into your High-Yield Emergency Buffer before discretionary shopping.
"""
        elif "50/30/20" in q or "rule" in q or "ratio" in q:
            reply = f"""### 📊 50/30/20 Rule Breakdown

Here is your current distribution vs the golden benchmark:
* **Needs (Target 50%):** You are at **{needs}%**. {'✅ On track!' if needs <= 52 else '⚠️ A bit high—review essential bills.'}
* **Wants (Target 30%):** You are at **{wants}%**. {'✅ Controlled spending!' if wants <= 30 else '⚠️ Over the 30% ceiling—cap dining and lifestyle expenses.'}
* **Savings & Investments (Target 20%):** You are at **{rate}%**.

**Recommendation:** {'You are in strong financial shape!' if score >= 75 else 'Shift 5% of discretionary spending into your automated savings bucket.'}
"""
        elif "afford" in q or "buy" in q or "purchase" in q:
            reply = f"""### 🛍️ Purchase Guidance

Use the **"Can I Afford This?"** evaluator in the top tab to run an instant affordability simulation.
* You have **${surplus:.2f}** in discretionary cashflow remaining.
* **{summary['days_remaining']} days** remain until your budget resets.
* If your intended purchase is above **${(surplus * 0.4):.2f}**, PocketSmart recommends spreading the purchase or deferring to next month.
"""
        elif "health" in q or "score" in q or "status" in q:
            reply = f"""### 🛡️ Financial Health Status: {summary['health_status']} ({score}/100)

* **Daily Burn Rate:** You are spending an average of **${summary['daily_burn_rate']}/day**.
* **Projected End of Month Spend:** **${summary['projected_monthly_spend']:.2f}**.
* **Key Strength:** Consistent income deposits and active savings allocations.
* **Target Improvement:** Keep unbudgeted impulse spending under $50 for the remainder of this cycle.
"""
        else:
            reply = f"""### 🤖 PocketSmart AI Co-Pilot

Here is a quick snapshot of your finances:
* **Monthly Income:** ${summary['effective_income']:.2f}
* **Total Spent:** ${summary['total_expenses']:.2f} | **Available Surplus:** ${surplus:.2f}
* **Health Score:** **{score}/100** ({summary['health_status']})

You can ask me anything about your budget, test potential purchases, or log expenses with voice and natural language!
"""
        return {"reply": reply, "engine": "pocketsmart-heuristic-ai"}
