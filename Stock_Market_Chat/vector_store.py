
from pinecone import Pinecone, ServerlessSpec
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Optional
import json
from config import get_pinecone_config, get_openai_api_key

def init_pinecone():
    """Initialize Pinecone client and index using new API."""
    config = get_pinecone_config()
    pc = Pinecone(api_key=config["api_key"])
    index_name = config["index_name"]
    # Create index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return pc.Index(index_name)

def get_vector_store():
    """Get initialized Pinecone vector store using new API."""
    embeddings = OpenAIEmbeddings(openai_api_key=get_openai_api_key())
    config = get_pinecone_config()
    pc = Pinecone(api_key=config["api_key"])
    index = pc.Index(config["index_name"])
    return PineconeVectorStore(index, embeddings)

def create_documents_from_news(news_articles: List[Dict]) -> List[Document]:
    """Convert news articles to LangChain documents."""
    documents = []
    for article in news_articles:
        content = f"Title: {article.get('title', '')}\n"
        content += f"Description: {article.get('description', '')}\n"
        content += f"Content: {article.get('content', '')}\n"
        content += f"Source: {article.get('source', '')}\n"
        content += f"Published: {article.get('published_at', '')}"
        metadata = {
            "type": "news",
            "title": article.get('title', ''),
            "source": article.get('source', ''),
            "published_at": article.get('published_at', ''),
            "url": article.get('url', '')
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def create_documents_from_stock_data(stock_data: Dict) -> List[Document]:
    """Convert stock data to LangChain documents."""
    content = f"Stock Symbol: {stock_data.get('symbol', '')}\n"
    content += f"Current Price: ${stock_data.get('price', 0):.2f}\n"
    content += f"Change: ${stock_data.get('change', 0):.2f}\n"
    content += f"Change Percent: {stock_data.get('change_percent', 0):.2f}%\n"
    content += f"Volume: {stock_data.get('volume', 0):,}\n"
    content += f"Market Cap: ${stock_data.get('market_cap', 0):,}\n"
    content += f"Timestamp: {stock_data.get('timestamp', '')}"
    metadata = {
        "type": "stock_data",
        "symbol": stock_data.get('symbol', ''),
        "timestamp": stock_data.get('timestamp', '')
    }
    return [Document(page_content=content, metadata=metadata)]

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_documents(documents)

def add_documents_to_vector_store(documents: List[Document]):
    """Add documents to Pinecone vector store."""
    try:
        vector_store = get_vector_store()
        split_docs = split_documents(documents)
        vector_store.add_documents(split_docs)
        return True
    except Exception as e:
        print(f"Error adding documents to vector store: {e}")
        return False

def search_vector_store(query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
    """Search vector store for relevant documents."""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(
            query, 
            k=k,
            filter=filter_dict
        )
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]
    except Exception as e:
        print(f"Error searching vector store: {e}")
        return []

def update_news_in_vector_store(news_articles: List[Dict]):
    """Update vector store with new news articles."""
    documents = create_documents_from_news(news_articles)
    return add_documents_to_vector_store(documents)

def update_stock_data_in_vector_store(stock_data: Dict):
    """Update vector store with new stock data."""
    documents = create_documents_from_stock_data(stock_data)
    return add_documents_to_vector_store(documents)

def clear_vector_store():
    """Clear all documents from vector store."""
    try:
        pc = Pinecone(api_key=get_pinecone_config()["api_key"])
        index = pc.Index(get_pinecone_config()["index_name"])
        index.delete(delete_all=True)
        return True
    except Exception as e:
        print(f"Error clearing vector store: {e}")
        return False 