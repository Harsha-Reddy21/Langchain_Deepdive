# 📈 Real-Time Stock Market Chat Application

A modern, real-time stock market chat application built with **Streamlit**, **LangChain**, **OpenAI**, and **Pinecone**. Get live market data, AI-powered stock recommendations, and trending financial news through a ChatGPT-like interface.

---

## 🚀 Features

### Core Functionality
- **ChatGPT-like Real-time Chat Interface**: Interactive, streaming chat with AI stock advisor
- **Live Stock Data**: Real-time price and historical data using Yahoo Finance
- **Trending Financial News**: Latest market news from NewsAPI
- **AI Stock Recommendations**: Personalized, context-aware recommendations using LangChain RAG
- **Market Overview**: Live tracking of S&P 500, Dow Jones, and NASDAQ
- **Vector Database**: Pinecone for storing and retrieving news, reports, and market data
- **Error Handling**: User-friendly error messages for missing data, API issues, etc.
- **Unit Tests**: Test script for all major components

### Technical Highlights
- **LangChain RAG**: Retrieval-Augmented Generation for context-aware answers
- **Streamlit Chat UI**: Modern, conversational interface with avatars and message streaming
- **Concurrent Sessions**: Stateless backend supports multiple users and sessions
- **Dynamic Knowledge Base**: Update news and market data on demand
- **Robust Symbol Extraction**: Maps company names ("tesla") to tickers ("TSLA")
- **Beautiful Market Overview**: Modern card UI for indices

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- API keys for OpenAI, Pinecone, NewsAPI

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Stock_Market_Chat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```
   Example `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=us-east-1-aws
   PINECONE_INDEX_NAME=stock-market-chat
   NEWS_API_KEY=your_newsapi_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  # (optional)
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **(Optional) Run unit tests**
   ```bash
   python test_app.py
   ```

---

## 📊 Usage

- **Chat**: Ask about any stock, e.g. "What is the price of Tesla?", "Recommend a tech stock", "Show me news about Apple".
- **Market Overview**: See live S&P 500, Dow Jones, and NASDAQ data.
- **News Feed**: Get the latest financial news headlines.
- **Stock Cards**: See price, change, and chart for recently mentioned stocks.
- **Knowledge Base**: Update news and market data with one click.

---

## 🏗️ Architecture

```
Stock_Market_Chat/
├── config.py              # Environment/config management
├── data_fetchers.py       # Stock/news fetchers, symbol mapping
├── vector_store.py        # Pinecone vector DB integration
├── chat_engine.py         # LangChain RAG, chat logic
├── streamlit_app.py       # Streamlit UI (ChatGPT-like)
├── test_app.py            # Unit/component tests
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🔧 Configuration

- **Yahoo Finance**: Used for all live price and historical data
- **NewsAPI**: Used for trending financial news
- **Pinecone**: Used for vector database (news, reports, market data)
- **OpenAI**: Used for AI-powered chat and recommendations
- **Alpha Vantage**: (Optional, not used by default)

---

## 🧪 Testing

- Run `python test_app.py` to verify all major components (config, data fetchers, vector store, chat engine)
- All tests should pass if API keys are set and network is available

---

