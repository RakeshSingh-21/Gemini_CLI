from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from typing import Dict, Any, List

def get_admin_analytics(db: Session) -> Dict[str, Any]:
    total_products = db.query(models.Product).count()
    total_users = db.query(models.User).filter(models.User.role == "customer").count()
    total_orders = db.query(models.Order).count()

    # Low stock products (e.g., stock < 10)
    low_stock_products = db.query(models.Product).filter(models.Product.stock < 10).all()
    low_stock_products_data = [{
        "id": p.id,
        "name": p.name,
        "stock": p.stock,
        "image_url": p.image_url
    } for p in low_stock_products]

    # Total sales amount
    total_sales_amount = db.query(func.sum(models.Order.total_price)).scalar() or 0.0

    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "low_stock_products": [
            {
                "id": p.id,
                "name": p.name,
                "stock": p.stock,
                "price": float(p.price)
            }
            for p in low_stock_products
        ],
        "total_sales_amount": total_sales_amount
    }
