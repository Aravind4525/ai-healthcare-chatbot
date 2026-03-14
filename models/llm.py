from langchain_groq import ChatGroq
from config.config import GROQ_API_KEY, MODEL_NAME

def get_chatgroq_model():
    try:
        model = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME)
        return model

    except Exception as e:
        print("Error initializing model", e)