#!/usr/bin/env python3
"""
Content Generator for Learning Plans using Groq API

This script generates learning plan content for markdown files
using the Groq API with an interactive CLI interface.
"""

import os
import sys
import time
import json
import threading
from typing import Optional
from dotenv import load_dotenv

try:
    import questionary
    import requests
except ImportError:
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Domain definitions
DOMAINS = {
    "thinking": "Thinking & Problem-Solving",
    "mathematics": "Mathematics",
    "computer_science": "Computer Science (Theory + Systems)",
    "web_development": "Full-Stack Web Development",
    "ai_ml": "Artificial Intelligence (AI, ML, DL, NLP, Agents, RAG)",
    "system_design": "System Design & Architecture",
    "ui_ux": "UI/UX & Product Design",
    "media": "Media Creation (Video, Photo, Audio, Content)",
    "automation": "Automation & Productivity Systems",
    "business": "Business, Startups & Monetization"
}

# Difficulty levels
DIFFICULTY_LEVELS = ["Basic", "Intermediate", "Advanced", "All"]

# Categories
CATEGORIES = [
    "coding",
    "design",
    "product",
    "marketing",
    "soft_skills",
    "prompt_engineering"
]


def show_processing(stop_event: threading.Event) -> None:
    """Display a processing spinner animation."""
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r🔄 Generating content... {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()


def sanitize_filename(title: str) -> str:
    """Convert title to a safe filename."""
    return "".join(c if c.isalnum() else "_" for c in title).lower()


def get_inputs() -> dict:
    """Gather user inputs via interactive CLI."""
    print("\n📚 Learning Plan Content Generator")
    print("=" * 40)
    
    # Title input
    title = questionary.text(
        "📘 Enter content title:",
        validate=lambda x: len(x.strip()) > 0 or "Title is required"
    ).ask()
    
    if title is None:
        raise KeyboardInterrupt("User cancelled")
    
    # Domain selection
    domain_choices = list(DOMAINS.values())
    domain_display = questionary.select(
        "🎯 Select domain:",
        choices=domain_choices
    ).ask()
    
    if domain_display is None:
        raise KeyboardInterrupt("User cancelled")
    
    # Get domain key from display value
    domain = next(k for k, v in DOMAINS.items() if v == domain_display)
    
    # Difficulty level
    difficulty = questionary.select(
        "📊 Select difficulty level:",
        choices=DIFFICULTY_LEVELS
    ).ask()
    
    if difficulty is None:
        raise KeyboardInterrupt("User cancelled")
    
    # Category selection
    category = questionary.select(
        "📂 Select category:",
        choices=CATEGORIES + ["None"]
    ).ask()
    
    if category == "None" or category is None:
        category = ""
    
    # Content type
    content_type = questionary.select(
        "📝 Select content type:",
        choices=[
            "Topic Overview",
            "Learning Roadmap",
            "Tutorial Guide",
            "Concept Explanation",
            "Practice Exercises",
            "Project Ideas"
        ]
    ).ask()
    
    if content_type is None:
        raise KeyboardInterrupt("User cancelled")
    
    # Custom prompt (optional)
    custom_prompt = questionary.text(
        "✏️ Custom prompt (optional, press Enter to skip):",
        default=""
    ).ask()
    
    # Include code examples
    include_code = questionary.confirm(
        "💻 Include code examples?",
        default=True
    ).ask()
    
    return {
        "title": title.strip(),
        "domain": domain,
        "domain_display": domain_display,
        "difficulty": difficulty,
        "category": category,
        "content_type": content_type,
        "custom_prompt": custom_prompt.strip() if custom_prompt else "",
        "include_code": include_code
    }


def build_prompt(inputs: dict) -> str:
    """Build the prompt for the Groq API."""
    base_prompt = f"""You are an expert technical educator creating high-quality learning content.

Generate comprehensive {inputs['content_type'].lower()} content for the following:

**Title:** {inputs['title']}
**Domain:** {inputs['domain_display']}
**Difficulty Level:** {inputs['difficulty']}
**Category:** {inputs['category'] if inputs['category'] else 'General'}

Requirements:
1. Write in clear, educational markdown format
2. Include appropriate headings, lists, and formatting
3. Be thorough but concise
4. {"Include practical code examples where relevant" if inputs['include_code'] else "Focus on concepts without code examples"}
5. Use tables for structured information where appropriate
6. Include key takeaways or summary points
7. Add links to related topics where relevant (using relative markdown links)

Content Type Guidelines:
- Topic Overview: Explain the concept, its importance, and applications
- Learning Roadmap: Provide a step-by-step learning path with milestones
- Tutorial Guide: Create a hands-on tutorial with examples
- Concept Explanation: Deep dive into the theory and fundamentals
- Practice Exercises: Provide exercises with varying difficulty
- Project Ideas: Suggest practical projects to build skills

Format the output as a complete markdown document suitable for a learning plan."""

    if inputs['custom_prompt']:
        base_prompt += f"\n\nAdditional instructions: {inputs['custom_prompt']}"
    
    return base_prompt


def generate_content(inputs: dict) -> Optional[str]:
    """Generate content using Groq API."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in your .env file:\n"
            "GROQ_API_KEY=your_api_key_here"
        )
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = build_prompt(inputs)
    
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert technical educator specializing in creating comprehensive learning materials. You write in clear, well-structured markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    
    # Start spinner
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=show_processing, args=(stop_event,))
    spinner_thread.start()
    
    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        stop_event.set()
        spinner_thread.join()
        
        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", response.text)
            raise ValueError(f"API error ({response.status_code}): {error_msg}")
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content
        
    except requests.exceptions.Timeout:
        stop_event.set()
        spinner_thread.join()
        raise ValueError("Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        stop_event.set()
        spinner_thread.join()
        raise ValueError(f"Network error: {e}")


def save_content(content: str, inputs: dict) -> str:
    """Save generated content to a markdown file."""
    # Determine folder path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if inputs['difficulty'].lower() == "all":
        folder = os.path.join(base_dir, "plans", "general")
    else:
        folder = os.path.join(base_dir, "plans", inputs['difficulty'].lower())
    
    os.makedirs(folder, exist_ok=True)
    
    # Generate filename
    filename = f"{sanitize_filename(inputs['title'])}.md"
    filepath = os.path.join(folder, filename)
    
    # Add metadata header
    metadata = f"""---
title: "{inputs['title']}"
domain: "{inputs['domain_display']}"
difficulty: "{inputs['difficulty']}"
category: "{inputs['category'] if inputs['category'] else 'general'}"
content_type: "{inputs['content_type']}"
generated: true
---

"""
    
    # Write content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(metadata + content)
    
    return filepath


def main():
    """Main entry point."""
    try:
        # Check for API key early
        if not GROQ_API_KEY:
            print("\n❌ Error: GROQ_API_KEY not found in environment variables.")
            print("\nTo set up:")
            print("1. Create a .env file in the project root")
            print("2. Add: GROQ_API_KEY=your_api_key_here")
            print("3. Get your API key from: https://console.groq.com/keys")
            sys.exit(1)
        
        # Get user inputs
        inputs = get_inputs()
        
        print(f"\n📝 Generating {inputs['content_type']} for: {inputs['title']}")
        
        # Generate content
        content = generate_content(inputs)
        
        if content:
            # Save to file
            filepath = save_content(content, inputs)
            print(f"\n✅ Content saved to: {filepath}")
            
            # Ask if user wants to view
            view_content = questionary.confirm(
                "👀 Would you like to view the generated content?",
                default=False
            ).ask()
            
            if view_content:
                print("\n" + "=" * 60)
                print(content)
                print("=" * 60)
        else:
            print("\n❌ Failed to generate content.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user.")
        sys.exit(0)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
