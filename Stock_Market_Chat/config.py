import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key():
    """Get OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")

def get_pinecone_config():
    """Get Pinecone configuration from environment variables."""
    return {
        "api_key": os.getenv("PINECONE_API_KEY"),
        "environment": os.getenv("PINECONE_ENVIRONMENT"),
        "index_name": os.getenv("PINECONE_INDEX_NAME", "stock-market-chat")
    }

def get_news_api_key():
    """Get News API key from environment variables."""
    return os.getenv("NEWS_API_KEY")

def get_alpha_vantage_api_key():
    """Get Alpha Vantage API key from environment variables."""
    return os.getenv("ALPHA_VANTAGE_API_KEY")

def validate_config():
    """Validate that all required API keys are present."""
    required_keys = {
        "OpenAI": get_openai_api_key(),
        "Pinecone": get_pinecone_config()["api_key"],
        "News API": get_news_api_key()
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    return True 