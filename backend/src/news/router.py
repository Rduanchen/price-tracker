from fastapi import APIRouter, Depends
from src.database import open_database_session
import itertools
from src.users.service import authenticate_user_token
from src.news.modal import NewsArticle
from src.news.service import (
    fetch_news_articles,
    generate_summary,
    toggle_upvote,
    extract_keywords,
    process_news_list,
)
from src.users.service import get_article_upvote_data
from src.news.schema import PromptRequest, NewsSummaryRequestSchema


router = APIRouter(
    prefix="/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)

id_counter = itertools.count(start=1000000)


# @router.get("/api/v1/news/articles")


@router.get("/news")
def get_all_news(db=Depends(open_database_session)):
    """
    read new

    :param db:
    :return:
    """
    news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    results = []
    for article in news_articles:
        upvotes, is_upvoted = get_article_upvote_data(article.id, None, db)
        results.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
        )
    return results


@router.get("/user_news")
def get_user_news(
    db=Depends(open_database_session), user=Depends(authenticate_user_token)
):
    news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    results = []
    for article in news_articles:
        upvotes, is_upvoted = get_article_upvote_data(article.id, user.id, db)
        results.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
        )
    return results


@router.post("/search_news")
async def search_news(request: PromptRequest):
    prompt = request.prompt
    keyword_response = extract_keywords(prompt)
    news_list = fetch_news_articles(keyword_response, initial_fetch=False)
    return process_news_list(news_list)


@router.post("/news_summary")
async def news_summary(
    payload: NewsSummaryRequestSchema, user=Depends(authenticate_user_token)
):
    response = generate_summary(payload.content)
    return {"summary": response["影響"], "reason": response["原因"]}


# FIXME: Problem might here
@router.post("/{article_id}/upvote")
def upvote_article(
    article_id, db=Depends(open_database_session), user=Depends(authenticate_user_token)
):
    message = toggle_upvote(article_id, user.id, db)
    return {"message": message}
