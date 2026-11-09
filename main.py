from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  
from database import init_db, save_review, get_all_reviews

# Initialize the FastAPI class
app = FastAPI(title='Review Intelligence API')


# Initialize the sentiment Analyser to process text
analyzer = SentimentIntensityAnalyzer()

# Initialize database and tables on startup
init_db()

pain_points = {
    "SHIPPING": ["late", "delay", "delayed", "slow", "weeks", "tracking", "never arrived"],
    "DAMAGED": ["broken", "damaged", "scratched", "cracked", "crushed", "torn"],
    "QUALITY": ["cheap", "fake", "flimsy", "terrible", "waste", "poor quality", "peeling"],
    "SERVICE": ["rude", "unhelpful", "refund", "support", "ignore", "bad support"]
}

def analyze_review(customer: str, product: str, rating: int, text: str):
    # Sentiment Scores
    all_scores = analyzer.polarity_scores(text)
    score = all_scores['compound']

    # Hybrid Sentiment Logic: Combines star rating with NLP text polarity
    if rating <= 2 or score < -0.05:
        sentiment = "NEGATIVE"
    elif rating >= 4 and score >= -0.05:
        sentiment = "POSITIVE"
    elif score > 0.05:
        sentiment = "POSITIVE"
    else:
        sentiment = "NEUTRAL"

    # Detecting Pain points
    text_lower = text.lower()
    identified_points = []

    for category, words in pain_points.items():
        for word in words:
            if word in text_lower:
                identified_points.append(category)
                break

    # Priority Logic
    if rating <= 2 or (sentiment == "NEGATIVE" and len(identified_points) >= 2):
        priority = "URGENT"
    elif sentiment == "NEGATIVE":
        priority = "HIGH"
    elif sentiment == "NEUTRAL" or rating >= 4:
        priority = "LOW"
    else:
        priority = "NORMAL"

    new_review = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "customer": customer,
        "product": product,
        "rating": rating,
        "review": text,
        "sentiment": sentiment,
        "pain_points": identified_points,
        "priority": priority
    }

    # Save in db
    saved_review = save_review(new_review)
    return saved_review


# Validating incoming request
class ReviewRequest(BaseModel):
    customer: str
    product: str
    rating: int = 5
    review: str

# FastAPI endpoint to submit reviews
@app.post("/api/reviews")
def submit_review(req: ReviewRequest):
    return analyze_review(req.customer, req.product, req.rating, req.review)

# FastAPI endpoint to fetch reviews from database
@app.get("/api/reviews")
def get_reviews():
    return get_all_reviews()

