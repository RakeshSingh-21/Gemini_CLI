from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database, models, auth
import os
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def home(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
    search_term: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    in_stock: bool | None = None
):
  
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    query = db.query(models.Product)

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

    products = query.all()

    categories = db.query(models.Category).all()
    brands = db.query(models.Brand).all()

    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "products": products, "user": current_user, "search_term": search_term, "min_price": min_price, "max_price": max_price, "category_id": category_id, "brand_id": brand_id, "in_stock": in_stock, "categories": categories, "brands": brands})
    
    # return templates.TemplateResponse("index.html", {"request": request, "products": products, "user": current_user})

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request,name="login.html",context={"request": request})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request,name="register.html",context={"request": request})

@router.get("/cart")
async def cart_page(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        return templates.TemplateResponse(request=request,name="login.html",context={"request": request, "msg": "Please login to view cart"})
      
    cart = current_user.cart
    overall_total = 0

    if cart and cart.items:
        for item in cart.items:
            overall_total += item.product.price * item.quantity
    return templates.TemplateResponse(request=request,name="cart.html",context={"request": request, "user": current_user, "cart": current_user.cart, "overall_total": overall_total})
    # return templates.TemplateResponse("cart.html", {"request": request, "user": current_user, "cart": current_user.cart})

@router.get("/orders")
async def orders_page(request: Request, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        return templates.TemplateResponse(request=request,name="login.html",context={"request": request, "msg": "Please login to view orders"})
        # return templates.TemplateResponse("login.html", {"request": request, "msg": "Please login to view orders"})
    
    if current_user.role == "admin":
        orders = db.query(models.Order).all()
    else:
        orders = current_user.orders

    return templates.TemplateResponse(request=request,name="orders.html",context={"request": request, "user": current_user, "orders": orders})  
    # return templates.TemplateResponse("orders.html", {"request": request, "user": current_user, "orders": orders})

@router.get("/admin")
async def admin_dashboard(request: Request, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_admin_user)):
    products = db.query(models.Product).all()
    orders = db.query(models.Order).all()
    return templates.TemplateResponse(request=request,name="admin_dashboard.html",context={"request": request, "user": current_user,"products": products, "orders": orders})
    # return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": current_user, "products": products, "orders": orders})

@router.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    return templates.TemplateResponse(request=request,name="product_detail.html",context={"request": request, "user": current_user, "product": product})
    # return templates.TemplateResponse("product_detail.html", {"request": request, "product": product, "user": current_user})


@router.get("/agent-chat")
async def agent_chat_page(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="agent_chat.html",
        context={
            "request": request,
            "user": current_user
        }
    )


@router.get("/admin-agent")
async def admin_agent_page(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="admin_agent.html",
        context={
            "request": request,
            "user": current_user
        }
    )


@router.get("/add-product")
async def add_product_page(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "admin":
        return RedirectResponse(url="/")

    categories = db.query(models.Category).all()
    brands = db.query(models.Brand).all()

    return templates.TemplateResponse(
        request=request,
        name="add_product.html",
        context={
            "request": request,
            "user": current_user,
            "categories": categories,
            "brands": brands
        }
    )


@router.get("/edit-product/{product_id}")
async def edit_product_page(
    product_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/login", status_code=303)

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        return RedirectResponse(url="/admin", status_code=303)

    categories = db.query(models.Category).all()
    brands = db.query(models.Brand).all()

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "request": request,
            "user": current_user,
            "product": product,
            "categories": categories,
            "brands": brands
        }
    )
