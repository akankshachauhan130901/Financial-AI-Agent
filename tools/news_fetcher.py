from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_news(company_name: str, num_articles: int = 5):
    """
    Fetches latest financial news for a given company.
    
    Args:
        company_name: Name of company e.g. 'Tesla', 'Infosys'
        num_articles: Number of articles to fetch (default 5)
    
    Returns:
        List of dictionaries with title, description, url, published date
    """
    api_key = os.getenv('NEWS_API_KEY')
    newsapi = NewsApiClient(api_key=api_key)

    response = newsapi.get_everything(
        q=company_name,
        language='en',
        sort_by='publishedAt',
        page_size=num_articles
    )

    articles = []

    if response['status'] == 'ok':
        for article in response['articles']:
            articles.append({
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'published_at': article['publishedAt'],
                'source': article['source']['name']
            })
    else:
        print("Error fetching news:", response['status'])

    return articles


if __name__ == "__main__":
    # Test the tool
    company = "Tesla"
    print(f"\nFetching news for: {company}\n")
    print("-" * 50)

    news = fetch_news(company, num_articles=3)

    for i, article in enumerate(news, 1):
        print(f"Article {i}:")
        print(f"  Title      : {article['title']}")
        print(f"  Source     : {article['source']}")
        print(f"  Published  : {article['published_at']}")
        print(f"  Description: {article['description']}")
        print(f"  URL        : {article['url']}")
        print("-" * 50)