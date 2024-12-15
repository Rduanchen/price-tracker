from src.news.modal import NewsArticle
from src.database import SessionLocal
from urllib.parse import quote
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import json
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session
import itertools
from src.news.modal import user_news_association_table


def add_news_article(news_data):
    session = SessionLocal()
    session.add(
        NewsArticle(
            url=news_data["url"],
            title=news_data["title"],
            time=news_data["time"],
            content=" ".join(news_data["content"]),
            summary=news_data["summary"],
            reason=news_data["reason"],
        )
    )
    session.commit()
    session.close()


def fetch_news_articles(search_term, initial_fetch=False):
    """
    get new

    :param search_term:
    :param is_initial:
    :return:
    """
    all_news_data = []
    params = {
        "id": f"search:{quote(search_term)}",
        "channelId": 2,
        "type": "searchword",
        "page": None,
    }
    if initial_fetch:
        for page_number in range(1, 10):
            params["page"] = page_number
            response = requests.get("https://udn.com/api/more", params=params)
            all_news_data.extend(response.json().get("lists", []))
    else:
        params["page"] = 1
        response = requests.get("https://udn.com/api/more", params=params)
        all_news_data = response.json().get("lists", [])
    return all_news_data


def process_and_store_news_articles(initial_fetch=False):
    news_data = fetch_news_articles("價格", initial_fetch=initial_fetch)
    for news in news_data:
        relevance = evaluate_news_relevance(news["title"])
        if relevance == "high":
            detailed_news = extract_news_details(news["titleLink"])
            summary_response = generate_summary(detailed_news["content"])
            detailed_news.update(summary_response)
            add_news_article(detailed_news)


def evaluate_news_relevance(title):
    prompt = [
        {
            "role": "system",
            "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
        },
        {"role": "user", "content": title},
    ]
    ai_response = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
    )
    return ai_response.choices[0].message.content


def extract_news_details(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="article-content__title").text
    time = soup.find("time", class_="article-content__time").text
    content_section = soup.find("section", class_="article-content__editor")
    paragraphs = [
        p.text
        for p in content_section.find_all("p")
        if p.text.strip() != "" and "•" not in p.text
    ]
    return {
        "url": news_url,
        "title": title,
        "time": time,
        "content": paragraphs,
    }


def generate_summary(content):
    prompt = [
        {
            "role": "system",
            "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
        },
        {"role": "user", "content": " ".join(content)},
    ]
    ai_response = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
    )
    return json.loads(ai_response.choices[0].message.content)


def extract_keywords(content):
    prompt = [
        {
            "role": "system",
            "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
        },
        {"role": "user", "content": content},
    ]
    ai_response = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
    )
    return ai_response.choices[0].message.content


id_counter = itertools.count(start=1000000)


def process_news_list(news_items):
    news_list = []
    for news in news_items:
        try:
            detailed_news = extract_news_details(news["titleLink"])
            detailed_news["content"] = " ".join(detailed_news["content"])
            detailed_news["id"] = next(id_counter)
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)


def toggle_upvote(article_id, user_id, db):
    existing_upvote = db.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_article_id == article_id,
            user_news_association_table.c.user_id == user_id,
        )
    ).scalar()

    if existing_upvote:
        delete_statement = delete(user_news_association_table).where(
            user_news_association_table.c.news_article_id == article_id,
            user_news_association_table.c.user_id == user_id,
        )
        db.execute(delete_statement)
        db.commit()
        return "Upvote removed"
    else:
        insert_statement = insert(user_news_association_table).values(
            news_article_id=article_id, user_id=user_id
        )
        db.execute(insert_statement)
        db.commit()
        return "Article upvoted"


def news_exists(id2, db: Session):
    return db.query(NewsArticle).filter_by(id=id2).first() is not None
