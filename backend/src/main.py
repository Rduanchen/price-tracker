from apscheduler.schedulers.background import BackgroundScheduler
import sentry_sdk
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.database import SessionLocal
from src.news.router import router as news_router
from src.users.router import router as user_router
from src.price.router import router as price_router
from src.news.service import (
    process_and_store_news_articles,
)
from src.news.modal import NewsArticle


sentry_sdk.init(
    dsn="https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()
bgs = BackgroundScheduler()
scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(NewsArticle).count() == 0:
        process_and_store_news_articles(initial_fetch=True)
    db.close()
    scheduler.add_job(process_and_store_news_articles, "interval", minutes=100)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


print(type(news_router))
app.include_router(news_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(price_router, prefix="/api/v1")
