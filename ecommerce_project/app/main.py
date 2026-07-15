from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models
from routes import api, pages, agent_routes, payment
import uvicorn


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api.router)
app.include_router(pages.router)
app.include_router(agent_routes.router)
app.include_router(payment.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
