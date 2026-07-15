from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from sqlalchemy.orm import Session
import database, auth, models, schemas
from agents.ecommerce_agent import ecommerce_agent_chat, ecommerce_agent_admin_chat, generate_product_description
from typing import Optional

router = APIRouter(prefix="/api/agent")

@router.post("/chat")
async def chat_with_agent(
    query: str = Form(...),
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user)
):
    response_data = ecommerce_agent_chat(db, query, current_user)
    return response_data

@router.post("/admin")
async def chat_with_admin_agent(
    query: str = Form(...),
    db: Session = Depends(database.get_db),
    admin_user: models.User = Depends(auth.get_admin_user)
):
    response_data = ecommerce_agent_admin_chat(db, query)
    return response_data

@router.post("/generate-description")
async def generate_description_api(
    product_name: str = Form(...),
    product_features: str = Form(...),
    admin_user: models.User = Depends(auth.get_admin_user)
):
    description = generate_product_description(product_name, product_features)
    return {"description": description}



