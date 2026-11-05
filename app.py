import streamlit as st
import pandas as pd
import requests

# FastAPI Backend Endpoint
API_URL = "http://127.0.0.1:8000/api/reviews"

st.set_page_config(page_title="Store Review Intelligence", page_icon="🛍️", layout="wide")

st.title("🛍️ Store Review Intelligence & Support Dashboard")
st.caption("Standalone review intelligence engine integrated with your online store. Automatically triages customer feedback, flags product defects, and escalates unhappy buyers.")

# Session state to hold store reviews fetched from API
if "reviews" not in st.session_state:
    try:
        # Fetches initial reviews from GET /api/v1/reviews
        res = requests.get(API_URL)
        if res.status_code == 200:
             #creating reviews key and assigning it list of dictionaries
            st.session_state["reviews"] = res.json()
        else:
            #For crash prevention as this is used in data frame
            st.session_state["reviews"] = []
    except requests.exceptions.ConnectionError:
        st.session_state["reviews"] = []

# 1. STOREFRONT INTEGRATION SIMULATOR 

st.markdown("### 📝 Submit Customer Review (Storefront Integration)")
st.write("When a buyer leaves a review on any product page, your store forwards it to our API:")

with st.form("store_review_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        customer = st.text_input("Customer Email:", value="alex.turner@gmail.com", help="Who wrote the review")
    with col2:
      
        product = st.text_input("Product Name (Type any item):", value="Wireless Noise-Canceling Headphones", help="Type any product name")
    with col3:
        rating = st.slider("Star Rating:", min_value=1, max_value=5, value=1)

    review_text = st.text_area(
        "Customer Review Text:",
        value="The item arrived 2 weeks late and the plastic was cracked! Customer support refused to help.",
        placeholder="Type customer review here..."
    )
    
    submitted = st.form_submit_button("🚀 Submit & Analyze Review", type="primary")

    if submitted:
        if customer.strip() and product.strip() and review_text.strip():
            # Send HTTP POST to FastAPI backend endpoint @app.post("/api/v1/reviews")
            payload = {
                "customer": customer,
                "product": product,
                "rating": rating,
                "review": review_text
            }
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.reviews.insert(0, result)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Sentiment", result["sentiment"])
                    c2.metric("Pain Points", ", ".join(result["pain_points"]) if result["pain_points"] else "None Detected")
                    c3.metric("Priority Triage", result["priority"])
                    
                    if result["priority"] == "URGENT":
                        st.error(f"🚨 **URGENT SUPPORT ACTION REQUIRED:** Customer **{result['customer']}** left a 1-star complaint on **'{result['product']}'**! Reach out to prevent chargeback.")
                    else:
                        st.success(f"✅ Review from **{result['customer']}** analyzed and saved to store dashboard!")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Cannot reach FastAPI backend! Is `uvicorn main:app --reload` running on port 8000?")
        else:
            st.warning("Please fill in Customer Email, Product Name, and Review text.")

st.divider()

# -------------------------------------------------------------
# 2. STORE OWNER ANALYTICS & TRIAGE FEED
# -------------------------------------------------------------
st.markdown("### 📊 Store Owner Analytics & Reviews Feed")

df = pd.DataFrame(st.session_state.reviews)

if not df.empty:
    # KPI Metrics
    total = len(df)
    neg_count = len(df[df["sentiment"] == "NEGATIVE"])
    neg_rate = round((neg_count / total) * 100, 2)
    urgent_count = len(df[df["priority"] == "URGENT"])
    pos_count = len(df[df["sentiment"] == "POSITIVE"])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Store Reviews", total)
    k2.metric("Negative Review Rate", f"{neg_rate}%")
    k3.metric("Urgent Complaints", urgent_count, delta_color="inverse")
    k4.metric("Satisfied Buyers", pos_count)

    st.markdown("---")
    
    # Store Review History Table with Customer Details
    st.subheader("📋 Customer Review History")
    display_cols = ["date", "customer", "product", "rating", "sentiment", "priority", "pain_points", "review"]
    st.dataframe(df[display_cols], use_container_width=True)

    # Visual Charts for Store Owner
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Customer Sentiment Distribution")
        st.bar_chart(df["sentiment"].value_counts())
        
    with col_chart2:
        st.subheader("Complaints by Product")
        neg_df = df[df["sentiment"] == "NEGATIVE"]
        if not neg_df.empty:
            st.bar_chart(neg_df["product"].value_counts())
        else:
            st.info("No negative reviews recorded yet!")
