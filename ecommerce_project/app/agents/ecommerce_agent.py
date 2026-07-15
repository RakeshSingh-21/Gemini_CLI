from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from agents.llm_client import ask_llm
from agents.recommendation_agent import get_product_suggestions
from agents.support_agent import get_support_response
from agents.admin_agent import get_admin_analytics
import models

# def classify_intent(query: str) -> str:
#     # Use LLM to classify user intent
#     prompt = f"""Classify the following user query into one of these categories: 
#     product_recommendation, order_status, cart_help, admin_analytics, general_support, product_description_generation.
#     Return only the category name.

#     Query: {query}
#     Category:"""
    
#     intent = ask_llm(prompt).strip().lower()
#     # Basic sanitization and fallback
#     if intent not in ["product_recommendation", "order_status", "cart_help", "admin_analytics", "general_support", "product_description_generation"]:
#         return "general_support" # Default to general support if classification is unclear
#     return intent

def classify_intent(query: str) -> str:
    q = query.lower()

    if any(word in q for word in [
        "analytics", "sales", "stock", "low stock",
        "total users", "total orders", "total products",
        "business summary"
    ]):
        return "admin_analytics"


    # 🔥 PRODUCT RECOMMENDATION (fix here)
    if any(word in q for word in [
        "recommend", "suggest", "show", "best",
        "product", "buy", "price", "under", "cheap"
    ]):
        return "product_recommendation"

    elif any(word in q for word in ["order", "status", "track"]):
        return "order_status"

    elif any(word in q for word in ["cart", "checkout"]):
        return "cart_help"

    elif any(word in q for word in ["analytics", "sales", "stock"]):
        return "admin_analytics"

    return "general_support"

def ecommerce_agent_chat(db: Session, query: str, current_user: Optional[models.User] = None) -> Dict[str, Any]:
    intent = classify_intent(query)
    response_data = {"intent": intent, "response": ""}

    if intent == "product_recommendation":
        suggestions = get_product_suggestions(db, query)
        if suggestions:
            response_data["response"] = "Here are some product recommendations based on your query:"
            response_data["products"] = suggestions
        else:
            response_data["response"] = "Sorry, I couldn't find any product recommendations matching your request."
    
    elif intent == "order_status":
        if not current_user:
            response_data["response"] = "Please log in to check your order status."
        else:
            orders = current_user.orders
            if orders:
                order_summaries = []
                for order in orders:
                    order_summaries.append(f"Order ID: {order.id}, Total: ${order.total_price:.2f}, Status: {order.status}, Date: {order.created_at.strftime('%Y-%m-%d')}")
                response_data["response"] = "Here are your recent orders:\n" + "\n".join(order_summaries)
            else:
                response_data["response"] = "You have no orders yet."

    elif intent == "cart_help":
        if not current_user:
            response_data["response"] = "Please log in to get help with your cart."
        else:
            cart_items = current_user.cart.items if current_user.cart else []
            if cart_items:
                cart_summary = []
                for item in cart_items:
                    cart_summary.append(f"{item.product.name} (x{item.quantity})")
                response_data["response"] = "Here's what's in your cart: " + ", ".join(cart_summary) + ". If you have specific issues, please describe them."
            else:
                response_data["response"] = "Your cart is empty. How can I help you with adding items or other cart-related questions?"

    elif intent == "admin_analytics":
        if not current_user or current_user.role != "admin":
            response_data["response"] = "Access denied. Admin only feature."
        else:
            analytics = get_admin_analytics(db)

            lines = [
                f"Total Products: {analytics['total_products']}",
                f"Total Users: {analytics['total_users']}",
                f"Total Orders: {analytics['total_orders']}",
                f"Total Sales: ₹{analytics['total_sales_amount']:.2f}"
            ]

            if analytics["low_stock_products"]:
                low_stock = [p["name"] for p in analytics["low_stock_products"]]
                lines.append(f"Low Stock (<5): {', '.join(low_stock)}")
            else:
                lines.append("No low stock products.")

            response_data["response"] = "\n".join(lines)

    elif intent == "general_support":
        response_data["response"] = get_support_response(query)

    elif intent == "product_description_generation":
        response_data["response"] = "This intent is handled by a separate endpoint. Please use the generate-description route."
    
    else:
        response_data["response"] = "I'm sorry, I don't understand your request. Please try rephrasing."

    return response_data

# def ecommerce_agent_admin_chat(db: Session, query: str) -> Dict[str, Any]:
#     intent = classify_intent(query)
#     response_data = {"intent": intent, "response": ""}
    
#     if intent == "admin_analytics":
#         analytics = get_admin_analytics(db)
#         response_lines = [
#             f"Total Products: {analytics["total_products"]}",
#             f"Total Users: {analytics["total_users"]}",
#             f"Total Orders: {analytics["total_orders"]}",
#             f"Total Sales Amount: ${analytics["total_sales_amount"]:.2f}"
#         ]
#         if analytics["low_stock_products"]:
#             low_stock_names = [p["name"] for p in analytics["low_stock_products"]]
#             response_lines.append(f"Low Stock Products (<10): {", ".join(low_stock_names)}")
#         else:
#             response_lines.append("No products are currently low in stock.")
#         response_data["response"] = "".join(response_lines)


#     elif intent == "product_description_generation":
#         response_data["response"] = "This intent is handled by a separate endpoint. Please use the generate-description route."
#     else:
#         response_data["response"] = get_support_response(query) # Admin can also ask general support questions
    
#     return response_data


def ecommerce_agent_admin_chat(db: Session, query: str) -> Dict[str, Any]:
    intent = classify_intent(query)
    response_data = {"intent": intent, "response": ""}

    if intent == "admin_analytics":
        analytics = get_admin_analytics(db)

        response_lines = [
            f"Total Products: {analytics['total_products']}",
            f"Total Users: {analytics['total_users']}",
            f"Total Orders: {analytics['total_orders']}",
            f"Total Sales Amount: ₹{analytics['total_sales_amount']:.2f}"
        ]

        if analytics["low_stock_products"]:
            low_stock_names = [p["name"] for p in analytics["low_stock_products"]]
            response_lines.append(
                f"Low Stock Products (<10): {', '.join(low_stock_names)}"
            )
        else:
            response_lines.append("No products are currently low in stock.")

        response_data["response"] = "\n".join(response_lines)

    elif intent == "product_description_generation":
        response_data["response"] = "This intent is handled by a separate endpoint."

    else:
        response_data["response"] = get_support_response(query)

    return response_data


def generate_product_description(product_name: str, product_features: str) -> str:
    prompt = f"""Generate a compelling and detailed product description for a product with the following name and features:

    Product Name: {product_name}
    Product Features: {product_features}

    Generated Description:"""

    # llm_response = ask_llm(prompt)
    return ask_llm(prompt)
