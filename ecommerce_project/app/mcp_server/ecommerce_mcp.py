import os
import sys
from fastmcp import FastMCP
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the parent directory (app/) to sys.path so we can import database and models
# This allows running the script from within the app/ directory as 'python mcp_server/ecommerce_mcp.py'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database import SessionLocal
import models

# Initialize FastMCP server
mcp = FastMCP("Ecommerce MCP Server")

@mcp.tool()
def search_products(keyword: str, max_price: float | None = None) -> list:
    print("🔥 MCP search_products tool called")
    """
    Search for products by keyword in the name and an optional maximum price.
    
    Args:
        keyword: The search term for the product name.
        max_price: Optional maximum price to filter products.
    """
    db = SessionLocal()
    try:
        query = db.query(models.Product).filter(models.Product.name.ilike(f"%{keyword}%"))
        if max_price is not None:
            query = query.filter(models.Product.price <= max_price)
        
        products = query.all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "stock": p.stock,
                "description": p.description
            } for p in products
        ]
    finally:
        db.close()

@mcp.tool()
def get_low_stock_products(limit_stock: int = 5) -> list:
    print("🔥 MCP search_products tool called")
    """
    Retrieve products that have stock less than the specified limit.
    
    Args:
        limit_stock: The stock threshold (default is 5).
    """
    db = SessionLocal()
    try:
        products = db.query(models.Product).filter(models.Product.stock < limit_stock).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "stock": p.stock,
                "price": p.price
            } for p in products
        ]
    finally:
        db.close()

@mcp.tool()
def get_admin_analytics() -> dict:
    """
    Fetch high-level e-commerce analytics including total users, products, orders, and revenue.
    """
    db = SessionLocal()
    try:
        total_users = db.query(models.User).count()
        total_products = db.query(models.Product).count()
        total_orders = db.query(models.Order).count()
        
        # Calculate total revenue from all orders
        revenue_result = db.query(func.sum(models.Order.total_price)).scalar()
        total_revenue = float(revenue_result) if revenue_result is not None else 0.0
        
        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2)
        }
    finally:
        db.close()

@mcp.tool()
def get_user_orders(user_id: int) -> list:
    """
    Retrieve all orders placed by a specific user.
    
    Args:
        user_id: The ID of the user whose orders are to be retrieved.
    """
    db = SessionLocal()
    try:
        orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
        result = []
        for order in orders:
            items = []
            for item in order.items:
                items.append({
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price
                })
            
            result.append({
                "order_id": order.id,
                "total_price": order.total_price,
                "status": order.status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "items": items
            })
        return result
    finally:
        db.close()

if __name__ == "__main__":
    # Start the FastMCP server
    mcp.run()
