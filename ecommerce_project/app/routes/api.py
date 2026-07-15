from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database, auth
from datetime import timedelta
from fastapi.responses import RedirectResponse
from database import get_db
import shutil
import os
import uuid

router = APIRouter(prefix="/api")

UPLOAD_DIR = "static/uploads/products"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# ... (Auth routes remain the same)

# Auth Routes
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    # First user is admin, others are customers (for demonstration)
    user_count = db.query(models.User).count()
    role = "admin" if user_count == 0 else "customer"
    
    new_user = models.User(username=user.username, email=user.email, password_hash=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create empty cart for the user
    new_cart = models.Cart(user_id=new_user.id)
    db.add(new_cart)
    db.commit()
    
    return new_user

@router.post("/login")
def login(response: Response, username: str = Form(...),
    password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user or not auth.verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

# Category Routes
@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryBase, db: Session = Depends(database.get_db), admin: models.User = Depends(auth.get_admin_user)):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Category).all()

# Brand Routes
@router.post("/brands", response_model=schemas.Brand)
def create_brand(brand: schemas.BrandBase, db: Session = Depends(database.get_db), admin: models.User = Depends(auth.get_admin_user)):
    db_brand = models.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.get("/brands", response_model=List[schemas.Brand])
def get_brands(db: Session = Depends(database.get_db)):
    return db.query(models.Brand).all()

# Product Routes

@router.get("/products", response_model=List[schemas.Product])
def get_products(
    db: Session = Depends(database.get_db),
    search_term: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    in_stock: bool | None = None
):
    query = db.query(models.Product).join(models.Category).join(models.Brand)

    if search_term:
        query = query.filter(models.Product.name.ilike(f"%{search_term}%"))
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    if brand_id is not None:
        query = query.filter(models.Product.brand_id == brand_id)
    if in_stock is True:
        query = query.filter(models.Product.stock > 0)

    return query.all()


@router.post("/products", response_model=schemas.Product)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    brand_id: int = Form(...),
    image_url: str | None = Form(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(auth.get_admin_user)
):
    final_image_url = image_url
    if image_file and image_file.filename:
        file_extension = os.path.splitext(image_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        final_image_url = f"/static/uploads/products/{filename}"

    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        brand_id=brand_id,
        image_url=final_image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    brand_id: int = Form(...),
    image_url: str | None = Form(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(auth.get_admin_user)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    final_image_url = image_url
    if image_file and image_file.filename:
        file_extension = os.path.splitext(image_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        final_image_url = f"/static/uploads/products/{filename}"
    elif image_url == '':  # User explicitly cleared the image URL
        final_image_url = None
    elif image_url is None: # No new URL and no file, keep existing image
        final_image_url = db_product.image_url

    db_product.name = name
    db_product.description = description
    db_product.price = price
    db_product.stock = stock
    db_product.category_id = category_id
    db_product.brand_id = brand_id
    db_product.image_url = final_image_url
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(auth.get_admin_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}


@router.post("/products/{product_id}/reviews", response_model=schemas.ProductReview)
def add_review(
    product_id: int,
    review: schemas.ProductReviewCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    new_review = models.ProductReview(
        product_id=product_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# Cart Routes
@router.get("/cart", response_model=schemas.Cart)
def get_cart(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return current_user.cart

@router.post("/cart/add")
def add_to_cart(item: schemas.CartItemBase, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    cart = current_user.cart

    cart_item = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == item.product_id).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        new_item = models.CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
        db.add(new_item)
    
    db.commit()
    return {"message": "Item added to cart"}

@router.delete("/cart/remove/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.cart_id == current_user.cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(auth.get_admin_user)
):
    valid_statuses = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid order status")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": "Order status updated"}

@router.get("/orders", response_model=List[schemas.Order])
def get_orders(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    if current_user.role == "admin":
        return db.query(models.Order).all()
    return current_user.orders

@router.post("/checkout")
def checkout(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")

    cart = current_user.cart

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = sum(item.product.price * item.quantity for item in cart.items)

    new_order = models.Order(
        user_id=current_user.id,
        total_price=total_price,
        status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart.items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)

        item.product.stock -= item.quantity

    db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id
    }

@router.post("/fake-payment")
def fake_payment(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")

    cart = current_user.cart

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = sum(
        item.product.price * item.quantity
        for item in cart.items
    )

    # Create order
    new_order = models.Order(
        user_id=current_user.id,
        total_price=total_price,
        status="Paid"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add order items
    for item in cart.items:

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        db.add(order_item)

        # Reduce stock
        item.product.stock -= item.quantity

    # Clear cart
    db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return {
        "message": "Fake Payment Successful",
        "order_id": new_order.id
    }
