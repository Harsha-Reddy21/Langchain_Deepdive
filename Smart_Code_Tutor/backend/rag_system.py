import os
import json
import asyncio
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Initialize LangChain components
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Documentation database
docs_db = None

def initialize_documentation():
    """Initialize the documentation database with coding best practices"""
    global docs_db
    
    if docs_db is not None:
        return docs_db
    
    # Load documentation from JSON file
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'documentation_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            documentation = data['documentation']
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Could not load documentation from JSON file: {e}")
        # Fallback to minimal documentation
        documentation = [
            {
                "content": "Python Basics: Use descriptive variable names, proper indentation, and handle exceptions with try/except blocks.",
                "metadata": {"language": "python", "topic": "basics"}
            },
            {
                "content": "JavaScript Basics: Use const/let instead of var, arrow functions, and proper error handling with try/catch.",
                "metadata": {"language": "javascript", "topic": "basics"}
            }
        ]
    
    # Create documents
    documents = []
    for doc in documentation:
        documents.append(Document(
            page_content=doc["content"],
            metadata=doc["metadata"]
        ))
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    split_docs = text_splitter.split_documents(documents)
    
    # Create vector store
    docs_db = FAISS.from_documents(split_docs, embeddings)
    
    return docs_db

async def get_code_explanation(code: str, language: str, context: str = "") -> str:
    """Get intelligent explanation for code using RAG"""
    
    # Initialize documentation if not already done
    vector_store = initialize_documentation()
    
    # Create retrieval chain
    prompt_template = PromptTemplate(
        input_variables=["query", "context"],
        template="""
        You are an expert programming tutor. Analyze the following code and provide a clear, step-by-step explanation.

        {query}

        Context from documentation:
        {context}

        Please provide:
        1. What the code does
        2. How it works step by step
        3. Any potential improvements or best practices
        4. Common pitfalls to avoid

        Be concise but thorough in your explanation.
        """
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt_template},
        input_key="query"
    )
    
    # Get relevant documentation
    query = f"Code Language: {language}\nCode Context: {context}\nCode to Explain: {code}"
    try:
        result = await qa_chain.ainvoke({"query": query})
        return result["result"]
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

async def get_error_solution(error_message: str, language: str) -> str:
    """Get solution for specific error using RAG"""
    
    vector_store = initialize_documentation()
    
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="""
        You are a programming expert. Help solve this error:
        
        {question}
        
        Provide:
        1. What caused this error
        2. How to fix it
        3. Prevention tips
        4. Example of correct code
        
        Be specific and actionable in your response.
        """
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
        chain_type_kwargs={"prompt": prompt_template}
    )
    
    try:
        result = await qa_chain.ainvoke({
            "query": error_message,
            "language": language
        })
        return result["result"]
    except Exception as e:
        return f"Error getting solution: {str(e)}"

async def get_coding_tips(language: str, topic: str = "general") -> str:
    """Get coding tips and best practices"""
    
    vector_store = initialize_documentation()
    
    query = f"Best practices and tips for {language} programming, focusing on {topic}"
    
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="""
        Provide helpful coding tips and best practices for:
        
        {question}
        
        Include:
        1. Key principles
        2. Common patterns
        3. Performance tips
        4. Code quality guidelines
        
        Make it practical and actionable.
        """
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt_template}
    )
    
    try:
        result = await qa_chain.ainvoke({
            "query": query,
            "language": language
        })
        return result["result"]
    except Exception as e:
        return f"Error getting tips: {str(e)}" 