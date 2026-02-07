# Learning Plan Content Generator

A Python script for generating learning plan content using the Groq API with an interactive CLI interface.

## Setup

1. **Install Python dependencies:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   # Get your API key from: https://console.groq.com/keys
   ```

3. **Run the generator:**
   ```bash
   python generate_content.py
   ```

## Features

- **Interactive CLI** - Easy-to-use command-line interface using questionary
- **Multiple domains** - Support for all learning domains (CS, AI, Web Dev, etc.)
- **Difficulty levels** - Generate content for Basic, Intermediate, or Advanced levels
- **Content types** - Create various content types:
  - Topic Overviews
  - Learning Roadmaps
  - Tutorial Guides
  - Concept Explanations
  - Practice Exercises
  - Project Ideas
- **Custom prompts** - Add custom instructions for specific content needs
- **Code examples** - Option to include/exclude code examples

## Generated Content

Generated content is saved as markdown files in the `plans/` directory:
- `plans/basic/` - Foundation level content
- `plans/intermediate/` - Intermediate level content  
- `plans/advanced/` - Advanced level content
- `plans/general/` - Content for "All" difficulty levels

## API Configuration

This script uses the Groq API with the `llama-3.1-70b-versatile` model. You'll need:

1. A Groq account (sign up at https://console.groq.com)
2. An API key from the Groq console
3. The API key set in your `.env` file

## Usage Example

```
$ python generate_content.py

📚 Learning Plan Content Generator
========================================
📘 Enter content title: Introduction to Neural Networks
🎯 Select domain: Artificial Intelligence (AI, ML, DL, NLP, Agents, RAG)
📊 Select difficulty level: Basic
📂 Select category: coding
📝 Select content type: Concept Explanation
✏️ Custom prompt (optional, press Enter to skip): 
💻 Include code examples? Yes

📝 Generating Concept Explanation for: Introduction to Neural Networks
🔄 Generating content... |

✅ Content saved to: /path/to/plans/basic/introduction_to_neural_networks.md
```
