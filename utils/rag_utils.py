from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from models.embeddings import get_embeddings
import json
import os


def load_medical_docs():

    # Load JSON data
    with open("data/medical_data.json", "r") as f:
        medical_data = json.load(f)

    documents = []

    for disease in medical_data:

        disease_name = disease.get("disease", "Unknown")

        text_chunks = []

        # Common symptoms
        if "common_symptoms" in disease:
            text_chunks.append(
                f"{disease_name} symptoms: " + ", ".join(disease["common_symptoms"])
            )

        # Overview
        if "overview" in disease:
            text_chunks.append(
                f"{disease_name} overview: {disease['overview'].get('description','')}"
            )

        # Transmission
        if "transmission" in disease:
            for key, values in disease["transmission"].items():
                if isinstance(values, list):
                    text_chunks.append(
                        f"{disease_name} transmission via {key}: " + ", ".join(values)
                    )

        # Treatment
        if "treatment" in disease:
            if isinstance(disease["treatment"], dict):
                management = disease["treatment"].get("management", [])
                if management:
                    text_chunks.append(
                        f"{disease_name} treatment: " + ", ".join(management)
                    )

        # Prevention
        if "prevention" in disease:
            if isinstance(disease["prevention"], dict):
                measures = disease["prevention"].get("measures", [])
                if measures:
                    text_chunks.append(
                        f"{disease_name} prevention: " + ", ".join(measures)
                    )

        for chunk in text_chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"disease": disease_name}
                )
            )

    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save FAISS locally
    vectorstore.save_local("health_store_knowledge_base")

    return vectorstore

def retrieve_docs(query, vectorstore):

    docs = vectorstore.similarity_search(query, k=3)

    context = "\n".join([doc.page_content for doc in docs])

    return context