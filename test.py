import os
import dotenv
import google.generativeai as genai

# Load environment variables from .env file
dotenv.load_dotenv()

# Load API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your environment.")

# Configure client
genai.configure(api_key=api_key)

# List available models
print("✅ Available Gemini Models for your API Key:")
for model in genai.list_models():
    # Only show models that support generate_content
    if "generateContent" in model.supported_generation_methods:
        print(f"- {model.name}")
