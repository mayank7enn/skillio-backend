import sys
from transformers import pipeline
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def answer_query(query):
    # Direct response for specific questions
    if "creators" in query.lower() and "app" in query.lower():
        return "The creators of this app are Gaurav Bisht, Mayank Sharma, and Sanyam Parashar."
    
    # Default model-based response
    qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    
    # This is a simplified example. In a real-world scenario, you'd have a knowledge base to query from.
    context = "Skillio is an AI-powered learning assistant that helps students summarize videos, answer questions, and summarize PDFs."
    
    result = qa_model(question=query, context=context)
    return result["answer"]

if __name__ == "__main__":
    query = sys.argv[1]
    answer = answer_query(query)
    print(answer)
