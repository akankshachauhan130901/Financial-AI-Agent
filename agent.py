from groq import Groq
from dotenv import load_dotenv
import os
import json

from tools.news_fetcher import fetch_news
from tools.sentiment_analyzer import analyze_news_sentiment
from tools.stock_price import get_stock_price, get_price_change, get_price_history
from tools.ner_tool import extract_entities
from tools.summarizer import summarize_text

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Tool Definitions ──────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_news",
            "description": "Fetches latest financial news articles for a given company or topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Company name or topic to search news for e.g. Tesla, Apple, Bitcoin"
                    },
                    "num_articles": {
                        "type": "integer",
                        "description": "Number of articles to fetch (default 5)"
                    }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Gets current stock price and basic info for a ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol e.g. TSLA, AAPL, INFY"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_change",
            "description": "Gets price change percentage and direction for a stock ticker",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol e.g. TSLA, AAPL, INFY"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_history",
            "description": "Gets stock price history for last N days",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol e.g. TSLA, AAPL, INFY"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of history to fetch (default 7)"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sentiment",
            "description": "Analyzes financial sentiment of news articles for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Company name to fetch and analyze sentiment for"
                    }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_news",
            "description": "Fetches and summarizes latest news for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Company name to fetch and summarize news for"
                    }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_entities",
            "description": "Extracts named entities like companies, people, money values from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract entities from"
                    }
                },
                "required": ["text"]
            }
        }
    }
]


# ── Tool Execution ────────────────────────────────────────────
def execute_tool(tool_name: str, tool_args: dict):
    """Executes the appropriate tool based on name."""
    print(f"\n  🔧 Executing tool: {tool_name}")
    print(f"  📥 With args: {tool_args}")

    if tool_name == "fetch_news":
        result = fetch_news(
            tool_args["company_name"],
            tool_args.get("num_articles", 5)
        )
        return json.dumps(result, default=str)

    elif tool_name == "get_stock_price":
        result = get_stock_price(tool_args["ticker"])
        return json.dumps(result, default=str)

    elif tool_name == "get_price_change":
        result = get_price_change(tool_args["ticker"])
        return json.dumps(result, default=str)

    elif tool_name == "get_price_history":
        result = get_price_history(
            tool_args["ticker"],
            tool_args.get("days", 7)
        )
        return json.dumps(result, default=str)

    elif tool_name == "analyze_sentiment":
        articles = fetch_news(tool_args["company_name"], 5)
        results = analyze_news_sentiment(articles)
        sentiment_summary = []
        for r in results:
            sentiment_summary.append({
                "title": r["title"],
                "sentiment": r["sentiment"],
                "confidence": r["confidence"]
            })
        return json.dumps(sentiment_summary, default=str)

    elif tool_name == "summarize_news":
        articles = fetch_news(tool_args["company_name"], 3)
        summaries = []
        for article in articles:
            text = f"{article['title']}. {article['description']}"
            result = summarize_text(text)
            summaries.append({
                "title": article["title"],
                "summary": result.get("summary", "")
            })
        return json.dumps(summaries, default=str)

    elif tool_name == "extract_entities":
        result = extract_entities(tool_args["text"])
        return json.dumps(result, default=str)

    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


# ── Agent Loop ────────────────────────────────────────────────
def run_agent(user_query: str):
    """
    Main agent loop — takes user query, decides tools,
    executes them and returns final answer.
    """
    print(f"\n{'='*60}")
    print(f"  🤖 Financial AI Agent")
    print(f"{'='*60}")
    print(f"  📝 Query: {user_query}")
    print(f"{'='*60}")

    messages = [
        {
            "role": "system",
            "content": """You are a Financial AI Agent specialized in market insights.
You have access to tools for fetching news, stock prices, sentiment analysis, 
summarization and named entity recognition.

When a user asks about a company or stock:
1. Use the appropriate tools to gather data
2. Analyze the information
3. Provide a comprehensive, structured market insight

Always be specific with numbers, percentages and dates.
Format your final response clearly with sections."""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    # Agentic loop — keep calling tools until agent is done
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n  🔄 Agent iteration {iteration}...")

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1000
        )

        message = response.choices[0].message

        # If no tool calls — agent is done, return final answer
        if not message.tool_calls:
            print(f"\n{'='*60}")
            print("  ✅ Final Answer:")
            print(f"{'='*60}")
            print(message.content)
            return message.content

        # Process tool calls
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # Execute each tool and add results to messages
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_result = execute_tool(tool_name, tool_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

    return "Agent reached maximum iterations."


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test queries
    queries = [
        "What is the current stock price and market sentiment for Tesla?",
        "Give me a summary of latest Apple news and how the stock is performing."
    ]

    for query in queries:
        run_agent(query)
        print("\n")