import os
from langchain.document_loaders import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

DATA_DIR = "data"
VECTOR_STORE_DIR = "vector_store"

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        name = file.replace(".csv", "")
        print(f"Indexing {file}...")
        try:
            loader = CSVLoader(file_path=os.path.join(DATA_DIR, file), encoding="utf-8")
            docs = loader.load()
            db = FAISS.from_documents(docs, embedding)
            db.save_local(os.path.join(VECTOR_STORE_DIR, name))
            print(f"✅ Saved vector store: {name}")
        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")
