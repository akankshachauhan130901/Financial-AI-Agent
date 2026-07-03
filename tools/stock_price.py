import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def get_stock_price(ticker: str):
    """
    Fetches current stock price and basic info.

    Args:
        ticker: Stock ticker symbol e.g. 'TSLA', 'INFY', 'AAPL'

    Returns:
        Dictionary with current price and stock info
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "previous_close": info.get("previousClose", "N/A"),
            "open_price": info.get("open", "N/A"),
            "day_high": info.get("dayHigh", "N/A"),
            "day_low": info.get("dayLow", "N/A"),
            "volume": info.get("volume", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "USD"),
        }

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def get_price_history(ticker: str, days: int = 7):
    """
    Fetches stock price history for last N days.

    Args:
        ticker: Stock ticker symbol
        days: Number of days of history (default 7)

    Returns:
        List of daily price records
    """
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)

        history = stock.history(start=start_date, end=end_date)

        records = []
        for date, row in history.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })

        return records

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def get_price_change(ticker: str):
    """
    Calculates price change percentage from previous close.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with price change info
    """
    try:
        stock_info = get_stock_price(ticker)

        current = stock_info.get("current_price")
        previous = stock_info.get("previous_close")

        if current and previous and current != "N/A" and previous != "N/A":
            change = current - previous
            change_pct = (change / previous) * 100

            return {
                "ticker": ticker.upper(),
                "current_price": round(current, 2),
                "previous_close": round(previous, 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "direction": "UP 📈" if change >= 0 else "DOWN 📉",
                "currency": stock_info.get("currency", "USD")
            }
        else:
            return {"error": "Price data unavailable", "ticker": ticker}

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


if __name__ == "__main__":
    ticker = "TSLA"

    print(f"\n{'='*60}")
    print(f"  Stock Analysis: {ticker}")
    print(f"{'='*60}")

    # Current price info
    print("\n📊 Current Stock Info:")
    print("-" * 40)
    info = get_stock_price(ticker)
    for key, value in info.items():
        print(f"  {key:<20}: {value}")

    # Price change
    print("\n📈 Price Change:")
    print("-" * 40)
    change = get_price_change(ticker)
    for key, value in change.items():
        print(f"  {key:<20}: {value}")

    # Price history
    print("\n📅 Last 7 Days History:")
    print("-" * 40)
    history = get_price_history(ticker, days=7)
    for record in history:
        print(f"  {record['date']} | Open: {record['open']} | "
              f"Close: {record['close']} | High: {record['high']} | "
              f"Low: {record['low']}")