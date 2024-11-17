import sys
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from transformers import BartTokenizer, BartForConditionalGeneration

# Ensure necessary nltk data is downloaded
nltk.download('punkt')

def get_video_id(video_url):
    """Extracts the video ID from the YouTube URL."""
    parsed_url = urlparse(video_url)
    if parsed_url.query:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v")
        if video_id:
            return video_id[0]
    if "youtu.be" in parsed_url.netloc and parsed_url.path:
        return parsed_url.path.split("/")[-1]
    return None

def fetch_transcript(video_id):
    """Fetches transcript from YouTube."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        subtitle = " ".join([entry['text'] for entry in transcript])
        return subtitle
    except Exception as e:
        return f"Error fetching transcript: {e}"

def summarize_text_tfidf(subtitle, num_sentences=3):
    """Generates a summary based on TF-IDF."""
    subtitle = subtitle.replace("\n", "")
    sentences = sent_tokenize(subtitle)
    organized_sent = {k: v for v, k in enumerate(sentences)}

    # TF-IDF vectorizer
    tf_idf = TfidfVectorizer(
        min_df=2,
        strip_accents='unicode',
        lowercase=True,
        token_pattern=r'\w{1,}',
        ngram_range=(1, 3),
        stop_words='english'
    )
    
    # Generate sentence vectors and scores
    sentence_vectors = tf_idf.fit_transform(sentences)
    sent_scores = np.array(sentence_vectors.sum(axis=1)).ravel()
    
    # Select top N sentences
    top_n_sentences = [sentences[index] for index in np.argsort(sent_scores, axis=0)[::-1][:num_sentences]]
    
    # Order sentences in original order
    mapped_sentences = [(sentence, organized_sent[sentence]) for sentence in top_n_sentences]
    ordered_sentences = sorted(mapped_sentences, key=lambda x: x[1])
    summary = " ".join([sentence for sentence, idx in ordered_sentences])
    
    # Create bullet points for key sentences
    bullet_points = "\n".join(f"• {sentence}" for sentence in top_n_sentences)
    return summary, bullet_points

def summarize_text_bart(subtitle):
    """Summarizes text using BART model."""
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
    
    # Tokenize input
    input_tensor = tokenizer.encode(subtitle, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate summary
    summary_ids = model.generate(input_tensor, max_length=160, min_length=120, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # Split BART summary into bullets for clarity
    bart_sentences = sent_tokenize(summary)
    bart_bullets = "\n".join(f"• {sentence}" for sentence in bart_sentences)
    return bart_bullets

def summarize_video(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"

    # Fetch subtitle transcript
    subtitle = fetch_transcript(video_id)
    if "Error" in subtitle:
        return subtitle  # Return error message if transcript fetch fails
    
    # Generate TF-IDF summary with bullet points
    tfidf_summary, bullet_points = summarize_text_tfidf(subtitle, num_sentences=3)
    
    # Generate BART summary
    bart_summary = summarize_text_bart(subtitle)
    
    # Combine BART and TF-IDF summaries into a detailed output
    return (
        f"Detailed Summary (TF-IDF):\n{bullet_points}\n\n"
        f"Detailed Summary (BART):\n{bart_summary}"
    )

if __name__ == "__main__":
    try:
        video_url = sys.argv[1]
        summary = summarize_video(video_url)
        print(summary)
    except Exception as e:
        print(f"Error: {e}")
