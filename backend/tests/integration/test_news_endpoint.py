import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
import json
from jose import jwt
from src.main import app

# from main import Base, NewsArticle, User, open_database_session
from src.database import open_database_session
from src.users.modal import User
from src.users.config import pwd_context
from src.news.modal import NewsArticle
from src.database import Base
from src.news.schema import NewsSummaryRequestSchema, PromptRequest

# from main import NewsSummaryRequestSchema, PromptRequest
# from main import pwd_context
from unittest.mock import Mock

SECRET_KEY = "1892dhianiandowqd0n"
ALGORITHM = "HS256"
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 重建資料庫
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_session_opener():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[open_database_session] = override_session_opener
client = TestClient(app)


@pytest.fixture(scope="function")
def clean_db():
    """
    Fixture: 清理資料庫
    確保每次測試都在一個乾淨的資料庫環境中進行。
    """
    with next(override_session_opener()) as db:
        db.query(NewsArticle).delete()
        db.query(User).delete()
        db.commit()


@pytest.fixture(scope="function")
def test_user(clean_db):
    """
    Fixture: 建立測試用戶
    """
    hashed_password = pwd_context.hash("testpassword")
    with next(override_session_opener()) as db:
        user = User(username="testuser", hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


@pytest.fixture(scope="function")
def test_token(test_user):
    """
    Fixture: 為測試用戶生成 JWT token
    """
    access_token = jwt.encode(
        {"sub": test_user.username}, SECRET_KEY, algorithm=ALGORITHM
    )
    return access_token


@pytest.fixture(scope="function")
def test_articles(clean_db):
    """
    Fixture: 建立測試文章數據
    """
    with next(override_session_opener()) as db:
        article_1 = NewsArticle(
            url="https://example.com/test-news-1",
            title="Test News 1",
            content="This is test content 1",
            time="2024-01-01",
            summary="Test summary 1",
            reason="Test reason 1",
        )
        article_2 = NewsArticle(
            url="https://example.com/test-news-2",
            title="Test News 2",
            content="This is test content 2",
            time="2024-01-02",
            summary="Test summary 2",
            reason="Test reason 2",
        )
        db.add_all([article_1, article_2])
        db.commit()
        db.refresh(article_1)
        db.refresh(article_2)
        return [article_1, article_2]


def test_read_news(test_articles):
    """
    測試: 獲取所有新聞列表
    """
    response = client.get("/api/v1/news/news")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == len(test_articles)
    assert json_response[0]["title"] == test_articles[1].title
    assert json_response[1]["title"] == test_articles[0].title


def test_read_user_news(test_user, test_token, test_articles):
    """
    測試: 獲取用戶新聞列表
    """
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/news/user_news", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == len(test_articles)


def test_upvote_article(test_user, test_token, test_articles):
    """
    測試: 點讚文章
    """
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post(
        f"/api/v1/news/{test_articles[0].id}/upvote", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article upvoted"


# def test_downvote_article(test_user, test_token, test_articles):
#     """
#     測試: 取消點讚文章
#     """
#     headers = {"Authorization": f"Bearer {test_token}"}
#     response = client.post(
#         f"/api/v1/news/{test_articles[0].id}/downvote", headers=headers
#     )
#     assert response.status_code == 200
#     assert response.json()["message"] == "Downvote successful"
