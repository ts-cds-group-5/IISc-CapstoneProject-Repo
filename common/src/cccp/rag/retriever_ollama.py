from pyexpat.errors import messages
from urllib import request
import torch
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from cccp.agents.workflows.nodes.chat_agent import create_chat_agent
from cccp.core.config import get_settings


# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Embedding model (should match embeddings.py)
embedding = HuggingFaceEmbeddings(
    model_name="mixedbread-ai/mxbai-embed-large-v1",
    model_kwargs={'device': device},
    encode_kwargs={'normalize_embeddings': False}
)
settings = get_settings()
# Load vector DB
vectordb = Chroma(persist_directory = settings.embeddings_path, embedding_function = embedding)

# Set up retriever
retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 3})


# Prompt

# Advanced retrieval using RunnablePassthrough and RunnableParallel
# Build prompt
template = """Use the following pieces of context to answer the question at the end. Avoid generic answers unless it is important, use the context and answer in precise and minimal and also say yes or no, don't try to make up an answer.\nAlways say \"thanks for asking!\" at the end of the answer.\n{context}\nQuestion: {question}\nHelpful Answer:"""
QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

#

# Runnable-based retrieval (fix: pass only the question string to retriever)
retrieval = RunnableParallel(
    {
        "context": (lambda x: x["question"]) | retriever,
        "question": RunnablePassthrough()
    }
)


# Example: get context chunks for a question
question = "40 days return policy is allowed for my order in india?"
print("Question:", question)

retriever_result = retrieval.invoke({"question": question})

#print("Result from retriever:", retriever_result)
#format the retriever result to display in a list in a better way
# if isinstance(retriever_result, dict) and "context" in retriever_result:
#     context_list = retriever_result["context"]
#     print(f"Retriever returned {len(context_list)} context chunks.")
#     for i, chunk in enumerate(context_list):
#         print(f"Chunk {i+1}: {chunk.page_content[:200]}...\n")
# else:
#     print("Retriever result is not in the expected format.")


docs = vectordb.max_marginal_relevance_search(question, k=1, fetch_k=1)

# print(f"Found {len(docs)} MMR documents:")
# for i, doc in enumerate(docs):
#     print(f"Doc {i+1}: {doc.page_content[:200]}...\n")

# QA Chain (standard)
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, return_source_documents=True)
# qa_result = qa_chain.invoke({"query": question})
# #print("Answer:", qa_result['result'])


agent = create_chat_agent()

request.prompt = question
#request.message = retriever_result
#request.message =  docs
result = agent.invoke({
                "user_input": request.prompt,
                "messages": QA_PROMPT.format(context=retriever_result, question=request.prompt)
                #"messages": QA_PROMPT.format(context=docs, question=request.prompt)
            })

print("Agent Result:")
if isinstance(result, dict):
    for key, value in result.items():
        print(f"{key}: {value}\n")
else:
    print(result)
