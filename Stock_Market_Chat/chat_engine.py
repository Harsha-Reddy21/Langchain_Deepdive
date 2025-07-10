from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from typing import List, Dict, Optional
import json
from config import get_openai_api_key
from vector_store import get_vector_store, search_vector_store
from data_fetchers import fetch_stock_price, fetch_financial_news, fetch_market_trends, get_symbol_from_query

def create_chat_model():
    """Create OpenAI chat model with streaming."""
    return ChatOpenAI(
        openai_api_key=get_openai_api_key(),
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        streaming=True
    )

def create_memory():
    """Create conversation memory."""
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

def create_qa_prompt():
    """Create custom prompt for stock market Q&A."""
    template = """You are a knowledgeable stock market analyst and financial advisor. 
    Use the following context to answer the user's question about stocks, market trends, and financial news.
    
    Context: {context}
    
    Chat History: {chat_history}
    
    Human: {question}
    
    Assistant: Provide a helpful, accurate response based on the context. If the context doesn't contain relevant information, 
    you can provide general financial advice but clearly state that you're giving general information. 
    Always be professional and considerate of the user's financial decisions."""
    
    return PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template
    )

def create_qa_chain():
    """Create conversational retrieval chain."""
    vector_store = get_vector_store()
    chat_model = create_chat_model()
    memory = create_memory()
    prompt = create_qa_prompt()
    
    return ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    )

def extract_stock_symbols(message: str) -> List[str]:
    """Extract potential stock symbols from user message."""
    import re
    
    # Common stock symbol patterns
    patterns = [
        r'\b[A-Z]{1,5}\b',  # 1-5 uppercase letters
        r'\$[A-Z]{1,5}\b',  # $ followed by 1-5 uppercase letters
    ]
    
    symbols = []
    for pattern in patterns:
        matches = re.findall(pattern, message.upper())
        symbols.extend(matches)
    
    # Remove duplicates and common words
    common_words = {'THE', 'AND', 'FOR', 'ARE', 'YOU', 'ALL', 'NEW', 'TOP', 'GET', 'NOW'}
    symbols = [s.replace('$', '') for s in symbols if s.replace('$', '') not in common_words]
    
    return list(set(symbols))

def get_relevant_context(user_message: str) -> str:
    """Get relevant context from vector store for user message."""
    # Search for relevant documents
    search_results = search_vector_store(user_message, k=3)
    
    if not search_results:
        return ""
    
    # Combine relevant content
    context_parts = []
    for result in search_results:
        if result["score"] < 0.8:  # Only include highly relevant results
            context_parts.append(result["content"])
    
    return "\n\n".join(context_parts)

def generate_stock_recommendation(symbol: str, context: str) -> str:
    """Generate stock recommendation based on current data and context."""
    # Fetch current stock data
    stock_data = fetch_stock_price(symbol)
    print(f"[DEBUG] generate_stock_recommendation: stock_data for {symbol}: {stock_data}")
    if "error" in stock_data or stock_data.get('price', 0) == 0:
        return f"Sorry, I couldn't fetch a valid current price for {symbol}. Please check the symbol or try again later."
    # Create recommendation prompt
    prompt = f"""You are a financial assistant. Here is the latest data for {symbol}:

Stock Data:
- Price: ${stock_data['price']:.2f}
- Change: ${stock_data['change']:.2f} ({stock_data['change_percent']:.2f}%)
- Volume: {stock_data['volume']:,}
- Market Cap: ${stock_data['market_cap']:,}

Market Context:
{context}

Based on the above, provide a brief, actionable recommendation for {symbol} in 2-3 sentences. If the data is insufficient, say so."""
    chat_model = create_chat_model()
    response = chat_model.predict(prompt)
    return response

def process_user_message(user_message: str, chat_history: List[Dict]) -> Dict:
    """Process user message and generate response."""
    # Try to extract a valid stock symbol or map company name
    symbol = get_symbol_from_query(user_message)
    symbols = [symbol] if symbol else []
    
    # Get relevant context
    context = get_relevant_context(user_message)
    
    # Check if user is asking about specific stocks
    if symbol and any(word in user_message.lower() for word in ['price', 'stock', 'recommend', 'analysis']):
        # Generate stock-specific response
        response = generate_stock_recommendation(symbol, context)
        
        return {
            "response": response,
            "symbols": symbols,
            "context_used": bool(context)
        }
    
    # Use general QA chain for other questions
    try:
        qa_chain = create_qa_chain()
        
        # Add chat history to memory
        for msg in chat_history[-5:]:  # Keep last 5 messages
            if msg["role"] == "user":
                qa_chain.memory.chat_memory.add_user_message(msg["content"])
            else:
                qa_chain.memory.chat_memory.add_ai_message(msg["content"])
        
        # Generate response
        result = qa_chain({"question": user_message})
        
        return {
            "response": result["answer"],
            "symbols": symbols,
            "context_used": bool(context),
            "sources": [doc.metadata for doc in result.get("source_documents", [])]
        }
    
    except Exception as e:
        return {
            "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
            "symbols": symbols,
            "context_used": False
        }

def update_knowledge_base():
    """Update knowledge base with latest news and market data."""
    # Fetch latest news
    news = fetch_financial_news(count=20)
    
    # Fetch market trends
    trends = fetch_market_trends()
    
    # Update vector store
    from vector_store import update_news_in_vector_store, update_stock_data_in_vector_store
    
    if news:
        update_news_in_vector_store(news)
    
    if "error" not in trends:
        for symbol, data in trends.items():
            update_stock_data_in_vector_store({
                "symbol": symbol,
                "price": data["price"],
                "change": data["change"],
                "change_percent": data["change_percent"],
                "volume": 0,
                "market_cap": 0,
                "timestamp": "2024-01-01T00:00:00"
            })
    
    return len(news) if news else 0 