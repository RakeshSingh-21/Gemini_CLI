from sqlalchemy.orm import Session
from typing import List, Dict
import models, schemas
from agents.llm_client import ask_llm
import re

# def get_product_suggestions(db: Session, query: str) -> List[Dict]:
#     products = db.query(models.Product).filter(models.Product.stock > 0).all()
    
#     if not products:
#         return []
        
#     # Convert products to a format easily digestible by the LLM
#     product_data = []
#     for p in products:
#         product_data.append(f"ID: {p.id}, Name: {p.name}, Description: {p.description}, Price: {p.price:.2f}, Stock: {p.stock}")

#     products_str = "".join(product_data)

#     # Use LLM to get recommendations based on the query and available products
#     prompt = f"""Given the following products, recommend some products that match the user's query. 
# Only list products that are in stock.

# Available Products:
# {products_str}

# User Query: {query}

# Recommendations (list product names or IDs, or say no match found):"""

#     llm_response = ask_llm(prompt)
    
#     # Post-process LLM response to link back to actual products
#     recommended_product_names = [line.strip() for line in llm_response.split('') if line.strip()]
    
#     suggestions = []
#     for rec_name in recommended_product_names:
#         # Try to find product by name or ID mentioned in LLM response
#         # This is a simplified matching; more robust parsing might be needed
#         matched_product = None
#         for p in products:
#             if rec_name.lower() in p.name.lower() or f"ID: {p.id}" in rec_name:
#                 matched_product = p
#                 break
        
#         if matched_product:
#             suggestions.append({"id": matched_product.id, "name": matched_product.name, "description": matched_product.description, "price": matched_product.price, "image_url": matched_product.image_url})

#     return suggestions

def extract_price_limit(query: str):
    match = re.search(r"(under|below|less than)\s*(₹|rs|inr)?\s*(\d+)", query.lower())
    if match:
        return float(match.group(3))
    return None


def get_product_suggestions(db: Session, query: str) -> List[Dict]:
    q = query.lower()
    price_limit = extract_price_limit(q)

    products = db.query(models.Product).filter(models.Product.stock > 0).all()

    suggestions = []

    for p in products:
        name = (p.name or "").lower()
        desc = (p.description or "").lower()

        keywords = q.split()

    # synonyms
        if "mobile" in q or "mobiles" in q or "phone" in q or "phones" in q:
            keywords += ["mobile", "phone", "smartphone", "iphone", "samsung", "vivo", "oppo", "redmi", "oneplus", "realme"]

        matches_text = any(word in name or word in desc for word in q.split())
        matches_price = True

        if price_limit:
            matches_price = float(p.price) <= price_limit

        if matches_text and matches_price:
            suggestions.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "image_url": p.image_url
            })

    return suggestions[:5]
