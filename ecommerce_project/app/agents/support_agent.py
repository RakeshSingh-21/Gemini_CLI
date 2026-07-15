from agents.llm_client import ask_llm

def get_support_response(query: str) -> str:
    support_context = """
    Our E-commerce Store Support Policy:
    - **Return Policy:** Customers can return products within 30 days of purchase for a full refund, provided the item is in its original condition and packaging. Perishable goods and items marked as final sale are not eligible for return.
    - **Cart Issues:** If you're experiencing issues with your cart (e.g., items not adding, disappearing), please try clearing your browser cache and cookies, or try using a different browser. If the problem persists, contact support with details.
    - **Checkout Issues:** For problems during checkout, ensure all your payment and shipping details are correct. Check if your payment method has sufficient funds. You can also try an alternative payment method. If errors continue, please reach out to our support team.
    - **Payment Issues:** We accept major credit cards (Visa, MasterCard, Amex) and PayPal. If your payment is declined, verify your card details, billing address, and ensure sufficient funds. Contact your bank if problems persist.
    - **Shipping:** We offer standard and express shipping options. Shipping costs and delivery times vary based on your location and chosen method. You can track your order via the 'My Orders' page.
    - **Order Cancellation:** Orders can be cancelled within 24 hours of placement, provided they have not yet been shipped. Please contact support immediately to request a cancellation.
    - **Account Issues:** If you are having trouble logging in or accessing your account, try the 'Forgot Password' link. If that doesn't work, contact support for assistance.
    """

    prompt = f"""Given the following e-commerce support context, answer the user's question. If the answer is not in the context, state that you cannot find the answer but provide general guidance to contact support.

    Support Context:
{support_context}

    User Question: {query}

    Answer:"""

    llm_response = ask_llm(prompt)
    return llm_response
