import json
import chromadb
from chromadb.config import Settings

# Load knowledge base
with open('knowledge_base.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Flatten policies
policy_chunks = []
for section in data['company_policies']:
    section_name = section['section']
    for item in section['items']:
        text = f"Section: {section_name}\nTitle: {item['title']}\nDescription: {item['description']}"
        policy_chunks.append({
            "type": "policy",
            "section": section_name,
            "title": item["title"],
            "content": text
        })

# Flatten FAQs
faq_chunks = []
for faq in data['faqs']:
    text = f"Q: {faq['question']}\nA: {faq['answer']}"
    faq_chunks.append({
        "type": "faq",
        "question": faq["question"],
        "content": text
    })

# Flatten Templates
template_chunks = []
for template in data['response_templates']:
    text = f"Template Name: {template['template_name']}\nTemplate: {template['template']}"
    template_chunks.append({
        "type": "template",
        "template_name": template["template_name"],
        "content": text
    })

# Combine all chunks
def get_all_chunks():
    return policy_chunks + faq_chunks + template_chunks

# Store in ChromaDB
chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = chroma_client.get_or_create_collection("company_knowledge")

def index_knowledge():
    all_chunks = get_all_chunks()
    # Remove existing docs (optional, for fresh indexing)
    try:
        collection.delete(where={})
    except Exception:
        pass
    for idx, chunk in enumerate(all_chunks):
        collection.add(
            documents=[chunk["content"]],
            ids=[f"doc_{idx}"],
            metadatas=[chunk]
        )
    print(f"Stored {len(all_chunks)} documents in ChromaDB.")

def search_knowledge(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        print("----")
        print(doc)
        print("Metadata:", meta)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        index_knowledge()
    elif len(sys.argv) > 2 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:])
        search_knowledge(query)
    else:
        print("Usage:")
        print("  python rag.py index         # Index the knowledge base")
        print("  python rag.py search <query>  # Search the knowledge base") 