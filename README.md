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

