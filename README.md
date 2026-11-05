# 🛍️ Customer Review Intelligence & Support Dashboard


> An end-to-end review intelligence engine and automated triage dashboard designed for modern e-commerce stores. It continuously ingests customer feedback, applies rule-based NLP sentiment analysis, isolates critical failure domains (shipping, damage, quality, support), and automatically flags urgent issues to prevent chargebacks and customer churn.

---

## 📑 Table of Contents
- [The Problem & The Solution](#-the-problem--the-solution)
- [System Architecture & Workflow](#-system-architecture--workflow)
- [Key Features](#-key-features)
- [Triage & Logic Engine](#-triage--logic-engine)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)

---

## 💡 The Problem & The Solution

* **The Problem:** High-volume e-commerce storefronts receive hundreds of buyer reviews weekly. Escalated complaints (such as broken items, weeks of delivery delays, or unhelpful support) frequently get lost beneath positive 5-star reviews, leading to credit card chargebacks, negative brand sentiment, and lost customers.
* **The Solution:** This project bridges customer feedback and support operations. Incoming reviews are automatically ingested via REST API, analyzed for sentiment, scanned for operational pain points, and assigned a triage priority level (`URGENT`, `HIGH`, `NORMAL`, `LOW`) with real-time visual alerts on a store operator dashboard.

---

## 🏗️ System Architecture & Workflow

```text
  [ Buyer Submits Review ]
              │
              ▼
   [ Streamlit / Storefront ] ──( HTTP POST /api/reviews )──► [ FastAPI Backend (main.py) ]
                                                                      │
                                   ┌──────────────────────────────────┴──────────────────────────────────┐
                                   ▼                                                                     ▼
                        [ VADER Sentiment Analyzer ]                                          [ Pain-Point Engine ]
                      Compound Score: POS / NEU / NEG                                   SHIPPING | DAMAGED | QUALITY | SERVICE
                                   └──────────────────────────────────┬──────────────────────────────────┘
                                                                      ▼
                                                          [ Priority Triage Matrix ]
                                                          (URGENT / HIGH / NORMAL / LOW)
                                                                      │
                                                                      ▼
                                                       [ SQLite DB (database.py) ]
                                                            WAL Mode Storage
                                                                      │
                                                                      ▼
                                                      [ Streamlit Live Dashboard ]
                                                      • KPI Metric Cards
                                                      • Chargeback Alerts
                                                      • Sentiment & Product Charts
                                                      • Historical Data Table
```

---

## ✨ Key Features

1. **Automated Sentiment Analysis**: Utilizes VADER (Valence Aware Dictionary and sEntiment Reasoner) to compute sentiment polarity scores (`compound > 0.05` = POSITIVE, `compound < -0.05` = NEGATIVE, otherwise NEUTRAL).
2. **Domain-Specific Pain Point Detection**: Detects keywords across 4 critical retail failure categories:
   - 🚚 **SHIPPING**: Delivery delays, missing parcels, tracking errors.
   - 💥 **DAMAGED**: Broken components, cracked casings, crushed packaging.
   - ⚠️ **QUALITY**: Flimsy builds, fake goods, defective parts, poor materials.
   - 🎧 **SERVICE**: Unresponsive support, refund disputes, rude representatives.
3. **Automated Escalation & Triage**: Computes priority levels and triggers immediate high-visibility banner warnings for `URGENT` tickets to prevent customer churn.
4. **Live Store Analytics Dashboard**:
   - **Storefront Simulator:** Test submissions directly within the UI.
   - **Key KPI Counters:** Total Reviews, Negative Review Rate (%), Urgent Complaints, Satisfied Buyers.
   - **Interactive Visualizations:** Sentiment breakdown and product-specific complaint charts.
   - **Searchable History Table:** Sort and filter all past customer feedback.
5. **High-Performance Backend**: Built with FastAPI and Pydantic validation, featuring automatic interactive Swagger docs.
6. **Concurrent Database Layer**: SQLite database configured with **WAL (Write-Ahead Logging)** mode for simultaneous read/write operations without table locking, plus automatic seed data on initialization.

---

## 🧠 Triage & Logic Engine

The triage logic in `main.py` classifies reviews into four distinct escalation tiers:

| Priority | Criteria | Recommended Store Action |
| :--- | :--- | :--- |
| 🚨 **URGENT** | Rating $\le 2$ **OR** (Negative Sentiment AND $\ge 2$ Pain Points) | Immediate manager reach-out within 1 hour to prevent chargeback. |
| 🔴 **HIGH** | Negative Sentiment (Rating $> 2$ or $< 2$ pain points) | Standard support ticket creation for resolution. |
| 🟡 **NORMAL** | Neutral Sentiment with average rating | Logged for routine feedback review. |
| 🟢 **LOW** | Positive Sentiment or Star Rating $\ge 4$ | Eligible for automated testimonial marketing. |

---


## 📁 Project Structure

```text
Customer Review Intelligence/
├── app.py              # Streamlit dashboard & storefront simulator UI
├── main.py             # FastAPI backend, VADER analysis & triage engine
├── database.py         # SQLite connection, WAL mode configuration & CRUD operations
├── requirements.txt    # Python package dependencies
├── .gitignore          # Git exclusion rules (venv, database, cache)
└── README.md           # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.9+** and **pip** installed:
```bash
python3 --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd "Customer Review Intelligence"
```

### 3. Create & Activate Virtual Environment
```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

The system requires both the backend API and the frontend dashboard to run concurrently.

### Terminal 1: Start the FastAPI Backend
```bash
uvicorn main:app --reload --port 8000
```
* **API Endpoint:** `http://127.0.0.1:8000`
* **Swagger Documentation:** `http://127.0.0.1:8000/docs`
* **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

### Terminal 2: Start the Streamlit Dashboard
```bash
streamlit run app.py
```
* **Dashboard URL:** `http://localhost:8501`

---

## 🔌 API Reference

### 1. Submit and Analyze a Review
`POST /api/reviews`

**Request Headers:** `Content-Type: application/json`

**Request Body:**
```json
{
  "customer": "customer@example.com",
  "product": "Wireless Noise-Canceling Headphones",
  "rating": 1,
  "review": "The package arrived 2 weeks late and the plastic was broken! Customer support ignored my emails."
}
```

**Response (`200 OK`):**
```json
{
  "id": 4,
  "date": "2026-11-05 20:30",
  "customer": "customer@example.com",
  "product": "Wireless Noise-Canceling Headphones",
  "rating": 1,
  "review": "The package arrived 2 weeks late and the plastic was broken! Customer support ignored my emails.",
  "sentiment": "NEGATIVE",
  "pain_points": [
    "SHIPPING",
    "DAMAGED",
    "SERVICE"
  ],
  "priority": "URGENT"
}
```

---

### 2. Retrieve All Reviews
`GET /api/reviews`

**Response (`200 OK`):**
Returns a list of all reviews saved in the database, ordered from newest to oldest:
```json
[
  {
    "id": 4,
    "date": "2026-11-05 20:30",
    "customer": "customer@example.com",
    "product": "Wireless Noise-Canceling Headphones",
    "rating": 1,
    "review": "The package arrived 2 weeks late and the plastic was broken! Customer support ignored my emails.",
    "sentiment": "NEGATIVE",
    "pain_points": ["SHIPPING", "DAMAGED", "SERVICE"],
    "priority": "URGENT"
  }
]
```

---

## 🗄️ Database Schema

The database uses SQLite (`reviews.db`) with `PRAGMA journal_mode=WAL;` for non-blocking concurrent reads and writes.

```sql
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    customer TEXT NOT NULL,
    product TEXT NOT NULL,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    pain_points TEXT NOT NULL,   -- Stored as JSON serialized text
    priority TEXT NOT NULL
);
```

> **Note:** When the application runs for the first time, `database.py` automatically initializes the table and populates sample starter reviews if the database is empty.

---
