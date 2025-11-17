import re
import google.generativeai as genai
from datetime import datetime
import os
from openai import OpenAI
import json
import logging
from dotenv import load_dotenv
load_dotenv()

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except TypeError:
    print("ERROR: GOOGLE_API_KEY not found. Please check your .env file.")
    exit()

# -------------------------------
# Agent 1: Text Claim & Credibility
# -------------------------------
def text_claim_agent(tweet_text):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = f"""
    You are an expert fact-checker specializing in social media content.
    Analyze the credibility of the following tweet.

    Tweet: "{tweet_text}"

    Follow these steps carefully:
    1.  **Extract Claims**: Identify and list the main factual claim(s). If the tweet is purely an opinion, satire, or a question, explicitly state that in the list.
    2.  **Assess Credibility**: Assign a credibility score to the **factual claims only**. The score should be an integer from 0 (verifiably false) to 100 (verifiably true). If the tweet contains no factual claim (e.g., it's just an opinion), the score must be `null`.
        - **0-20**: Disinformation / Verifiably False
        - **21-40**: Unlikely / Lacks Evidence
        - **41-60**: Needs Context / Unverifiable
        - **61-80**: Plausible / Likely True
        - **81-100**: Verified / True
    3.  **Explain Reasoning**: Provide a brief, neutral explanation for your score. Mention any logical fallacies, emotional language, or lack of sources.

    Respond ONLY with a valid JSON object following this structure:
    {{
      "claims": ["List of claims or a statement that it's an opinion."],
      "credibility_score": <integer or null>,
      "explanation": "Your concise reasoning here."
    }}
    """
    try:
        # Generate the content based on the detailed prompt
        response = model.generate_content(prompt)

        # Clean the model's output to ensure it's a parsable JSON string
        # by removing potential markdown formatting.
        cleaned_json_string = response.text.strip().lstrip("```json").rstrip("```")

        # Parse the cleaned string into a Python dictionary
        return json.loads(cleaned_json_string)

    except json.JSONDecodeError:
        logging.error(f"JSON Decode Error: Could not parse model response - {response.text}")
        return {"error": "Failed to parse the model's response as JSON."}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": f"An API or other unexpected error occurred: {str(e)}"}

# -------------------------------
# Agent 2: Link & Source Credibility
# -------------------------------
def link_agent(tweet_text):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    # Extract links from the tweet using regex
    links = re.findall(r'(https?://\S+)', tweet_text)
    if not links:
        return {
            "sources": [],
            "overall_score": 50, # Neutral score as no sources are provided
            "explanation": "No external links were found in the tweet."
        }
    
    prompt = f"""
    You are a digital source analyst. Analyze the credibility of the domains found in the following tweet.
    **You cannot access the content of these links directly.** Your analysis must be based on the general reputation of the source domains.

    Tweet Text: "{tweet_text}"
    Links Found: {links}

    Perform the following tasks:
    1.  **Analyze Individual Sources**: For each link, determine the reputation of its domain. Is it a mainstream news outlet, a scientific journal, a government site, a personal blog, a known source of misinformation, etc.?
    2.  **Assess Overall Credibility**: Based on the sources, provide an `overall_score` from 0 (sources are highly unreliable and likely weaken the claim) to 100 (sources are highly reputable and strongly support the claim).
    3.  **Explain Your Reasoning**: Briefly explain your overall score.

    Respond ONLY with a valid JSON object with the following structure:
    {{
      "sources": [
        {{
          "link": "The full URL",
          "domain_reputation": "A brief description of the source's reputation (e.g., 'Reputable international news agency')."
        }}
      ],
      "overall_score": <integer>,
      "explanation": "Your concise explanation for the overall score."
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_json_string)

    except json.JSONDecodeError:
        logging.error(f"JSON Decode Error from link agent: {response.text}")
        return {"error": "Failed to parse the model's response as JSON."}
    except Exception as e:
        logging.error(f"An unexpected error occurred in link agent: {e}")
        return {"error": f"An API or other unexpected error occurred: {str(e)}"}

# -------------------------------
# Agent 3: x_Account Analysis Agent
# -------------------------------

def analyze_x_account(username_or_id, num_posts="50", time_range="6 months"):
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Format the prompt with inputs
    prompt = f"""
    Analyze the X account [@username or user_id: {username_or_id}] for credibility and hate speech risk as a fact-checking agent. Fetch up to [NUM_POSTS: {num_posts}] recent posts from the last [TIME_RANGE: {time_range}] using X tools. Use these factors, weighted equally unless specified:

    1. Transparency: % posts with evidence (links OR references to sources); check bio for methodology.
    2. Non-Partisanship: Topic diversity (e.g., balanced politics?); retweet balance from diverse accounts.
    3. Methodology: Verify 3-5 sample claims via web search (e.g., match to PolitiFact/Snopes).
    4. Account History: Patterns of consistency (no flip-flops); flag repeats of debunked topics.
    5. Engagement: Avg likes/replies; % toxic replies (semantic search for "fake" or "hate").
    6. Hate Risk: Scan for slurs, threats, bias (e.g., against groups); % flagged posts.

    Output:
    - Overall Credibility Score: [0-100], with Low/Med/High label.
    - Hate Risk: Low/Med/High, with % flagged.
    - Table: Factor | Score (0-10) | Evidence (2-3 examples).
    - Recommendations: e.g., "Trust for neutral topics; flag political claims."

    Handle media accounts leniently if verified/high-followers but low links—focus on history. Current date: [{today}].
    """


    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    completion = client.chat.completions.create(
    extra_body={},
    model="x-ai/grok-4-fast",
    messages=[
        {
        "role": "system",
        "content": "You are a fact-checking agent with access to X tools, web search, and semantic analysis capabilities. Respond in the specified output format."
        },
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=0.5,  # Lower for more structured output
    max_tokens=1500  # Increase for detailed responses with table
    )
    
    return completion.choices[0].message.content


# -------------------------------
# Agent 4: Main Brain Aggregator
# -------------------------------
def run_pipeline(tweet_text, username):
    # Run agents
    text_result = text_claim_agent(tweet_text)
    link_result = link_agent(tweet_text)
    x_account_result = analyze_x_account(username)  # Use the provided username

    # Combine via Gemini
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    prompt = f"""
    You are a master intelligence analyst. Your mission is to synthesize reports from three specialist agents to determine the overall credibility of a tweet.

    **Agent Reports:**

    1.  **Text & Claim Analysis**:
        ```json
        {json.dumps(text_result, indent=2)}
        ```

    2.  **Link & Source Analysis**:
        ```json
        {json.dumps(link_result, indent=2)}
        ```

      3.  **X Account Analysis (Raw Text from Grok)**:
        ```text
        {x_account_result}
        ```

    **Reasoning Framework:**
    Use the following guidelines to weigh the evidence:
    -   **Conflict is a Red Flag**: If the claim's score is high but the source and/or account scores are low, the verdict should be **"Misleading"**. A strong claim requires strong backing.
    -   **No Sources**: If no links were provided (neutral source score of ~50), your verdict must rely more heavily on the text claim's plausibility and the account's reputation.
    -   **Opinions**: If the text is identified as an opinion, the verdict must be **"Opinion/Unverifiable"** unless it uses deceptive language to appear as fact.
    -   **Errors**: If any agent report contains an "error" field, acknowledge that data is missing and lower your confidence in the final verdict accordingly.

    **Final Task:**
    Based on all available data, provide a final verdict. Respond ONLY with a valid JSON object.

    {{
      "final_verdict": "One of ['Verified True', 'Likely True', 'Misleading', 'Likely False', 'Verified False', 'Opinion/Unverifiable']",
      "overall_score": <integer from 0 to 100>,
      "reason": "A concise explanation justifying your verdict by referencing the key findings from the three agent reports."
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_json_string)

    except json.JSONDecodeError:
        logging.error(f"JSON Decode Error in main brain agent: {response.text}")
        return {"error": "Failed to parse the final verdict from the model."}
    except Exception as e:
        logging.error(f"An unexpected error occurred in main brain agent: {e}")
        return {"error": f"An API or other unexpected error occurred: {str(e)}"}


# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    tweet = """I was laughing out listening to this nonsense, imagine the plight of the audience. He is an embarrassment. He should stick to India bashing and Modi bashing in his foreign trips than attempting to portray as an intellectual. 

@INCIndia
 think about it."""
    
    name = "Isriramseshadri"

    verdict = run_pipeline(tweet, username=name)
    print("\nFinal Verdict:\n", verdict)