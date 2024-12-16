"""
UDN News Scraper Module

This module provides the UDNCrawler class for fetching, parsing, and saving news articles from the UDN website.
The class extends the NewsCrawlerBase and includes functionalities to search for news articles based on a search term,
parse the details of individual articles, and save them to a database using SQLAlchemy ORM.

Classes:
    UDNCrawler: A class to scrape news from UDN.

Exceptions:
    DomainMismatchException: Raised when the URL domain does not match the expected domain for the crawler.

Usage Example:
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)

UDNCrawler Methods:
    __init__(self, timeout: int = 5): Initializes the crawler with a default timeout for HTTP requests.
    startup(self, search_term: str) -> list[Headline]: Fetches news headlines for a given search term across multiple pages.
    get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]: Fetches news headlines for specified pages.
    _fetch_news(self, page: int, search_term: str) -> list[Headline]: Helper method to fetch news headlines for a specific page.
    _create_search_params(self, page: int, search_term: str): Creates the parameters for the search request.
    _perform_request(self, params: dict): Performs the HTTP request to fetch news data.
    _parse_headlines(response): Parses the response to extract headlines.
    parse(self, url: str) -> News: Parses a news article from a given URL.
    _extract_news(soup, url: str) -> News: Extracts news details from the BeautifulSoup object.
    save(self, news: News, db: Session): Saves a news article to the database.
    _commit_changes(db: Session): Commits the changes to the database with error handling.
"""

from requests import Response
from urllib.parse import quote
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session


from src.crawler.crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        """
        Initializes the application by fetching news headlines for a given search term across multiple pages.
        This method is typically called at the beginning of the program when there is no data available,
        hence it fetches headlines from the first 10 pages.

        :param search_term: The term to search for in news headlines.
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        :rtype: list[Headline]
        """
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(
        self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:

        # Calculate the range of pages to fetch news from.
        # If 'page' is a tuple, unpack it and create a range representing those pages (inclusive).
        # If 'page' is an int, create a list containing only that single page number.
        page_range = range(*page) if isinstance(page, tuple) else [page]
        headlines = []
        for page_num in page_range:
            headlines.extend(self._fetch_news(page_num, search_term))
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        params = self._create_search_params(page, search_term)
        respones = self._perform_request(params=params)
        return self._parse_headlines(respones)


    def _create_search_params(self, page: int, search_term: str) -> dict:
        return {
            "id": f"search:{quote(search_term)}",
            "channelId": 2,
            "type": "searchword",
            "page": page,
        }

    def _perform_request(
        self, url: str | None = None, params: dict | None = None
    ) -> Response:
        try:
            response = requests.get(url or self.news_website_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to the news website. {e}")

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        data = response.json()
        if "lists" not in data:
            return []
        Headlines = []
        for item in data["lists"]:
            Headlines.append(
                Headline(
                    title = item.get("title", ""),
                    url = item.get("titleLink", "")
                )
            )
        return Headlines
    def parse(self, url: str) -> News: ...

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News: ...

    def save(self, news: NewsWithSummary, db: Session): ...

    @staticmethod
    def _commit_changes(db: Session): ...


if __name__ == "__main__":
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)