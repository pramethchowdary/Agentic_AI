# 🛑 Social Media Credibility & Misinformation Analyzer 🧠

A Multi-Agent System for Automated Fact-Checking and Trust Scoring of Social Media Content.

| Metric | Status |
| :--- | :--- |
| **Current Stage** | Proof of Concept (Simple Pipeline) |
| **Tech Stack** | Python, Flask, Gemini API (Google), Grok API (OpenRouter) |
| **Agent Count** | 4 Specialist Agents + 1 Aggregator (Main Brain) |
| **Fact-Check Scope** | Text Claims, Source/Link Reputation, Account History |

---

## ✨ Project Summary: Agentic Fact-Checking Pipeline

This project demonstrates an **Agentic AI** approach to real-time social media content analysis. We have implemented a four-part collaborative pipeline to determine the overall trustworthiness of a tweet. This system moves beyond single-model analysis by utilizing specialized AI agents, each focusing on a distinct aspect of credibility, and then aggregating their findings for a final, well-reasoned verdict.

The initial implementation establishes a **simple, sequential workflow** (Text $\rightarrow$ Link $\rightarrow$ Account $\rightarrow$ Final Verdict), proving the concept of agent collaboration for automated fact-checking, credibility scoring, and misinformation detection.

> **Next Step:** We are preparing to transition this pipeline into a full **Agentic AI Template** with a more complex, dynamic workflow. This advanced system will feature iterative reasoning, self-correction, and dynamic tool use to handle more nuanced and complex misinformation patterns.

---

## ⚙️ Architecture and Agent Roles

The system is built on a modular architecture using the **Google Gemini API** and the **Grok-4-Fast model** via OpenRouter for specialized, state-of-the-art analysis.

### 1. Specialist Agents (`pipeline.py`)

| Agent Name | Model | Function | Output |
| :--- | :--- | :--- | :--- |
| **Text Claim Agent** | `Gemini-2.5-Flash` | Extracts factual claims from the text and assigns an initial credibility score (0-100). | JSON: Claims, Claim Score, Reasoning. |
| **Link & Source Agent** | `Gemini-2.5-Flash` | Analyzes external links/domains for reputation (e.g., mainstream vs. unreliable blog). **(Cannot crawl link content)** | JSON: Source list, Overall Source Score (0-100). |
| **X Account Analysis Agent** | `Grok-4-Fast` | Assesses the post author's history (transparency, non-partisanship, hate risk). **(Simulates external X/Web Tool use)** | Text: Credibility Score, Hate Risk, Factor Analysis Table. |

### 2. The Aggregator Agent (`pipeline.py`)

| Agent Name | Model | Function | Output |
| :--- | :--- | :--- | :--- |
| **Main Brain Aggregator** | `Gemini-2.5-Pro` | Synthesizes all three specialist reports using a structured framework (e.g., **"Conflict is a Red Flag"**). Determines the final, overall verdict. | JSON: Final Verdict (e.g., 'Misleading'), Overall Score, Justification. |

---

## 🚀 Getting Started

To run this project locally, you will need a working Python environment and API keys for both Google Gemini and OpenRouter (for Grok access).

### Prerequisites

1.  **Python 3.8+**
2.  **API Keys:**
    * `GOOGLE_API_KEY`
    * `OPENROUTER_API_KEY`
3.  **Dependencies:** `pip install flask google-genai openai python-dotenv`

### Setup and Execution

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_LINK]
    cd [YOUR_REPO_NAME]
    ```
2.  **Create a `.env` file** in the root directory and populate it with your API keys:
    ```ini
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
    ```
3.  **Run the Flask application:**
    ```bash
    python app.py
    ```
4.  **Access the application** in your browser at `http://127.0.0.1:5000`.

---

## 🌐 Deployment Status & Links

| Platform | Link Field 1 | Link Field 2 |
| :--- | :--- | :--- |
| **Live Demo Link** | **[PENDING: Insert Hosted Application Link Here]** | **[OPTIONAL: Insert Second Hosted Link or Demo Video Here]** |
| **Repository** | [YOUR_REPO_LINK] | |

---

## 🤝 Contributing

We welcome suggestions and contributions! Please open an issue or submit a pull request if you have ideas for enhancing the agent logic, expanding the framework, or improving the front-end interface.








# 🚀 Agentic AI — Multi-Agent Credibility & Fact-Checking System  

> 🧠 **Ongoing Project:** we have implemented ai-agents and check wether our system is performing well in a simple workflow,Next we will be implemented into the **Agentic AI Template**, showcasing how agentic reasoning and collaboration can perform automated fact-checking, credibility scoring, and misinformation detection with more complex workflow rather than  a simple pipeline.

---

## 🧩 Overview

**Agentic AI** is a modular **multi-agent framework** designed to assess the **credibility, reliability, and intent** behind social media content — particularly tweets (X posts).  
It orchestrates multiple AI agents (powered by **Gemini 2.5**, **Grok-4**, and **OpenAI**) to analyze:

1. The **factual integrity** of the text.  
2. The **trustworthiness of linked sources**.  
3. The **reputation and historical behavior** of the author.  
4. And finally — synthesize everything into a **single verdict** that classifies a tweet as *Verified True*, *Misleading*, *Likely False*, etc.

---

## 🧠 System Architecture

### 🕸️ Multi-Agent Pipeline
Each agent operates independently, then reports back to the **Main Brain Agent**, which fuses all insights into a final structured verdict.

| Agent | Function | Model |
|-------|-----------|-------|
| 🧩 **Agent 1 – Text Claim & Credibility** | Extracts factual claims and evaluates their credibility (0–100). | `gemini-2.5-flash` |
| 🔗 **Agent 2 – Link & Source Credibility** | Evaluates domains and sources mentioned in the tweet. | `gemini-2.5-flash` |
| 👤 **Agent 3 – X Account Analysis** | Analyzes the author’s profile for transparency, bias, and hate-speech risk. | `x-ai/grok-4-fast` |
| 🧠 **Agent 4 – Main Brain Aggregator** | Synthesizes all reports and produces a unified verdict. | `gemini-2.5-pro` |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Flask Templates (HTML/Jinja2) |
| **Backend** | Flask + Python |
| **AI APIs** | Google Generative AI (Gemini), OpenRouter (Grok-4), OpenAI SDK |
| **Environment** | `.env` for secure API key management |
| **Libraries** | `google-generativeai`, `openai`, `python-dotenv`, `flask`, `re`, `json`, `logging` |

---

## 🧪 Workflow

1. **User enters a tweet URL** on the web interface.  
2. The **Tweet Extractor** fetches text and author metadata.  
3. The **Pipeline (`pipeline.py`)** runs:
   - Text analysis  
   - Link credibility  
   - Account behavior scoring  
4. The **Main Brain Agent** fuses all findings into a **final structured JSON verdict**.
5. The **Results Page** displays:
   - Extracted tweet  
   - Individual agent outputs  
   - Final credibility verdict and reasoning

---

## 🖼️ UI Preview

| Landing Page | Results Page |
|---------------|--------------|
| ![Landing Page Screenshot](assets/ui_landing.png) | ![Results Screenshot](assets/ui_results.png) |

*(Add your actual screenshots in `assets/` and replace image paths accordingly.)*

---

## 🧰 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/agentic-ai.git
cd agentic-ai

