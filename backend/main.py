import json
import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
import requests
from fastapi import APIRouter, HTTPException, Query, Depends, status, FastAPI
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, AnyHttpUrl
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from urllib.parse import quote
from bs4 import BeautifulSoup
import itertools

# Base = declarative_base()
# db_engine = create_engine("sqlite:///news_database.db", echo=True)
# Base.metadata.create_all(db_engine)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# user_news_association_table = Table(
#     "user_news_upvotes",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
#     Column(
#         "news_article_id", Integer, ForeignKey("news_articles.id"), primary_key=True
#     ),
# )


# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     username = Column(String(50), unique=True, nullable=False)
#     hashed_password = Column(String(200), nullable=False)
#     upvoted_news = relationship(
#         "NewsArticle",
#         secondary=user_news_association_table,
#         back_populates="upvoted_by_users",
#     )


# class NewsArticle(Base):
#     __tablename__ = "news_articles"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     url = Column(String, unique=True, nullable=False)
#     title = Column(String, nullable=False)
#     time = Column(String, nullable=False)
#     content = Column(Text, nullable=False)
#     summary = Column(Text, nullable=False)
#     reason = Column(Text, nullable=False)
#     upvoted_by_users = relationship(
#         "User", secondary=user_news_association_table, back_populates="upvoted_news"
#     )


# sentry_sdk.init(
#     dsn="https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000",
#     traces_sample_rate=1.0,
#     profiles_sample_rate=1.0,
# )

# app = FastAPI()
# bgs = BackgroundScheduler()
# scheduler = BackgroundScheduler()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8080"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from openai import OpenAI


# def generate_summary(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content

#
# def extract_search_keywords(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content


from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session


# Removed
# def add_new(news_data):
#     """
#     add new to db
#     :param news_data: news info
#     :return:
#     """
#     session = Session()
#     session.add(
#         NewsArticle(
#             url=news_data["url"],
#             title=news_data["title"],
#             time=news_data["time"],
#             content=" ".join(news_data["content"]),  # 將內容list轉換為字串
#             summary=news_data["summary"],
#             reason=news_data["reason"],
#         )
#     )


# def add_news_article(news_data):
#     session = SessionLocal()
#     session.add(
#         NewsArticle(
#             url=news_data["url"],
#             title=news_data["title"],
#             time=news_data["time"],
#             content=" ".join(news_data["content"]),
#             summary=news_data["summary"],
#             reason=news_data["reason"],
#         )
#     )
#     session.commit()
#     session.close()


# def fetch_news_articles(search_term, initial_fetch=False):
#     """
#     get new

#     :param search_term:
#     :param is_initial:
#     :return:
#     """
#     all_news_data = []
#     params = {
#         "id": f"search:{quote(search_term)}",
#         "channelId": 2,
#         "type": "searchword",
#         "page": None,
#     }
#     if initial_fetch:
#         for page_number in range(1, 10):
#             params["page"] = page_number
#             response = requests.get("https://udn.com/api/more", params=params)
#             all_news_data.extend(response.json().get("lists", []))
#     else:
#         params["page"] = 1
#         response = requests.get("https://udn.com/api/more", params=params)
#         all_news_data = response.json().get("lists", [])
#     return all_news_data


# def process_and_store_news_articles(initial_fetch=False):
#     news_data = fetch_news_articles("價格", initial_fetch=initial_fetch)
#     for news in news_data:
#         relevance = evaluate_news_relevance(news["title"])
#         if relevance == "high":
#             detailed_news = extract_news_details(news["titleLink"])
#             summary_response = generate_summary(detailed_news["content"])
#             detailed_news.update(summary_response)
#             add_news_article(detailed_news)


# def evaluate_news_relevance(title):
#     prompt = [
#         {
#             "role": "system",
#             "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
#         },
#         {"role": "user", "content": title},
#     ]
#     ai_response = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=prompt,
#     )
#     return ai_response.choices[0].message.content


# def extract_news_details(news_url):
#     response = requests.get(news_url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     title = soup.find("h1", class_="article-content__title").text
#     time = soup.find("time", class_="article-content__time").text
#     content_section = soup.find("section", class_="article-content__editor")
#     paragraphs = [
#         p.text
#         for p in content_section.find_all("p")
#         if p.text.strip() != "" and "•" not in p.text
#     ]
#     return {
#         "url": news_url,
#         "title": title,
#         "time": time,
#         "content": paragraphs,
#     }


# def generate_summary(content):
#     prompt = [
#         {
#             "role": "system",
#             "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
#         },
#         {"role": "user", "content": " ".join(content)},
#     ]
#     ai_response = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=prompt,
#     )
#     return json.loads(ai_response.choices[0].message.content)


# @app.on_event("startup")
# def startup_event():
#     db = SessionLocal()
#     if db.query(NewsArticle).count() == 0:
#         process_and_store_news_articles(initial_fetch=True)
#     db.close()
#     scheduler.add_job(process_and_store_news_articles, "interval", minutes=100)
#     scheduler.start()


# @app.on_event("shutdown")
# def shutdown_event():
#     scheduler.shutdown()


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


# def open_database_session():
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# # FIXME: Problem might here
# def authenticate_user(db, username, password):
#     user = db.query(User).filter(User.username == username).first()
#     if user and verify_password(password, user.hashed_password):
#         return user
#     return False


# def create_jwt_token(data, expires_delta=None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, "1892dhianiandowqd0n", algorithm="HS256")
#     return encoded_jwt


# def authenticate_user_token(
#     token=Depends(oauth2_scheme), db=Depends(open_database_session)
# ):
#     payload = jwt.decode(token, "1892dhianiandowqd0n", algorithms=["HS256"])
#     return db.query(User).filter(User.username == payload.get("sub")).first()


# @app.post("/api/v1/users/login")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(open_database_session),
# ):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     # if not user:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
#     #     )
#     access_token = create_jwt_token(
#         data={"sub": user.username}, expires_delta=timedelta(minutes=30)
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


# class UserAuthSchema(BaseModel):
#     username: str
#     password: str


# @app.post("/api/v1/users/register")
# def register_user(user: UserAuthSchema, db: Session = Depends(open_database_session)):
#     hashed_password = pwd_context.hash(user.password)
#     new_user = User(username=user.username, hashed_password=hashed_password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


# @app.get("/api/v1/users/me")
# def get_current_user(user=Depends(authenticate_user_token)):
#     return {"username": user.username}


# id_counter = itertools.count(start=1000000)


# def get_article_upvote_data(article_id, user_id, db):
#     total_upvotes = (
#         db.query(user_news_association_table)
#         .filter_by(news_article_id=article_id)
#         .count()
#     )
#     user_voted = False
#     if user_id:
#         user_voted = (
#             db.query(user_news_association_table)
#             .filter_by(news_article_id=article_id, user_id=user_id)
#             .first()
#             is not None
#         )
#     return total_upvotes, user_voted


# @app.get("/api/v1/news/news")
# def get_all_news(db=Depends(open_database_session)):
#     """
#     read new

#     :param db:
#     :return:
#     """
#     news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
#     results = []
#     for article in news_articles:
#         upvotes, is_upvoted = get_article_upvote_data(article.id, None, db)
#         results.append(
#             {**article.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
#         )
#     return results


# @app.get("/api/v1/news/user_news")
# def get_user_news(
#     db=Depends(open_database_session), user=Depends(authenticate_user_token)
# ):
#     news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
#     results = []
#     for article in news_articles:
#         upvotes, is_upvoted = get_article_upvote_data(article.id, user.id, db)
#         results.append(
#             {**article.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
#         )
#     return results


# class PromptRequest(BaseModel):
#     prompt: str


# @app.post("/api/v1/news/search_news")
# async def search_news(request: PromptRequest):
#     prompt = request.prompt
#     keyword_response = extract_keywords(prompt)
#     news_list = fetch_news_articles(keyword_response, initial_fetch=False)
#     return process_news_list(news_list)


# def extract_keywords(content):
#     prompt = [
#         {
#             "role": "system",
#             "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
#         },
#         {"role": "user", "content": content},
#     ]
#     ai_response = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=prompt,
#     )
#     return ai_response.choices[0].message.content


# def process_news_list(news_items):
#     news_list = []
#     for news in news_items:
#         try:
#             detailed_news = extract_news_details(news["titleLink"])
#             detailed_news["content"] = " ".join(detailed_news["content"])
#             detailed_news["id"] = next(id_counter)
#             news_list.append(detailed_news)
#         except Exception as e:
#             print(e)
#     return sorted(news_list, key=lambda x: x["time"], reverse=True)


# class NewsSummaryRequestSchema(BaseModel):
#     content: str


# @app.post("/api/v1/news/news_summary")
# async def news_summary(
#     payload: NewsSummaryRequestSchema, user=Depends(authenticate_user_token)
# ):
#     response = generate_summary(payload.content)
#     return {"summary": response["影響"], "reason": response["原因"]}


# # FIXME: Problem might here
# @app.post("/api/v1/news/{article_id}/upvote")
# def upvote_article(
#     article_id, db=Depends(open_database_session), user=Depends(authenticate_user_token)
# ):
#     message = toggle_upvote(article_id, user.id, db)
#     return {"message": message}


# def toggle_upvote(article_id, user_id, db):
#     existing_upvote = db.execute(
#         select(user_news_association_table).where(
#             user_news_association_table.c.news_article_id == article_id,
#             user_news_association_table.c.user_id == user_id,
#         )
#     ).scalar()

#     if existing_upvote:
#         delete_statement = delete(user_news_association_table).where(
#             user_news_association_table.c.news_article_id == article_id,
#             user_news_association_table.c.user_id == user_id,
#         )
#         db.execute(delete_statement)
#         db.commit()
#         return "Upvote removed"
#     else:
#         insert_statement = insert(user_news_association_table).values(
#             news_article_id=article_id, user_id=user_id
#         )
#         db.execute(insert_statement)
#         db.commit()
#         return "Article upvoted"


# def news_exists(id2, db: Session):
#     return db.query(NewsArticle).filter_by(id=id2).first() is not None


# @app.get("/api/v1/prices/necessities-price")
# def get_necessities_prices(category=Query(None), commodity=Query(None)):
#     return requests.get(
#         "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice",
#         params={"CategoryName": category, "Name": commodity},
#     ).json()
