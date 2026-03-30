from langchain_community.tools import DuckDuckGoSearchResults

def fetch_market_news(query: str, asset_type: str = "stock") -> str:
    """Fetch recent news and search results contextually based on asset type."""
    try:
        search = DuckDuckGoSearchResults()
        term = "mutual fund performance OR news" if asset_type == "mutual_fund" else "stock financial news OR market sentiment"
        results = search.run(f"{query} {term}")
        return results
    except Exception as e:
        return f"Error fetching news for {query}: {str(e)}"
