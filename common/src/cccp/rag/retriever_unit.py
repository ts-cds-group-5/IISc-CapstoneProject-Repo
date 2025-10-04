import torch
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough


# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Embedding model (should match embeddings.py)
embedding = HuggingFaceEmbeddings(
    model_name="mixedbread-ai/mxbai-embed-large-v1",
    model_kwargs={'device': device},
    encode_kwargs={'normalize_embeddings': False}
)

# Load vector DB
vectordb = Chroma(persist_directory = './embeddings/chroma/', embedding_function = embedding)

#fetch all doccuments in the vectordb
# Set up retriever
retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10, "fetch_k": 15})


question = "what is the number of days allowed for return?"

# --- Similarity Search Example ---
#print("\n--- Similarity Search ---")
# Use MMR (Maximal Marginal Relevance) search for more relevant and diverse results
# docs = vectordb.similarity_search(question, k=3)
# #print(f"Found {len(docs)} similar documents:")
# for i, doc in enumerate(docs):
#     print(f"Doc {i+1}: {doc.page_content[:200]}...\n")

# # --- Max Marginal Relevance (MMR) Search Example ---
# ##print("\n--- Max Marginal Relevance (MMR) Search ---")
# messages = vectordb.max_marginal_relevance_search(question, k=4, fetch_k=4)
# #
# print(f"Found {len(messages)} MMR documents:")
# for i, doc in enumerate(messages):
#     print(f"Doc {i+1}: {doc.page_content[:200]}...\n")


# Prompt

# Advanced retrieval using RunnablePassthrough and RunnableParallel
# Build prompt
template = """Use the following pieces of context to answer the question at the end.\nIf you don't know the answer, just say that you don't know, don't try to make up an answer.\nAlways say \"thanks for asking!\" at the end of the answer.\n{context}\nQuestion: {question}\nHelpful Answer:"""
QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

#

# Runnable-based retrieval (fix: pass only the question string to retriever)
retrieval = RunnableParallel(
    {
        "context": (lambda x: x["question"]) | retriever,
        "question": RunnablePassthrough()
    }
)

#from langchain_huggingface import ChatHuggingFace
#chain_retriever = RunnablePassthrough() | retriever


# Example: get context chunks for a question

#retriever_result = retrieval.invoke({"question": question})
#print("Result from retriever:", retriever_result)
#print chain retriever result
# chain_retriever_result  = chain_retriever.invoke({"question": question})
# print("Chain Retriever returned {} context chunks.".format(len(chain_retriever_result)))
# for i, chunk in enumerate(chain_retriever_result):
#     print(f"Chunk {i+1}: {chunk.page_content[:200]}...\n")




# LLM setup (replace with your Hugging Face API key)
hfapi_key = "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"
chat_llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    max_new_tokens=512,
    top_k=30,
    temperature=0.1,
    repetition_penalty=1.03,
    huggingfacehub_api_token=hfapi_key,
)
llm = ChatHuggingFace(llm=chat_llm)



# QA Chain (standard)
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, return_source_documents=True)
qa_result = qa_chain.invoke({"query": question})
#format the qa_result to display in a list in a better way
#print("Answer:", qa_result['result'])

#print the qa_result dictornary object keys and values
print("QA Result Keys:", qa_result.keys())
print("Answer:", qa_result['result'])
print("Source Documents:")
for i, doc in enumerate(qa_result['source_documents']):
    print(f"Doc {i+1}: {doc.page_content[:200]}...\n")


exit()


#use the available llm to find the answer using the QA_PROMPT
final_result = llm.invoke(QA_PROMPT.format(context=qa_result, question=question))

print("Final Answer:")
#print final result in a formatted way
print(final_result)
print("Final result type:", type(final_result))



