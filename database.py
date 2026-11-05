import sqlite3
import json

DB_FILE = "reviews.db"

def get_connection():

    conn = sqlite3.connect(DB_FILE)
    # Allows accessing columns by column name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable WAL mode 
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # 1. Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            pain_points TEXT NOT NULL,
            priority TEXT NOT NULL
        )
    """)
    
    # 2. Seed initial sample reviews if database is empty
    cursor.execute("SELECT COUNT(*) FROM reviews")
    if cursor.fetchone()[0] == 0:
        sample_reviews = [
            ("2026-10-30 14:10", "sara@gmail.com", "Headphones", 1, "The box arrived 2 weeks late.", "NEGATIVE", '["SHIPPING"]', "URGENT"),
            ("2026-10-31 01:10", "saim@gmail.com", "Phone", 4, "The product is good.", "POSITIVE", '[]', "LOW"),
            ("2026-10-21 20:20", "hamza@gmail.com", "Keyboard", 2, "The keys are sticky and not working.", "NEGATIVE", '["QUALITY"]', "HIGH"),
        ]
        cursor.executemany("""
            INSERT INTO reviews (date, customer, product, rating, review, sentiment, pain_points, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_reviews)
    
    conn.commit()
    conn.close()

def save_review(review: dict) -> dict:

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO reviews (date, customer, product, rating, review, sentiment, pain_points, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review["date"],
        review["customer"],
        review["product"],
        review["rating"],
        review["review"],
        review["sentiment"],
        json.dumps(review["pain_points"]),  # Lists are converted to JSON text in SQLite
        review["priority"]
    ))
    
    # Assign the auto-generated database ID
    review["id"] = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return review

def get_all_reviews() -> list:

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM reviews ORDER BY id DESC")
    rows = cursor.fetchall()
    
    reviews = []
    for row in rows:
        reviews.append({
            "id": row["id"],
            "date": row["date"],
            "customer": row["customer"],
            "product": row["product"],
            "rating": row["rating"],
            "review": row["review"],
            "sentiment": row["sentiment"],
            "pain_points": json.loads(row["pain_points"]),  # Convert JSON text back to Python list
            "priority": row["priority"]
        })
    
    conn.close()
    return reviews

