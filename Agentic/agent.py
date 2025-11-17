import os
import re 
import dotenv
import json
import logging
import httpx  # Use httpx for async requests
import tweepy
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from openai import AsyncOpenAI # Use AsyncOpenAI
from datetime import datetime
import google.generativeai as genai

dotenv.load_dotenv()

class Agent:
    def __init__(self):
        # Configure Gemini models
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_flash = genai.GenerativeModel("models/gemini-1.5-flash")
            self.gemini_pro = genai.GenerativeModel("models/gemini-1.5-pro")
        except Exception as e:
            logging.error(f"Gemini initialization failed: {e}")
            raise

        # Configure OpenRouter client
        try:
            # Use AsyncOpenAI for await
            self.openrouter_client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        except Exception as e:
            logging.error(f"OpenRouter initialization failed: {e}")
            raise

    # -------------------------
    # Tweet Claim Extraction
    # -------------------------
    async def extract_points_logic(self, tweet_text: str) -> Dict[str, Any]:
        prompt = f"""
        You are a summarization expert. Extract all factual claims, opinions, and main points from the tweet.

        Tweet: "{tweet_text}"

        Respond ONLY with JSON:
        {{
          "points": ["claim 1", "claim 2", ...]
        }}
        """
        try:
            # Use async call
            response = await self.gemini_flash.generate_content_async(prompt)
            cleaned = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(cleaned)
        except Exception as e:
            logging.error(f"extract_points_logic error: {e}")
            return {"error": str(e)}

    # -------------------------
    # Article Summarization
    # -------------------------
    async def summarize_text_logic(self, article_text: str) -> Dict[str, Any]:
        prompt = f"""
        Summarize the article into one dense factual paragraph.
        Article:
        "{article_text}"

        Respond ONLY with JSON:
        {{
          "summary": "<your summary>"
        }}
        """
        try:
            # Use async call
            response = await self.gemini_flash.generate_content_async(prompt)
            cleaned = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(cleaned)
        except Exception as e:
            logging.error(f"summarize_text_logic error: {e}")
            return {"error": str(e)}

    # -------------------------
    # X Account Analysis (via OpenRouter)
    # -------------------------
    async def analyze_x_account_logic(self, username_or_id, num_posts="50", time_range="6 months"):
        prompt = f"""
        Analyze the X account @{username_or_id} for credibility, bias, and hate risk.
        Fetch up to {num_posts} posts from the last {time_range}.
        Output structured analysis and score.
        """
        try:
            # Use await on the async client
            completion = await self.openrouter_client.chat.completions.create(
                model="x-ai/grok-1",
                messages=[
                    {"role": "system", "content": "You are a fact-checking AI agent."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=1500,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logging.error(f"analyze_x_account_logic error: {e}")
            return f"Error: {e}"

    # -------------------------
    # Verifier Agent
    # -------------------------
    async def verifier_agent_logic(self, tweet_points_result, article_summary_result):
        claims = tweet_points_result.get("points", [])
        summary = article_summary_result.get("summary", "")

        prompt = f"""
        Compare tweet claims against article summary.

        Claims:
        {json.dumps(claims, indent=2)}

        Article Summary:
        "{summary}"

        Respond ONLY with JSON:
        {{
          "overall_verdict": "<Supported / Contradicted / No Overlap>",
          "results": [...]
        }}
        """
        try:
            # Use async call
            response = await self.gemini_flash.generate_content_async(prompt)
            cleaned = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(cleaned)
        except Exception as e:
            logging.error(f"verifier_agent_logic error: {e}")
            return {"error": str(e)}

    # -------------------------
    # Main Brain (Final Verdict)
    # -------------------------
    async def main_brain_logic(self, text_result, link_result, x_account_result):
        prompt = f"""
        Combine the three analyses and produce a final verdict.

        1. Tweet analysis: {json.dumps(text_result, indent=2)}
        2. Link analysis: {json.dumps(link_result, indent=2)}
        3. Account analysis: {x_account_result}

        Respond ONLY with JSON:
        {{
          "final_verdict": "<Verdict>",
          "overall_score": <0-100>,
          "reason": "<Summary>"
        }}
        """
        try:
            # Use async call
            response = await self.gemini_pro.generate_content_async(prompt)
            cleaned = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(cleaned)
        except Exception as e:
            logging.error(f"main_brain_logic error: {e}")
            return {"error": str(e)}


# -------------------------
# Helper Functions (not part of the class)
# -------------------------

def find_links(tweet_text: str) -> List[str]:
    """Extracts all URLs from a block of text."""
    return re.findall(r'(https?://\S+)', tweet_text)

async def async_web_scrape(url: str) -> str:
    """
    Asynchronously scrapes text from a URL.
    Uses httpx and pretends to be a browser.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10.0, headers=headers)
            html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=" ", strip=True)
        return text
    except Exception as e:
        logging.error(f"async_web_scrape error for {url}: {e}")
        return f"Error scraping {url}: {str(e)}"