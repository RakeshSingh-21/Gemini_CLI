from mcp_server.ecommerce_mcp import (
    search_products,
    get_low_stock_products,
    get_admin_analytics,
    get_user_orders
)

def mcp_search_products(query, max_price=None):
    return search_products(query, max_price)

def mcp_low_stock():
    return get_low_stock_products()

def mcp_admin_analytics():
    return get_admin_analytics()

def mcp_user_orders(user_id):
    return get_user_orders(user_id)