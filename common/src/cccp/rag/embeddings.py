
import os
import shutil
import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
#from langchain_postgres import PostgresVectorStore
#import psycopg
from langchain.prompts import PromptTemplate
#from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load PDF documents
pdf_paths = [
    "../rag/docs/01_policy_overview.pdf",
    "../rag/docs/02_return_eligibility.pdf",
    "../rag/docs/03_non_returnable_items.pdf",
    "../rag/docs/04_return_process.pdf",
    "../rag/docs/05_refund_policy.pdf",
    "../rag/docs/06_exchange_policy.pdf",
    "../rag/docs/07_contact_information.pdf",
]
loaders = [PyPDFLoader(path) for path in pdf_paths]
docs = []
for loader in loaders:
    docs.extend(loader.load())
print(f"Loaded {len(docs)} documents from PDFs.")

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=25)
texts = text_splitter.split_documents(docs)
print(f"Split into {len(texts)} chunks.")

# Embedding model
modelPath = "mixedbread-ai/mxbai-embed-large-v1"
model_kwargs = {'device': device}
encode_kwargs = {'normalize_embeddings': False}
embedding = HuggingFaceEmbeddings(
    model_name=modelPath,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Create and store embeddings in vector DB--TODO
persist_directory = './embeddings/chroma/'
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)
os.makedirs(persist_directory, exist_ok=True)

# Define Postgres connection details
# postgres_connection = {
#     "host": "localhost",
#     "port": 5432,
#     "user": "postgres",
#     "password": "Harige*1",
#     "database": "evershop",
# }

# vectordb = PostgresVectorStore.from_documents(
#     documents=texts,
#     embedding=embedding,
#     connection_args=postgres_connection,
#     table_name="embeddings_table"
# )

vectordb = Chroma.from_documents(
    documents=texts,                    # splits we created earlier
    embedding=embedding,
    persist_directory=persist_directory, # save the directory
)

print(f"Vector DB created with {vectordb._collection.count()} chunks.")
# vectordb.persist()  # Uncomment if you want to persist the DB

# --- Similarity Search Example ---
question = "What is the exchange policy?"
docs = vectordb.similarity_search(question, k=3)
print(f"\n--- Similarity Search ---")
print(f"Found {len(docs)} similar documents:")
for i, doc in enumerate(docs):
    print(f"Doc {i+1}: {doc.page_content[:200]}...\n")


# --- Max Marginal Relevance (MMR) Search Example ---
docs_with_mmr = vectordb.max_marginal_relevance_search(question, k=3, fetch_k=6)
print(f"\n--- Max Marginal Relevance (MMR) Search ---")
print(f"Found {len(docs_with_mmr)} MMR documents:")
for i, doc in enumerate(docs_with_mmr):
    print(f"MMR Doc {i+1}: {doc.page_content[:200]}...\n")