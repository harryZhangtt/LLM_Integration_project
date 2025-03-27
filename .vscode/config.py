import os

# ChatGPT API Key
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")  # Ensure this is set in your environment

# Claude API Key
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")  # Ensure this is set in your environment

# Correct ChatGPT API Endpoint
CHATGPT_API_URL = os.getenv("CHATGPT_API_URL", "https://api.openai.com/v1/chat/completions")  # Default value provided
