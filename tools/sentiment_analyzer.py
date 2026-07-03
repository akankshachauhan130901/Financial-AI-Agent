from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from dotenv import load_dotenv

load_dotenv()

# Load FinBERT model once when file is imported
print("Loading FinBERT model... (first time may take 1-2 minutes)")
MODEL_NAME = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()
print("FinBERT model loaded successfully!")


def analyze_sentiment(text: str):
    """
    Analyzes financial sentiment of given text.

    Args:
        text: Any financial text (news title, description etc.)

    Returns:
        Dictionary with sentiment label and confidence score
    """
    if not text or text.strip() == "":
        return {"sentiment": "neutral", "confidence": 0.0}

    # Tokenize input
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    # Get prediction
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert to probabilities
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    probs = probs.numpy()[0]

    # FinBERT labels
    labels = ["positive", "negative", "neutral"]
    scores = {label: round(float(prob), 4) for label, prob in zip(labels, probs)}

    # Get highest confidence label
    best_label = max(scores, key=scores.get)
    confidence = scores[best_label]

    return {
        "sentiment": best_label,
        "confidence": confidence,
        "scores": scores
    }


def analyze_news_sentiment(articles: list):
    """
    Analyzes sentiment for a list of news articles.

    Args:
        articles: List of article dicts from news_fetcher

    Returns:
        Same list with sentiment added to each article
    """
    results = []

    for article in articles:
        # Combine title and description for better accuracy
        text = f"{article.get('title', '')}. {article.get('description', '')}"

        sentiment_result = analyze_sentiment(text)

        article_with_sentiment = {
            **article,
            "sentiment": sentiment_result["sentiment"],
            "confidence": sentiment_result["confidence"],
            "scores": sentiment_result["scores"]
        }

        results.append(article_with_sentiment)

    return results


if __name__ == "__main__":
    # Test with sample financial texts
    test_texts = [
        "Tesla reports record profits, stock surges 15%",
        "Infosys faces massive losses, layoffs expected",
        "Apple announces new product lineup for next quarter"
    ]

    print("\n--- Testing FinBERT Sentiment Analysis ---\n")
    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"Text      : {text}")
        print(f"Sentiment : {result['sentiment'].upper()}")
        print(f"Confidence: {result['confidence'] * 100:.1f}%")
        print(f"Scores    : {result['scores']}")
        print("-" * 60)