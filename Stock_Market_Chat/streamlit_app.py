import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
from typing import List, Dict
import pandas as pd

# Import our modules
from config import validate_config
from data_fetchers import fetch_stock_price, fetch_market_trends, fetch_financial_news
from chat_engine import process_user_message, update_knowledge_base
from vector_store import init_pinecone

# Page configuration
st.set_page_config(
    page_title="Stock Market Chat",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stock-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .positive-change {
        color: #28a745;
        font-weight: bold;
    }
    .negative-change {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_stocks" not in st.session_state:
        st.session_state.current_stocks = []
    
    if "last_update" not in st.session_state:
        st.session_state.last_update = datetime.now()
    
    if "knowledge_base_updated" not in st.session_state:
        st.session_state.knowledge_base_updated = False

def display_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">📈 Real-Time Stock Market Chat</h1>', unsafe_allow_html=True)
    st.markdown("---")

def display_market_overview():
    """Display market overview with major indices (modern card UI)."""
    st.markdown('<h2 style="display:flex;align-items:center;"><span style="font-size:2rem;">📊</span> <span style="margin-left:0.5rem;">Market Overview</span></h2>', unsafe_allow_html=True)
    try:
        trends = fetch_market_trends()
        if "error" not in trends:
            col1, col2, col3 = st.columns(3)
            icons = ["📈", "🏛️", "💹"]
            for i, (symbol, data) in enumerate(trends.items()):
                with [col1, col2, col3][i]:
                    st.markdown(f"""
                    <div style='background:#fff;border-radius:1rem;padding:1.5rem 1rem 1rem 1rem;box-shadow:0 2px 8px #0001;min-height:170px;'>
                        <div style='font-size:2.2rem;'>{icons[i]}</div>
                        <div style='font-size:1.1rem;font-weight:700;color:#222;margin-bottom:0.5rem;'>{data['name']}</div>
                        <div style='font-size:2rem;font-weight:800;color:#1f77b4;'>${data['price']:,.2f}</div>
                        <div style='font-size:1.1rem;font-weight:600;color:{'#28a745' if data['change'] >= 0 else '#dc3545'};'>
                            {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Unable to fetch market data")
    except Exception as e:
        st.error(f"Error fetching market data: {e}")

def display_stock_price_chart(symbol: str):
    """Display stock price chart."""
    try:
        from data_fetchers import fetch_stock_history
        history_data = fetch_stock_history(symbol, "1mo")
        if "error" not in history_data:
            df = pd.DataFrame(history_data["data"])
            if not df.empty and 'Close' in df.columns:
                df['Date'] = pd.to_datetime(df.index)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df['Close'],
                    mode='lines',
                    name=f'{symbol} Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                fig.update_layout(
                    title=f"{symbol} - 1 Month Price Chart",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No chart data available for {symbol}.")
        else:
            st.error(f"Unable to fetch chart data for {symbol}")
    except Exception as e:
        st.error(f"Error creating chart: {e}")

def display_chat_interface():
    """Display the main chat interface with ChatGPT-like UI."""
    st.subheader("💬 Chat with AI Stock Advisor")
    # Use Streamlit's chat input and message components
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
    # Chat input at the bottom
    user_input = st.chat_input("Ask about stocks, market trends, or get recommendations...")
    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)
        with st.spinner("Analyzing..."):
            response_data = process_user_message(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_data["response"],
            "timestamp": datetime.now(),
            "symbols": response_data.get("symbols", []),
            "context_used": response_data.get("context_used", False)
        })
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response_data["response"])
        # Update current stocks if symbols were mentioned
        if response_data.get("symbols"):
            st.session_state.current_stocks.extend(response_data["symbols"])
            st.session_state.current_stocks = list(set(st.session_state.current_stocks))[-5:]  # Keep last 5

def display_stock_cards():
    """Display current stock cards."""
    if st.session_state.current_stocks:
        st.subheader("📈 Current Stocks")
        
        for symbol in st.session_state.current_stocks:
            try:
                stock_data = fetch_stock_price(symbol)
                
                if "error" not in stock_data:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="stock-card">
                            <h3>{symbol}</h3>
                            <h2>${stock_data['price']:.2f}</h2>
                            <p class="{'positive-change' if stock_data['change'] >= 0 else 'negative-change'}">
                                {stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)
                            </p>
                            <p>Volume: {stock_data['volume']:,}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        display_stock_price_chart(symbol)
                
                else:
                    st.error(f"Error fetching data for {symbol}")
            
            except Exception as e:
                st.error(f"Error displaying {symbol}: {e}")

def display_news_feed():
    """Display latest financial news."""
    st.subheader("📰 Latest Financial News")
    
    try:
        news = fetch_financial_news(count=5)
        
        if news:
            for article in news:
                with st.expander(f"{article['title']} - {article['source']}"):
                    st.write(article['description'])
                    if article['url']:
                        st.markdown(f"[Read more]({article['url']})")
        else:
            st.info("No news available at the moment")
    
    except Exception as e:
        st.error(f"Error fetching news: {e}")

def main():
    """Main application function."""
    try:
        # Validate configuration
        validate_config()
        
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # Auto-refresh toggle
            auto_refresh = st.checkbox("Auto-refresh data", value=True)
            
            if auto_refresh:
                st.info("Data will refresh every 30 seconds")
            
            # Clear chat history
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.session_state.current_stocks = []
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 Quick Actions")
            
            # Quick stock lookup
            quick_symbol = st.text_input("Quick Stock Lookup:", placeholder="e.g., AAPL")
            if st.button("Get Price"):
                if quick_symbol:
                    stock_data = fetch_stock_price(quick_symbol.upper())
                    if "error" not in stock_data:
                        st.success(f"{stock_data['symbol']}: ${stock_data['price']:.2f}")
                    else:
                        st.error(stock_data["error"])
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Market overview
            display_market_overview()
            
            # Chat interface
            display_chat_interface()
            
            # Stock cards
            display_stock_cards()
        
        with col2:
            # News feed
            display_news_feed()
            
            # System status
            st.subheader("🔧 System Status")
            st.info(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
            
            if st.session_state.knowledge_base_updated:
                st.success("Knowledge base recently updated")
            
            # Initialize Pinecone if needed
            try:
                init_pinecone()
                st.success("Vector database connected")
            except Exception as e:
                st.error(f"Vector database error: {e}")
    
    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please check your .env file and ensure all required API keys are set.")
    
    except Exception as e:
        st.error(f"Application Error: {e}")
        st.info("Please check the console for more details.")

if __name__ == "__main__":
    main() 