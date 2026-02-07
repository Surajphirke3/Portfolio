#!/usr/bin/env python3
"""
Simplified Content Generator for Learning Plans using Groq API

A streamlined version for quick content generation.
"""

import os
import sys
import time
import threading
from dotenv import load_dotenv

try:
    import questionary
    import requests
except ImportError:
    print("Please install dependencies: pip install questionary requests python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Size to complexity mapping (similar to module_numbers in roadmap generator)
size_to_complexity = {
    "Bite-Size": {"depth": "brief", "tokens": 1024},
    "Standard": {"depth": "moderate", "tokens": 2048},
    "Comprehensive": {"depth": "detailed", "tokens": 4096},
    "In-Depth": {"depth": "extensive", "tokens": 6000}
}

# Domains
domains = [
    "Thinking & Problem-Solving",
    "Mathematics",
    "Computer Science",
    "Web Development",
    "Artificial Intelligence",
    "System Design",
    "UI/UX Design",
    "Media Creation",
    "Automation",
    "Business & Startups"
]


def sanitize_filename(title):
    return "".join(c if c.isalnum() else "_" for c in title).lower()


def show_processing(stop_event):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\rProcessing... {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 30 + "\r")


def get_inputs():
    title = questionary.text("📘 Enter Content Title:").ask()
    if not title or not title.strip():
        raise ValueError("Title is required")
    
    domain = questionary.select("📂 Select Domain:", choices=domains).ask()
    size = questionary.select("📏 Select Content Size:", choices=list(size_to_complexity.keys())).ask()
    difficulty = questionary.select("🎯 Select Difficulty Level:", choices=["All", "Basic", "Intermediate", "Advanced"]).ask()

    return {
        "title": title.strip(),
        "domain": domain,
        "size": size,
        "difficulty": difficulty,
        "depth": size_to_complexity[size]["depth"],
        "max_tokens": size_to_complexity[size]["tokens"]
    }


def generate_content(inputs):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Set it in .env file.")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Create a {inputs['depth']} learning guide for:

Title: {inputs['title']}
Domain: {inputs['domain']}
Difficulty: {inputs['difficulty']}

Format as a well-structured markdown document with:
- Clear headings and sections
- Key concepts explained
- Practical examples where relevant
- Learning objectives
- Related topics to explore"""

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert educator creating learning content."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": inputs["max_tokens"]
    }
    
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=show_processing, args=(stop_event,))
    spinner_thread.start()
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
        stop_event.set()
        spinner_thread.join()
        
        if response.status_code != 200:
            raise ValueError(f"API error {response.status_code}: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]
    finally:
        if not stop_event.is_set():
            stop_event.set()
            spinner_thread.join()


def save_content(content, title, difficulty):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(base_dir, "plans", sanitize_filename(difficulty) if difficulty != "All" else "general")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{sanitize_filename(title)}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Content saved to {filename}")


def main():
    try:
        if not GROQ_API_KEY:
            print("❌ Error: GROQ_API_KEY not set in environment.")
            print("   Add GROQ_API_KEY=your_key to .env file")
            sys.exit(1)
        
        payload = get_inputs()
        content = generate_content(payload)
        save_content(content, payload["title"], payload["difficulty"])
        
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
