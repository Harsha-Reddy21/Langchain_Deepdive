# server.py
import os
import base64
import json
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from fastmcp import FastMCP
import chromadb
from chromadb.config import Settings
import openai
import redis

mcp = FastMCP("Demo 🚀")

# Gmail API setup
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

# --- RAG/ChromaDB Setup ---
chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = chroma_client.get_or_create_collection("company_knowledge")

# --- OpenAI LLM Setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Redis Caching Setup ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# --- Caching Helpers ---
def cache_get(key):
    return redis_client.get(key)

def cache_set(key, value, ex=3600):
    redis_client.set(key, value, ex=ex)

# --- RAG Search Function ---
def semantic_search(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    return list(zip(docs, metas))

# --- Cached Semantic Search ---
def cached_semantic_search(query, n_results=3):
    cache_key = f"semantic:{query}:{n_results}"
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)
    results = semantic_search(query, n_results)
    cache_set(cache_key, json.dumps(results))
    return results

# --- LLM Response Generation ---
def generate_llm_response(query, context_chunks):
    context_text = "\n\n".join([doc for doc, meta in context_chunks])
    prompt = f"""
You are an intelligent HR assistant. Use the following company knowledge to answer the user's question. Be concise, accurate, and polite.

Company Knowledge:
{context_text}

User Question:
{query}

Response:
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# --- Cached LLM Response ---
def cached_llm_response(query, context_chunks):
    context_text = "\n\n".join([doc for doc, meta in context_chunks])
    cache_key = f"llm:{query}:{hash(context_text)}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    response = generate_llm_response(query, context_chunks)
    cache_set(cache_key, response)
    return response

# --- Gmail API Auth ---
def get_gmail_service():
    """Get authenticated Gmail service"""
    creds = None
    
    # Load credentials from token.json
    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token:
                token_data = json.load(token)
            
            creds = Credentials(
                token=None,  # We'll refresh this
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes', SCOPES)
            )
        except Exception as e:
            print(f"Error loading token.json: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            # Use credential.json for OAuth client configuration
            if not os.path.exists('credential.json'):
                raise FileNotFoundError("credential.json not found. Please provide your OAuth client credentials as credential.json.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credential.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                token_data = {
                    'refresh_token': creds.refresh_token,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'token_uri': creds.token_uri,
                    'scopes': creds.scopes
                }
                
                with open('token.json', 'w') as token:
                    json.dump(token_data, token, indent=2)
                    
            except Exception as e:
                import traceback
                print("Error during OAuth flow:", repr(e))
                traceback.print_exc()
                raise Exception("Failed to authenticate with Google. Please check your credential.json.")
    
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload):
    """Extract email body from Gmail API payload"""
    if not payload:
        return ""
    
    # If payload has body data
    if payload.get('body') and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    # If payload has parts (multipart email)
    if payload.get('parts'):
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                if part.get('body') and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    
    return "(No body content)"

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool
def get_mails(limit: int = 10, query: str = "") -> List[Dict[str, Any]]:
    """Fetch emails from Gmail inbox
    
    Args:
        limit: Maximum number of emails to return (default: 10)
        query: Gmail search query (e.g., "from:example@gmail.com", "subject:meeting")
    
    Returns:
        List of email objects with id, subject, from, date, and body
    """
    try:
        service = get_gmail_service()
        
        # Get list of messages
        response = service.users().messages().list(
            userId='me',
            maxResults=limit,
            q=query
        ).execute()
        
        messages = response.get('messages', [])
        email_details = []
        
        for msg in messages:
            # Get full message details
            detail = service.users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()
            
            # Extract headers
            headers = detail['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            body = extract_email_body(detail['payload'])
            
            email_details.append({
                'id': msg['id'],
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body[:500] + '...' if len(body) > 500 else body  # Truncate long bodies
            })
        
        return email_details
        
    except Exception as e:
        return [{"error": f"Failed to fetch emails: {str(e)}"}]

@mcp.tool  
def send_mail(
    to: str,
    subject: str,
    body: str = "",
    user_query: str = "",
    auto_respond: bool = False
) -> str:
    """Send email via Gmail. If auto_respond is True or body is empty, generate the body using company knowledge and LLM.
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content (optional)
        user_query: The question or context to answer (for auto-respond)
        auto_respond: If True, generate the body automatically
    Returns:
        Success message with message ID or error message
    """
    try:
        # If auto_respond is requested or body is empty, generate the body
        if auto_respond or not body:
            if not user_query:
                return "Error: user_query must be provided for auto-responding."
            context_chunks = cached_semantic_search(user_query, n_results=3)
            body = cached_llm_response(user_query, context_chunks)
        service = get_gmail_service()
        message = {
            'raw': base64.urlsafe_b64encode(
                f'To: {to}\r\n'
                f'Subject: {subject}\r\n'
                f'Content-Type: text/plain; charset=utf-8\r\n'
                f'MIME-Version: 1.0\r\n'
                f'\r\n'
                f'{body}'.encode('utf-8')
            ).decode('utf-8').rstrip('=')
        }
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        return f"Email sent successfully! Message ID: {sent_message['id']}\n\nResponse:\n{body}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@mcp.tool  
def intelligent_send_mail(to: str, subject: str, user_query: str) -> str:
    """Generate an intelligent email response using company knowledge and send it via Gmail.
    Args:
        to: Recipient email address
        subject: Email subject
        user_query: The question or context to answer (e.g., the incoming email body)
    Returns:
        Success message with message ID or error message
    """
    try:
        # 1. Semantic search for relevant knowledge
        context_chunks = cached_semantic_search(user_query, n_results=3)
        # 2. Generate response using LLM
        llm_response = cached_llm_response(user_query, context_chunks)
        # 3. Send the email
        service = get_gmail_service()
        message = {
            'raw': base64.urlsafe_b64encode(
                f'To: {to}\r\n'
                f'Subject: {subject}\r\n'
                f'Content-Type: text/plain; charset=utf-8\r\n'
                f'MIME-Version: 1.0\r\n'
                f'\r\n'
                f'{llm_response}'.encode('utf-8')
            ).decode('utf-8').rstrip('=')
        }
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        return f"Email sent successfully! Message ID: {sent_message['id']}\n\nResponse:\n{llm_response}"
    except Exception as e:
        return f"Failed to send intelligent email: {str(e)}"

# --- Batch Email Processing ---
def batch_auto_respond(email_list):
    results = []
    for email in email_list:
        to = email.get('to')
        subject = email.get('subject')
        user_query = email.get('user_query')
        # Use cached semantic search and LLM
        context_chunks = cached_semantic_search(user_query, n_results=3)
        body = cached_llm_response(user_query, context_chunks)
        result = send_mail(to=to, subject=subject, body=body)
        results.append({'to': to, 'subject': subject, 'result': result})
    return results

@mcp.tool
def batch_respond_to_emails(email_batch: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Batch auto-respond to a list of emails using company knowledge and LLM with caching.
    Args:
        email_batch: List of dicts with keys 'to', 'subject', 'user_query'
    Returns:
        List of dicts with 'to', 'subject', and 'result' (send_mail result)
    """
    return batch_auto_respond(email_batch)

if __name__ == "__main__":
    mcp.run()


