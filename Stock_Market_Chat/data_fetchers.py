import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import get_news_api_key, get_alpha_vantage_api_key

def fetch_stock_price(symbol: str) -> Dict:
    """Fetch current stock price and basic info using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        return {
            "symbol": symbol.upper(),
            "price": current_price,
            "change": info.get('regularMarketChange', 0),
            "change_percent": info.get('regularMarketChangePercent', 0),
            "volume": info.get('volume', 0),
            "market_cap": info.get('marketCap', 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}

def fetch_stock_history(symbol: str, period: str = "1mo") -> Dict:
    """Fetch historical stock data."""
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        
        return {
            "symbol": symbol.upper(),
            "data": history.to_dict('records'),
            "period": period
        }
    except Exception as e:
        return {"error": f"Failed to fetch history for {symbol}: {str(e)}"}

def fetch_financial_news(query: str = "stock market", count: int = 10) -> List[Dict]:
    """Fetch financial news from NewsAPI."""
    api_key = get_news_api_key()
    if not api_key:
        return []
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": count,
            "domains": "reuters.com,bloomberg.com,cnbc.com,marketwatch.com"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        return [
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", "")
            }
            for article in articles
        ]
    except Exception as e:
        return []

def fetch_market_trends() -> Dict:
    """Fetch general market trends and indices."""
    try:
        # Fetch major indices
        indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        trends = {}
        
        for index in indices:
            ticker = yf.Ticker(index)
            info = ticker.info
            trends[index] = {
                "name": info.get("longName", index),
                "price": info.get("currentPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0)
            }
        
        return trends
    except Exception as e:
        return {"error": f"Failed to fetch market trends: {str(e)}"}

def search_stock_symbol(company_name: str) -> List[str]:
    """Search for stock symbols by company name using yfinance's Ticker and fallback to yfinance's built-in search."""
    try:
        # Try yfinance's Ticker.info first
        ticker = yf.Ticker(company_name)
        info = ticker.info
        if info.get("symbol") and info.get("regularMarketPrice", 0) > 0:
            return [info["symbol"]]
        # Fallback: use yfinance's built-in search (returns a DataFrame)
        search = yf.utils.get_tickers(company_name)
        if search:
            return [search[0]]
        # Fallback: try common variations
        variations = [
            company_name.upper(),
            company_name.replace(" ", "").upper(),
            company_name.split()[0].upper()
        ]
        results = []
        for var in variations:
            try:
                ticker = yf.Ticker(var)
                if ticker.info.get("symbol") and ticker.info.get("regularMarketPrice", 0) > 0:
                    results.append(ticker.info["symbol"])
            except:
                continue
        return list(set(results))
    except Exception as e:
        return []

def get_symbol_from_query(query: str) -> Optional[str]:
    """Given a user query, try to extract a valid US stock symbol or map a company name to a symbol. Only return if the symbol is valid and active."""
    import re
    # Try to extract a symbol (1-5 uppercase letters)
    match = re.search(r'\b([A-Z]{1,5})\b', query.upper())
    if match:
        symbol = match.group(1)
        # Validate symbol with yfinance
        ticker = yf.Ticker(symbol)
        try:
            info = ticker.info
            if info.get("regularMarketPrice", 0) > 0 and info.get("quoteType", "") == "EQUITY" and info.get("exchange", "").startswith("N"):  # NYSE/NASDAQ
                print(f"[DEBUG] get_symbol_from_query: Using extracted symbol {symbol}")
                return symbol
        except:
            pass
    # If not found, try to map company name
    results = search_stock_symbol(query)
    for sym in results:
        ticker = yf.Ticker(sym)
        try:
            info = ticker.info
            if info.get("regularMarketPrice", 0) > 0 and info.get("quoteType", "") == "EQUITY" and info.get("exchange", "").startswith("N"):
                print(f"[DEBUG] get_symbol_from_query: Using mapped symbol {sym}")
                return sym
        except:
            continue
    print(f"[DEBUG] get_symbol_from_query: No valid symbol found for query '{query}'")
    return None 