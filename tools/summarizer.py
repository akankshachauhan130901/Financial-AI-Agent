from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_text(text: str):
    """
    Summarizes financial text using Groq LLM.

    Args:
        text: Financial text to summarize

    Returns:
        Dictionary with original text and summary
    """
    if not text or text.strip() == "":
        return {"summary": "No text provided", "original": text}

    if len(text.split()) < 30:
        return {
            "summary": text,
            "original": text,
            "note": "Text too short to summarize"
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial news summarizer. Summarize the given text in 2-3 concise sentences. Focus on key financial facts, numbers, and impact."
                },
                {
                    "role": "user",
                    "content": f"Summarize this financial text:\n\n{text}"
                }
            ],
            max_tokens=150
        )

        summary = response.choices[0].message.content.strip()

        return {
            "original": text,
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e), "original": text}


def summarize_articles(articles: list):
    """
    Summarizes a list of news articles.

    Args:
        articles: List of article dicts from news_fetcher

    Returns:
        Same list with summary added to each article
    """
    results = []

    for article in articles:
        text = f"{article.get('title', '')}. {article.get('description', '')}"
        summary_result = summarize_text(text)

        article_with_summary = {
            **article,
            "summary": summary_result.get("summary", text)
        }

        results.append(article_with_summary)

    return results


if __name__ == "__main__":
    test_texts = [
        """Tesla Inc reported record breaking quarterly earnings on Thursday,
        surpassing analyst expectations by a significant margin. The electric
        vehicle giant posted revenue of $25 billion, up 35% year over year,
        driven by strong demand for its Model 3 and Model Y vehicles across
        all major markets including the United States, China and Europe.
        CEO Elon Musk credited the results to improved manufacturing efficiency
        at its gigafactories and a significant reduction in production costs
        per vehicle.""",

        """Apple Inc has announced a major strategic partnership with OpenAI
        to integrate advanced artificial intelligence features directly into
        its iPhone operating system. The deal, valued at approximately $1 billion,
        will see OpenAI technology powering Apple's new smart assistant features
        launching later this year. Analysts believe this move positions Apple
        strongly against competitors like Google and Microsoft who have already
        integrated AI into their core products. Apple shares jumped 8% following
        the announcement during after hours trading on Wall Street."""
    ]

    print("\n--- Testing Summarizer Tool ---\n")

    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"Original ({len(text.split())} words):")
        print(f"  {text[:150].strip()}...")
        print()
        result = summarize_text(text)
        print(f"Summary:")
        print(f"  {result.get('summary', 'Error')}")
        print("-" * 60)