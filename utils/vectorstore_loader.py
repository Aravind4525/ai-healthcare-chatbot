from utils.rag_utils import load_medical_docs
from langchain_community.vectorstores import FAISS
from models.embeddings import get_embeddings
import os

_vectorstore = None


def get_vectorstore():
    """
    Load vectorstore only once and reuse it.
    """
    global _vectorstore

    if _vectorstore is None:

        embeddings = get_embeddings()

        if os.path.exists("health_store_knowledge_base"):
            # Load existing FAISS index
            _vectorstore = FAISS.load_local("health_store_knowledge_base", embeddings, allow_dangerous_deserialization=True)
        else:
            # Create new FAISS index
            _vectorstore = load_medical_docs()

    return _vectorstore

# if __name__ == "__main__":
#     load_medical_docs()