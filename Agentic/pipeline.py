import logging
import asyncio
import json
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END, START
from Agentic.agent import Agent, find_links, async_web_scrape # Import our tools

# --- 1. Define the State ---
class GraphState(TypedDict):
    # Inputs from the external tweet extractor
    tweet_text: str
    username: str
    
    # --- Parallel Branch 1 ---
    text_claim_result: Optional[Dict[str, Any]]
    
    # --- Parallel Branch 2 ---
    account_analysis_result: Optional[str]
    
    # --- Parallel Branch 3 (Web) ---
    scraped_content_list: Optional[List[Dict[str, str]]]
    summaries_list: Optional[List[Dict[str, str]]]
    
    # --- Joiner Nodes ---
    verifier_result: Optional[Dict[str, Any]]
    final_verdict: Optional[Dict[str, Any]]

# --- 2. Create Agent Instance ---
# All nodes will share this one instance of the agent class
agents = Agent()

# --- 3. Define Graph Nodes ---

async def text_claim_node(state: GraphState) -> Dict[str, Any]:
    """Branch 1: Analyzes the tweet text for claims."""
    logging.info("--- Running Node: text_claim ---")
    tweet_text = state["tweet_text"]
    result = await agents.extract_points_logic(tweet_text)
    return {"text_claim_result": result}

async def account_analysis_node(state: GraphState) -> Dict[str, Any]:
    """Branch 2: Analyzes the user's account."""
    logging.info("--- Running Node: account_analysis ---")
    username = state["username"]
    result = await agents.analyze_x_account_logic(username)
    return {"account_analysis_result": result}

async def web_scraping_node(state: GraphState) -> Dict[str, Any]:
    """Branch 3 (Step 1): Finds links and scrapes them in parallel."""
    logging.info("--- Running Node: web_scraping ---")
    tweet_text = state["tweet_text"]
    links = find_links(tweet_text)
    if not links:
        logging.info("No links found in tweet.")
        return {"scraped_content_list": []}

    # Run all scrapes in parallel
    tasks = [async_web_scrape(link) for link in links]
    results = await asyncio.gather(*tasks)
    
    scraped_data = [{"link": link, "content": content} for link, content in zip(links, results)]
    return {"scraped_content_list": scraped_data}

async def summarization_node(state: GraphState) -> Dict[str, Any]:
    """Branch 3 (Step 2): Summarizes scraped content in parallel."""
    logging.info("--- Running Node: summarization ---")
    scraped_content_list = state.get("scraped_content_list", [])
    if not scraped_content_list:
        return {"summaries_list": []}

    # Run all summaries in parallel
    tasks = [agents.summarize_text_logic(item["content"]) for item in scraped_content_list]
    results = await asyncio.gather(*tasks)
    
    summaries = [
        {"link": item["link"], "summary": summary.get("summary"), "error": summary.get("error")}
        for item, summary in zip(scraped_content_list, results)
    ]
    return {"summaries_list": summaries}

async def verifier_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Joiner Node 1: Waits for text_claim AND summarization.
    Verifies claims against the *first* link's summary.
    """
    logging.info("--- Running Node: verifier_agent ---")
    text_claim_result = state.get("text_claim_result")
    summaries_list = state.get("summaries_list", [])

    # Get the summary of the first link, if it exists
    summary_result = {}
    if summaries_list:
        first_summary = summaries_list[0]
        summary_result = {"summary": first_summary.get("summary"), "error": first_summary.get("error")}
    else:
        summary_result = {"summary": "", "error": "No links found or summarized."}

    result = await agents.verifier_agent_logic(text_claim_result, summary_result)
    return {"verifier_result": result}

async def aggregator_node(state: GraphState) -> Dict[str, Any]:
    """
    Joiner Node 2 (Final): Waits for text_claim, account_analysis, AND verifier_agent.
    """
    logging.info("--- Running Node: aggregator ---")
    text_result = state.get("text_claim_result")
    account_result = state.get("account_analysis_result")
    verifier_result = state.get("verifier_result") # This is the "link_result"

    result = await agents.main_brain_logic(text_result, verifier_result, account_result)
    return {"final_verdict": result}

# --- 4. Wire the Graph ---

workflow = StateGraph(GraphState)

# Add all nodes
workflow.add_node("text_claim", text_claim_node)
workflow.add_node("account_analysis", account_analysis_node)
workflow.add_node("web_scraping", web_scraping_node)
workflow.add_node("summarization", summarization_node)
workflow.add_node("verifier_agent", verifier_agent_node)
workflow.add_node("aggregator", aggregator_node)

# This is the parallel entry point.
# All 3 nodes will run simultaneously.
workflow.add_edge(START, "text_claim")
workflow.add_edge(START, "account_analysis")
workflow.add_edge(START, "web_scraping")

# Define the web scraping branch's dependency
workflow.add_edge("web_scraping", "summarization")

# --- Define the Joins (The important part) ---

# 1. 'verifier_agent' must wait for BOTH 'text_claim' AND 'summarization'
workflow.add_edge("text_claim", "verifier_agent")
workflow.add_edge("summarization", "verifier_agent")

# 2. 'aggregator' must wait for ALL THREE:
#    - 'text_claim' (from Branch 1)
#    - 'account_analysis' (from Branch 2)
#    - 'verifier_agent' (from Branch 3, after its own join)
workflow.add_edge("text_claim", "aggregator")
workflow.add_edge("account_analysis", "aggregator")
workflow.add_edge("verifier_agent", "aggregator")

# 3. Finally, end the graph
workflow.add_edge("aggregator", END)

# --- 5. Compile and Run ---
app = workflow.compile()

# This is the function you will import from other files
async def run_pipeline(tweet_text: str, username: str):
    """
    Runs the full parallel fact-checking pipeline
    and RETURNS the final state.
    """
    initial_state = {
        "tweet_text": tweet_text,
        "username": username
    }
    
    try:
        # Use ainvoke() to run the entire graph and get the
        # final state dictionary back.
        final_state = await app.ainvoke(initial_state)
        
        # Return only the final_verdict dictionary
        return final_state.get("final_verdict", {"error": "No final_verdict in state"})
                
    except Exception as e:
        logging.exception(f"🔥 Graph execution failed: {e}")
        # Return an error dictionary so the template can show it
        return {"error": f"Graph execution failed: {str(e)}"}

# This part runs when you execute `python pipeline.py`
if __name__ == "__main__":
    # This data comes from your external tweet_extractor
    TEST_TWEET_TEXT = "A new study from example.com shows that LangGraph is 10x faster than sequential execution. This is amazing!"
    TEST_USERNAME = "tech_bro_123"

    print(f"--- 🚀 Starting Parallel Graph for user: {TEST_USERNAME} ---")
    asyncio.run(run_pipeline(TEST_TWEET_TEXT, TEST_USERNAME))