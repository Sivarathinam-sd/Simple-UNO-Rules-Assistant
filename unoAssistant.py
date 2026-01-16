from groq import Groq
import os
from dotenv import load_dotenv
import gradio as gr
from bs4 import BeautifulSoup
import requests

load_dotenv(override=True)
api_key = os.getenv('GROQ_API_KEY')

client = Groq(api_key=api_key)

def webContentScraper(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find_all('p')
    text = []
    for i in content:
        for a in i.find_all('a'):
            a.unwrap()
        for img in i.find_all('img'):
            img.decompose()
        for tag in i.find_all('strong', 'span'):
            tag.unwrap()
        
        cleaned_text = i.get_text()
        if cleaned_text:
            text.append(cleaned_text)

    return "\n\n".join(text)
    
    
rules = webContentScraper("https://www.unorules.com")

systemPromt = f"""You are a UNO Expert given the details of a Revised & Polished UNO Assistant Prompt {rules}.
Use only the information provided in the context to respond.
Do not assume, infer, or invent any rules, strategies, or information that are not explicitly stated.
If something is not mentioned in the context, acknowledge that it is not specified rather than guessing.
Keep responses concise, neutral, and faithful to the given rules.
Do not overthink or expand beyond the provided details.
"""

def chat(message, history):
    history = [{'role': h['role'], 'content' : h['content']} for h in history]
    messages = [{'role': 'system', 'content': systemPromt}] + history + [{'role': 'user', 'content': message}]
    stream = client.chat.completions.create(model='llama-3.3-70b-versatile', messages=messages, stream=True)
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response

gr.ChatInterface(fn=chat).launch()