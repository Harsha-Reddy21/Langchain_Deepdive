#!/usr/bin/env python3
"""
Simple test script to verify the basic functionality of the Stock Market Chat application.
Run this script to test individual components before running the full application.
"""

import sys
import os
from datetime import datetime

def test_config():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        from config import get_openai_api_key, get_pinecone_config, get_news_api_key
        from config import validate_config
        
        # Test individual config functions
        openai_key = get_openai_api_key()
        pinecone_config = get_pinecone_config()
        news_key = get_news_api_key()
        
        print(f"✅ OpenAI API Key: {'Set' if openai_key else 'Not set'}")
        print(f"✅ Pinecone API Key: {'Set' if pinecone_config['api_key'] else 'Not set'}")
        print(f"✅ News API Key: {'Set' if news_key else 'Not set'}")
        
        # Test validation
        try:
            validate_config()
            print("✅ Configuration validation passed")
        except ValueError as e:
            print(f"⚠️ Configuration validation failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_data_fetchers():
    """Test data fetching functions."""
    print("\n📊 Testing data fetchers...")
    try:
        from data_fetchers import fetch_stock_price, fetch_market_trends, fetch_financial_news
        
        # Test stock price fetching
        print("Testing stock price fetching...")
        stock_data = fetch_stock_price("AAPL")
        if "error" not in stock_data:
            print(f"✅ AAPL Price: ${stock_data['price']:.2f}")
        else:
            print(f"⚠️ Stock price fetch failed: {stock_data['error']}")
        
        # Test market trends
        print("Testing market trends...")
        trends = fetch_market_trends()
        if "error" not in trends:
            print(f"✅ Market trends fetched: {len(trends)} indices")
        else:
            print(f"⚠️ Market trends fetch failed: {trends['error']}")
        
        # Test news fetching
        print("Testing news fetching...")
        news = fetch_financial_news(count=3)
        if news:
            print(f"✅ News fetched: {len(news)} articles")
        else:
            print("⚠️ News fetch failed or returned empty")
        
        return True
    except Exception as e:
        print(f"❌ Data fetchers test failed: {e}")
        return False

def test_vector_store():
    """Test vector store operations."""
    print("\n🗄️ Testing vector store...")
    try:
        # Test if required packages are installed
        try:
            import pinecone
            from langchain_community.embeddings import OpenAIEmbeddings
            from langchain_pinecone import Pinecone
            print("✅ Required packages imported successfully")
        except ImportError as e:
            print(f"❌ Missing required packages: {e}")
            print("Please install: pip install pinecone langchain-pinecone langchain-community")
            return False
        
        from vector_store import init_pinecone, create_documents_from_news
        
        # Test Pinecone initialization
        print("Testing Pinecone initialization...")
        try:
            index = init_pinecone()
            print("✅ Pinecone initialized successfully")
        except Exception as e:
            print(f"⚠️ Pinecone initialization failed: {e}")
            print("This might be due to missing API keys or network issues")
            return False
        
        # Test document creation
        print("Testing document creation...")
        test_news = [{
            "title": "Test Article",
            "description": "This is a test article for vector store testing",
            "content": "Test content for vector store operations",
            "source": "Test Source",
            "published_at": datetime.now().isoformat(),
            "url": "https://test.com"
        }]
        
        documents = create_documents_from_news(test_news)
        print(f"✅ Created {len(documents)} test documents")
        
        return True
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_chat_engine():
    """Test chat engine functionality."""
    print("\n💬 Testing chat engine...")
    try:
        # Test if required packages are installed
        try:
            from langchain_community.chat_models import ChatOpenAI
            print("✅ LangChain community packages imported successfully")
        except ImportError as e:
            print(f"❌ Missing required packages: {e}")
            print("Please install: pip install langchain-community")
            return False
        
        from chat_engine import extract_stock_symbols, create_chat_model
        
        # Test stock symbol extraction
        print("Testing stock symbol extraction...")
        test_message = "What's the price of AAPL and TSLA?"
        symbols = extract_stock_symbols(test_message)
        print(f"✅ Extracted symbols: {symbols}")
        
        # Test chat model creation
        print("Testing chat model creation...")
        try:
            chat_model = create_chat_model()
            print("✅ Chat model created successfully")
        except Exception as e:
            print(f"⚠️ Chat model creation failed: {e}")
            print("This might be due to missing OpenAI API key")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Chat engine test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Stock Market Chat Application - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Data Fetchers", test_data_fetchers),
        ("Vector Store", test_vector_store),
        ("Chat Engine", test_chat_engine)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("1. Make sure all API keys are set in .env file")
        print("2. Run: streamlit run streamlit_app.py")
    else:
        print("⚠️ Some tests failed. Please check the configuration and API keys.")
        print("Make sure to set up your .env file with the required API keys.")
        print("\nCommon issues:")
        print("- Missing API keys in .env file")
        print("- Network connectivity issues")
        print("- Outdated packages (run: pip install -r requirements.txt)")

if __name__ == "__main__":
    main() 