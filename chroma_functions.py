import os
import chromadb
import openai
from chromadb.utils import embedding_functions
from openai import OpenAI

# Setup OpenAI embedding function
api_key = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = api_key
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-ada-002")

# Setup directories for database storage
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "chromadb_data")
os.makedirs(db_dir, exist_ok=True)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=db_dir)
collection_name = 'documents'  # Single collection name
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding



def get_or_create_collection(client, collection_name, embedding_function):
    try:
        collection = client.get_collection(name=collection_name, embedding_function=embedding_function)
        created = False
        print(f"Collection {collection_name} retrieved successfully.")
    except Exception as e:
        collection = client.create_collection(name=collection_name, embedding_function=embedding_function)
        created = True
        print(f"Collection {collection_name} created successfully.")
    return collection, created

def delete_collection(client, collection_name):
    try:
        client.delete_collection(name=collection_name)
        print(f"Collection {collection_name} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete collection {collection_name}: {e}")

def split_into_chunks(text, max_length=500):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def index_documents(folder_path='./docs'):
    if not folder_path or not os.path.exists(folder_path):
        raise ValueError("Folder path is invalid")

    # Check if the collection exists
    try:
        chroma_client.get_collection(name=collection_name)
        print(f"Collection {collection_name} already exists. Skipping indexing.")
        return
    except Exception as e:
        print(f"Collection {collection_name} does not exist. Proceeding with indexing.")

    # Create a new collection
    collection, created = get_or_create_collection(chroma_client, collection_name, openai_ef)
    print("Collection initialized:", created)

    # Process each text file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                chunks = split_into_chunks(text)

                for i, chunk in enumerate(chunks):
                    embedding = get_embedding(chunk)
                    metadata = {
                        "filename": filename,
                        "chunk_id": f"{filename}_chunk_{i}",
                        "chunk_text": chunk
                    }

                    collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[metadata['chunk_id']],
                        embeddings=[embedding]
                    )
                    print(f"Processed file: {filename}, chunk: {i}")

def query_documents(query_text):
    if not query_text:
        raise ValueError("Query text is required")

    collection, _ = get_or_create_collection(chroma_client, collection_name, openai_ef)
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas"]
    )

    if results and 'metadatas' in results and 'documents' in results:
        metadatas = results['metadatas'][0]
        documents = results['documents'][0]
        print('results', results)
        top_3_chunks = []
        unique_chunks = set()

        for metadata, document in zip(metadatas, documents):
            chunk_id = metadata.get('chunk_id', 'N/A')
            if chunk_id not in unique_chunks:
                top_3_chunks.append({
                    "filename": metadata.get('filename', 'No filename available'),
                    "chunk_id": chunk_id,
                    "chunk_text": document  # Retrieve the actual document text
                })
                unique_chunks.add(chunk_id)
        return top_3_chunks
    else:
        return []

# # Index documents if the script is run directly
# if __name__ == '__main__':
#     index_documents()
