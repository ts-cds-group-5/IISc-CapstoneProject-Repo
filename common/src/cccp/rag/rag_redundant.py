import os
import numpy as np
from getpass import getpass
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Set your Hugging Face API key here or use getpass to input it securely
hfapi_key = "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"


print("Hugging Face API Key set.") 

from langchain_community.document_loaders import PyPDFLoader

# Load the PDF document

# Load PDF
pdf_paths = [
    #"rag/customer_return_policy.pdf",
    "../rag/docs/customer_return_policy.pdf"
]

loaders = [PyPDFLoader(path) for path in pdf_paths]

docs = []
for loader in loaders:
    docs.extend(loader.load())

print(f"Loaded {len(docs)} documents from PDFs.")
# Print the first document's content for verification
print(docs[0].page_content[:500])  # Print first 500 characters of the first document
print("Sample document content loaded.")    


from langchain_text_splitters import RecursiveCharacterTextSplitter
# Split the documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 250,
    chunk_overlap = 50
)

texts = text_splitter.split_documents(docs)
print(f"Split into {len(texts)} chunks.")
print("Sample chunk content:", texts[0].page_content[:500])  # Print first 500 characters of the first chunk

print("Document splitting completed.")

#print splitted texts

print("Sample splitted text chunk:", texts)





import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")


#embedding = HuggingFaceHubEmbeddings()

# Embedding Model

#from langchain_huggingface import HuggingFaceEmbeddings

modelPath ="mixedbread-ai/mxbai-embed-large-v1"                  # Model card: https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1
                                                                 # Find other Emb. models at: https://huggingface.co/spaces/mteb/leaderboard

# Create a dictionary with model configuration options, specifying to use the CPU for computations
model_kwargs = {'device': device}      # cuda/cpu

# Create a dictionary with encoding options, specifically setting 'normalize_embeddings' to False
encode_kwargs = {'normalize_embeddings': False}

embedding =  HuggingFaceEmbeddings(
    model_name=modelPath,     # Provide the pre-trained model's path
    model_kwargs=model_kwargs, # Pass the model configuration options
    encode_kwargs=encode_kwargs # Pass the encoding options
)


print("I AM HERE****")
print("embedding", embedding)


# Create and store the embeddings in a vector database

import shutil
import os
from langchain_chroma import Chroma # Light-weight and in memory

# Define the directory
persist_directory = './embeddings/chroma/'

# Step 1: Remove old directory (if exists) safely
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)

# Step 2: Ensure parent directory exists
os.makedirs(persist_directory, exist_ok=True)

vectordb = Chroma.from_documents(
    documents=texts,                    # splits we created earlier
    embedding=embedding,
    persist_directory=persist_directory, # save the directory
)

print(vectordb._collection.count()) # same as number of splits

question = "What is the return policy?"
docs = vectordb.similarity_search(question,k=3) # k --> No. of doc as return
print(len(docs))
print(docs[0].page_content)
print(docs[1].page_content)
print(docs[2].page_content)

print("Similarity search completed.:question", question)

question= 'how exchange works?'
docs = vectordb.similarity_search(question,k=2)
print(len(docs))
print(docs[0].page_content)
print(docs[1].page_content) 
print("Similarity search completed.:question", question)


# Max Marginal Relevance Search
print
docs_with_mmr=vectordb.max_marginal_relevance_search(question, k=3, fetch_k=6)
print(len(docs_with_mmr))
print(docs_with_mmr[0].page_content)
print(docs_with_mmr[1].page_content)
print(docs_with_mmr[2].page_content)
print("MMR search completed.:question", question)



# # Without metadata information
# question = "what is the role of variance in pca?"
# docs = vectordb.similarity_search(question,k=5)
# for doc in docs:
#     print(doc.metadata) # metadata contains information about from which doc the answer has been fetched


#     # With metadata information
# question = "what is the role of variance in pca?"
# docs = vectordb.similarity_search(
#     question,
#     k=5,
#     #filter={"source":'/content/pca_d1.pdf'} # manually passing metadata, using metadata filter.
#     filter={"source":'/content/ens_d1.pdf'}
# )
# print("docs",len(docs))
# for doc in docs:
#     print(doc.metadata)




llm_name = "gpt-3.5-turbo"
print(llm_name)

#Augementation using RAG
from langchain_core.prompts import PromptTemplate                                    # To format prompts
from langchain_core.output_parsers import StrOutputParser                            # to transform the output of an LLM into a more usable format
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough          # Required by LCEL (LangChain Expression Language)



# Build prompt
template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""

QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)



retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 7, "fetch_k":15})
retriever


retrieval = RunnableParallel(
    {
        "context": RunnablePassthrough(context= lambda x: x["question"] | retriever),
        "question": RunnablePassthrough()
        }
    )


chat_llm = HuggingFaceEndpoint(
    #repo_id="mixedbread-ai/mxbai-3b-chat",  # Model card: https://huggingface.co/mixedbread-ai/mxbai-3b-chat
    repo_id="HuggingFaceH4/zephyr-7b-beta",  # Model card: https://huggingface.co/HuggingFaceH4/zephyr-7b-beta
    task="text-generation",
    max_new_tokens = 512,
    top_k = 30,
    temperature = 0.1,
    repetition_penalty = 1.03,
    huggingfacehub_api_token=hfapi_key,
)


# # RAG Chain

# rag_chain = (retrieval                     # Retrieval
#              | QA_PROMPT                   # Augmentation
#              | chat_llm                         # Generation
#              | StrOutputParser()
#              )

# response = rag_chain.invoke({"question": "What is PCA ?"})

# response

#from langchain_huggingface import ChatHuggingFace
chain_retriever = RunnablePassthrough() | retriever

result = chain_retriever.invoke("What is return policy?")

print("Result from retriever:", result)

#download the vector db
#vectordb.persist()
embedding =  HuggingFaceEmbeddings(
    model_name="mixedbread-ai/mxbai-embed-large-v1",                             # Provide the pre-trained model's path
    model_kwargs={'device': "cuda" if torch.cuda.is_available() else "cpu"},     # Pass the model configuration options
    encode_kwargs={'normalize_embeddings': False},                               # Pass the encoding options
)


vectordb = Chroma(persist_directory = '../rag/embeddings/chroma/',
                  embedding_function = embedding
                  )


llm = ChatHuggingFace(llm=chat_llm)

question = "What is return policy?"

qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectordb.as_retriever(), return_source_documents=True)

result = qa_chain.invoke({"query": question})

print("Result from QA chain:", result)
print("Answer:", result['result'])
print("Source documents:")