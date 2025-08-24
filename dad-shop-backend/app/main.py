from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .db import engine
from .routes import products, sales, reports

# This creates the tables. In a production app, you'd use Alembic migrations.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dad Shop Backend")

# Allow frontend dev & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# The root path can be a simple welcome message or API documentation link
@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Welcome to Dad's Shop API. Visit /docs for documentation."}

# include routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(sales.router,    prefix="/api/sales",    tags=["sales"])
app.include_router(reports.router,  prefix="/api/reports",  tags=["reports"])
