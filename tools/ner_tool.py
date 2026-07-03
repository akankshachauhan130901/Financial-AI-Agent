import spacy
from dotenv import load_dotenv

load_dotenv()

# Load spaCy model once
print("Loading spaCy NER model...")
nlp = spacy.load("en_core_web_sm")
print("spaCy model loaded successfully!")


def extract_entities(text: str):
    """
    Extracts named entities from financial text.

    Args:
        text: Any financial text (news title, description etc.)

    Returns:
        Dictionary with categorized entities
    """
    if not text or text.strip() == "":
        return {}

    doc = nlp(text)

    entities = {
        "companies": [],
        "people": [],
        "money": [],
        "dates": [],
        "locations": [],
        "percentages": [],
        "others": []
    }

    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["companies"].append(ent.text)
        elif ent.label_ == "PERSON":
            entities["people"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC"]:
            entities["locations"].append(ent.text)
        elif ent.label_ == "PERCENT":
            entities["percentages"].append(ent.text)
        else:
            entities["others"].append(f"{ent.text} ({ent.label_})")

    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))

    return entities


def extract_entities_from_articles(articles: list):
    """
    Extracts entities from a list of news articles.

    Args:
        articles: List of article dicts from news_fetcher

    Returns:
        Same list with entities added to each article
    """
    results = []

    for article in articles:
        text = f"{article.get('title', '')}. {article.get('description', '')}"
        entities = extract_entities(text)

        article_with_entities = {
            **article,
            "entities": entities
        }

        results.append(article_with_entities)

    return results


if __name__ == "__main__":
    # Test with sample financial texts
    test_texts = [
        "Tesla CEO Elon Musk announced $5 billion investment in new gigafactory in Texas on Monday.",
        "Apple Inc. shares rose 12% after beating earnings expectations in Q3 2026.",
        "Infosys and Wipro reported strong growth in European markets, gaining $200 million in contracts."
    ]

    print("\n--- Testing NER Tool ---\n")

    for text in test_texts:
        print(f"Text: {text}")
        print("-" * 60)
        entities = extract_entities(text)

        for category, values in entities.items():
            if values:  # Only print non-empty categories
                print(f"  {category:<15}: {', '.join(values)}")

        print()