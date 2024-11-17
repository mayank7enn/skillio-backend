# ./ai/translator.py
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from gtts import gTTS
import torch
import os
import json

def initialize_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "Qwen/Qwen2-1.5B-Instruct"
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # Explicitly set dtype
        device_map="auto",
        trust_remote_code=True  # Required for Qwen models
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True  # Required for Qwen models
    )
    
    # Set pad token to eos token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer, device

def process_input(input_text, action, model_data):
    if action == "Translate to English":
        prompt = f"Please translate the following text into English: {input_text}"
        lang = "en"
    elif action == "Translate to Chinese":
        prompt = f"Please translate the following text into Chinese: {input_text}"
        lang = "zh-cn"
    elif action == "Translate to Japanese":
        prompt = f"Please translate the following text into Japanese: {input_text}"
        lang = "ja"
    else:
        prompt = input_text
        lang = "en"

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}
    ]
    
    text = model_data['tokenizer'].apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Create input tensors with attention mask
    inputs = model_data['tokenizer'](
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    ).to(model_data['device'])
    
    # Generate response with attention mask
    generated_ids = model_data['model'].generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=512,
        pad_token_id=model_data['tokenizer'].pad_token_id,
        do_sample=True,
        temperature=0.7
    )
    
    generated_ids = [
        output_ids[len(input_ids):] 
        for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = model_data['tokenizer'].batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return output_text, lang

def text_to_speech(text, lang):
    # Get the absolute path to the public directory
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public'))
    audio_dir = os.path.join(public_dir, 'audio')
    
    # Create audio directory if it doesn't exist
    os.makedirs(audio_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f'output_audio_{hash(text)}.mp3'
    filepath = os.path.join(audio_dir, filename)
    
    # Generate audio file
    tts = gTTS(text=text, lang=lang)
    tts.save(filepath)
    
    # Return relative path for serving
    return f'/audio/{filename}'

def main():
    if len(sys.argv) != 3:
        print("Error: Incorrect number of arguments", file=sys.stderr)
        sys.exit(1)

    input_text = sys.argv[1]
    action = sys.argv[2]

    try:
        # Initialize model
        model, tokenizer, device = initialize_model()
        
        # Process input and generate output
        model_data = {'model': model, 'tokenizer': tokenizer, 'device': device}
        output_text, lang = process_input(input_text, action, model_data)
        
        # Generate audio and get relative path
        audio_path = text_to_speech(output_text, lang)
        
        # Return both output text and audio path as JSON
        result = {
            'outputText': output_text,
            'audioPath': audio_path
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()