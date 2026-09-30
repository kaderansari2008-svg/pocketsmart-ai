# PocketSmart AI: Your Smart Budget & Recommendation Assistant

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![AI Architecture: Heuristic + Gemini](https://img.shields.io/badge/AI-Heuristic%20%2B%20Gemini%20API-indigo.svg)](#ai-engine)

> **Analyzed from YouTube Video:** [`https://youtu.be/Rpcn0WkDLEo`](https://youtu.be/Rpcn0WkDLEo)  
> **Original Project Showcase:** *PocketSmart AI: Your Smart Budget & Recommendation Assistant* by **Chikka Prathibha**

---

## 📌 Project Overview

**PocketSmart AI** is an intelligent personal finance co-pilot and automated recommendation platform designed to transform how individuals manage budgets, evaluate discretionary purchases, and optimize cashflow.

Instead of passive retroactive accounting, PocketSmart AI acts as a **proactive financial companion**:
1. **Evaluates purchase decisions before money is spent** using the *"Can I Afford This?"* AI Recommendation Engine.
2. **Eliminates manual bookkeeping friction** with natural language parsing and hands-free voice logging.
3. **Keeps spending aligned with the 50/30/20 Rule** (50% Needs, 30% Wants, 20% Savings).
4. **Hunts down recurring subscription drain** to safeguard wealth accumulation.
5. **Provides on-demand conversational financial advice** grounded in actual, real-time database transactions.

---

## 🚀 Key Features & Modules

### 1. 🛍️ Smart "Can I Afford This?" AI Recommendation Assistant
- **Real-Time Purchase Evaluator:** Input an item name (e.g. *Sony Headphones*, *Weekend Trip*), price, category, urgency (*Essential Need*, *Nice-to-Have*, *Impulse Want*), and payment strategy (lump-sum vs. installments).
- **Multi-Factor Affordability Score (0–100):** Cross-references current remaining monthly surplus, category budget headroom, days left in billing cycle, and emergency buffer impact.
- **Actionable AI Verdicts:**
  - 🟢 **Safe to Buy (Guilt-Free):** Low impact, discretionary cashflow supports the purchase.
  - 🟡 **Caution / Stretch:** Consumes significant category headroom; recommends cooling off or offsetting against other discretionary categories.
  - 🔴 **High Risk / Not Recommended:** Would trigger an overdraft or erode emergency reserves; automatically calculates a weekly saving timeline and suggests budget alternatives.
- **1-Click Conversion:** Turn evaluated items directly into an expense or automatically spawn a **Target Savings Goal**.

### 2. 📊 50 / 30 / 20 Budget Tracker & Category Analytics
- **Dynamic Rule Monitoring:** Tracks live percentage distribution:
  - **50% Needs:** Housing, utilities, groceries, healthcare, transit.
  - **30% Wants:** Dining out, entertainment, shopping, personal care.
  - **20% Savings:** Emergency fund buffer, investment dollar-cost averaging, debt reduction.
- **Financial Health Index (FHI):** 0–100 live composite score with status badges (*Excellent*, *Strong*, *Moderate*, *Attention Needed*).
- **Daily Spend Velocity & Burn Rate:** Forecasts end-of-month projected balance and alerts you before budget breaches happen.

### 3. 🎙️ Natural Language & Voice Transaction Logger
- **Web Speech API Integration:** Tap the microphone and speak naturally (e.g. *"Spent 35 dollars on dinner at Chipotle"*).
- **Smart Regex & Semantic Extractor:** Automatically extracts amount, transaction type (*expense* vs. *income*), category mapping, merchant name, and date.
- **Interactive Review:** Instant pre-filled modal for 1-click confirmation.

### 4. 🤖 PocketSmart AI Financial Co-Pilot (Chat Advisor)
- **Context-Grounded Financial Advice:** Evaluates real numbers from your SQLite database.
- **Dual Engine Architecture:**
  - **Built-in Financial Heuristic Engine:** Fast, zero-configuration offline advisor with tailored tips.
  - **Google Gemini 1.5 Flash Integration:** Connect your Gemini API key anytime for deep multimodal reasoning and conversational synthesis.
- **Quick-Prompt Chips:** Pre-built financial analysis queries (e.g. *"How can I save $200 more this month?"*, *"Audit my subscriptions"*).

### 5. 🎯 Savings Goals & 🔍 Subscription Leakage Hunter
- **Milestone Tracker:** Set targets (emergency buffer, laptop, vacation) with progress bars, visual completion percentage, and quick deposit/withdraw controls.
- **Annual Subscription Drain Calculator:** Aggregates recurring monthly and annual software, media, and fitness subscriptions to highlight unused leakages.

---

## 🏗️ Architecture & Technology Stack

```
pocketsmart-ai/
├── backend/
│   ├── server.py        # High-performance HTTP REST API & static file server
│   ├── database.py      # SQLite schema (Categories, Transactions, Goals, Subs, History)
│   ├── ai_engine.py     # Affordability Engine, NL Parser, FHI Calculator & AI Chat
│   ├── seed_data.py     # Realistic demo dataset generator
│   └── pocketsmart.db   # Persistent SQLite database
├── frontend/
│   ├── index.html       # Responsive, semantic single-page application
│   ├── styles.css       # Glassmorphism design system (Dark/Light themes)
│   └── app.js           # Client controller, Web Speech API & reactive state
├── requirements.txt     # Python dependency documentation
├── run.sh               # One-click startup script
└── README.md            # Complete documentation
```

- **Backend:** Python 3 (Standard Library: `http.server`, `sqlite3`, `json`, `urllib`, `re`) — **Zero mandatory external dependencies!**
- **Frontend:** HTML5, CSS3 Custom Properties (Dark/Light theme toggle), Vanilla JavaScript ES6+, Web Speech API, Glassmorphism UI.
- **AI / LLM:** Hybrid Context Engine + Google Gemini API (`gemini-1.5-flash`).

---

## ⚡ Quick Start Guide

### 🚀 Running in Visual Studio Code (Recommended)
1. Open this repository folder in **VS Code**: `File > Open Folder...`
2. Press **`F5`** (or click the green Play button in the top right / Run & Debug menu).
3. VS Code will automatically start `main.py` and open your default browser directly at **`http://localhost:8080/`**!

### 💻 Running from Terminal
Run the primary entrypoint:
```bash
python3 main.py
```
*(Or use `python3 main.py --no-browser` to run headlessly, or `python3 main.py 8081` to pick a custom port)*

---

## 🎬 2-Minute Demo Video Recording Guide

When recording your presentation or demo video (e.g., using Loom, OBS, or QuickTime Screen Recording), follow this high-impact walkthrough:

| Timestamp | Screen / Action | Voiceover / Talking Point |
| :--- | :--- | :--- |
| **0:00 - 0:25** | **Dashboard View** | *"Welcome to PocketSmart AI — an intelligent budget and recommendation assistant. Unlike static budgeting apps, PocketSmart AI proactively guides your financial health using the 50/30/20 rule, real-time burn-rate forecasting, and smart purchase evaluation."* |
| **0:25 - 0:55** | **"Can I Afford This?" Evaluator** | *"Here is the hero feature: 'Can I Afford This?'. Before buying a $350 pair of Sony Headphones, PocketSmart analyzes my real-time discretionary surplus, remaining days, and emergency buffer. Let's click 'Evaluate Affordability'. PocketSmart AI immediately returns an 85/100 score with a 'Safe to Buy' verdict and instant saving strategies."* |
| **0:55 - 1:20** | **Voice & Natural Language Logging** | *"Expense tracking is zero-friction. Watch me click the microphone or type in natural English: 'Spent 28 dollars on Uber rides'. PocketSmart automatically categorizes it under Transit, parses the exact dollar amount, and logs it with one click."* |
| **1:20 - 1:45** | **AI Financial Co-Pilot (Chat)** | *"Need personalized advice? Open the AI Financial Advisor. Clicking 'How can I save $200 more this month?' immediately analyzes my subscriptions and category spending to generate an actionable savings breakdown."* |
| **1:45 - 2:00** | **Wrap Up & Architecture** | *"PocketSmart AI is built with clean Python standard library architecture, zero mandatory external dependencies, and an interactive glassmorphism UI. Thank you!"* |

---

## 🌐 Live Deployments & Repository
- **GitHub Repository:** [https://github.com/kaderansari2008-svg/pocketsmart-ai](https://github.com/kaderansari2008-svg/pocketsmart-ai)
- **Live Preview (GitHub Pages):** [https://kaderansari2008-svg.github.io/pocketsmart-ai/](https://kaderansari2008-svg.github.io/pocketsmart-ai/)

---

## 🛡️ License
MIT License. Open-source educational and personal finance assistant.

