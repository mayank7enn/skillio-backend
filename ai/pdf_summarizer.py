#code for pdf_summarizer.py
import sys
import fitz  # PyMuPDF
from transformers import pipeline

def summarize_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    
    return summary[0]["summary_text"]

def answer_question(question, context):
    qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    result = qa_model(question=question, context=context)
    
    return result["answer"]

def handle_pdf(pdf_path, question=None, context=None):
    # Summarize the PDF content
    summary = summarize_pdf(pdf_path)
    
    # If there's a question, use the summary as context for answering
    if question and context:
        answer = answer_question(question, context)
        return summary, answer
    else:
        return summary, None

if __name__ == "__main__":
    action = sys.argv[1]
    
    if action == "summarize":
        pdf_path = sys.argv[2]
        summary = summarize_pdf(pdf_path)
        print(summary)
    elif action == "question":
        if len(sys.argv) < 4:
            print("Error: Missing arguments. Ensure you pass the question and context.")
            sys.exit(1)

        question = sys.argv[2]
        context = sys.argv[3]
        answer = answer_question(question, context)
        print(answer)
