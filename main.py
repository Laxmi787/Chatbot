import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# Direct key (or use os.getenv())
api_key = "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"

llm = ChatOpenAI(
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    model_name="mistralai/mistral-7b-instruct",
)

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_vector_store(dataset_name):
    path = f"vector_store/{dataset_name}"
    return FAISS.load_local(
        path,
        embeddings=embedding,
        allow_dangerous_deserialization=True  # Required for FAISS
    ).as_retriever()

def query_dataset(question, retriever):
    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return chain.run(question)
