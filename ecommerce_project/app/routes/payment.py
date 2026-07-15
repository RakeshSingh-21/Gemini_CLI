import razorpay
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import models, database, auth, schemas
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/payment")

client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

@router.post("/create-order")
def create_order(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    amount = int(sum(item.product.price * item.quantity for item in current_user.cart.items) * 100)
    
    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_rcptid_{current_user.id}"
    }
    razorpay_order = client.order.create(data=order_data)
    return razorpay_order

@router.post("/verify")
def verify_payment(
    razorpay_order_id: str = Form(...),
    razorpay_payment_id: str = Form(...),
    razorpay_signature: str = Form(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    
    try:
        client.utility.verify_payment_signature(params_dict)
    except:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # Create order after successful verification
    total_price = sum(item.product.price * item.quantity for item in current_user.cart.items)
    new_order = models.Order(user_id=current_user.id, total_price=total_price)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item in current_user.cart.items:
        order_item = models.OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.add(order_item)
        item.product.stock -= item.quantity
    
    db.query(models.CartItem).filter(models.CartItem.cart_id == current_user.cart.id).delete()
    db.commit()
    
    return {"message": "Payment verified and order created", "order_id": new_order.id}
