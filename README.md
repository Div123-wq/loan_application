# LoanLens AI 🔍 — AI Financial Intelligence Assistant

**LoanLens AI** transforms standard, dry, legalistic loan documents into an interactive "AI Financial Intelligence Companion." It highlights hidden fees, detects traps, simulates "what-if" scenarios, translates to regional languages, and prepares personalized negotiation scripts.

No more "Upload PDF → Get Summary." This is a premium financial advisor designed to protect the borrower.

---

## 🚀 Key Features Demonstrated

1. **Hidden Trap Detector (⭐ Most Crucial)**: Automatically extracts variable interest terms, exit prepayment penalties, and compounded delayed rates, complete with simulated absolute financial losses.
2. **Explain Like a Friend Mode (⭐)**: Translates legalese into friendly side-by-side conversational English.
3. **Scary Meter / Risk Score Gauge (⭐)**: Renders beautiful SVG circular danger score levels (Low, Medium, High, Critical) with sub-scores.
4. **Reality Cost Calculator (⭐)**: Breaks down EMIs versus absolute interest paid, displaying detailed year-by-year amortization forecasts.
5. **What-If Scenario Simulator (⭐)**: Type or select templates (e.g. "What if I miss 2 EMIs?") and watch simulated event ladders, credit score drops, and recovery times populate.
6. **Loan Comparison Battle (⭐)**: Upload 2 or 3 agreements side-by-side to discover the cheapest, safest, and overall recommended contract with Radar parameter matches.
7. **Fraud & Suspicious Fee Flags (⭐)**: Benchmarks administrative fees or unilateral contracts against standard tier-1 lending codes.
8. **Emotional Financial Pressure Detector (⭐)**: Inputs your household salary, expenses, and dependents to calculate safety scores and seasonal calendars.
9. **Voice Conversation AI (⭐)**: Fully voice-enabled text-to-speech chat pane integrated directly inside your browser.
10. **Regional Language Simplifier (⭐)**: Translates explanations into Hindi, Kannada, Tamil, Telugu, Malayalam, or Marathi instantly.
11. **Deadline Panic Predictor (⭐)**: Correlates household fee cycles with loan rate revisions.
12. **Negotiation Script Generator (👑 Futuristic)**: Drafts contextual opening scripts and list exact questions to ask bank managers to remove fees.

---

## 🛠️ Technology Stack & Core System Architecture

### Frontend (Desktop & Mobile)
- **HTML5 & Semantic Markup**: Built using unique IDs and clean, semantic tags.
- **Vanilla CSS (Design System)**: Harmonious HSL color tokens, dark mode gradients, glassmorphism containers, skeletons, shimmers, and float micro-animations.
- **Web Speech API**: In-browser speech-to-text integration.

### Backend (REST API Gateway)
- **Python / Flask**: Multi-route REST API, thread-safe session controls, in-memory document parsing cache.
- **PyMuPDF (`fitz`)**: Fast PDF document text extractors.
- **GitHub Models (OpenAI SDK Integration)**: Direct connections to GitHub's Azure AI Inference endpoints utilizing `gpt-4o` for deep structural understanding.

---

## 📦 Local Quickstart Instructions

### 1. Prerequisites
- **Python 3.8+** installed.
- A **GitHub Personal Access Token (PAT)**. You can generate one easily from [GitHub Settings → Developer Settings → Personal Access Tokens (classic)](https://github.com/settings/tokens) (No special permissions/scopes are required!).

### 2. Backend Setup
1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create your environment variables file:
   ```bash
   copy .env.example .env
   ```
3. Open the `.env` file and insert your GitHub Personal Access Token:
   ```env
   GITHUB_TOKEN=ghp_YourGitHubTokenHere
   GITHUB_MODEL=gpt-4o
   ```
4. Install all Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Launch the Flask backend server:
   ```bash
   python app.py
   ```
   The API will listen at `http://localhost:5000`.

### 3. Frontend Setup
1. Launch any local development server (or simply double-click and open `frontend/index.html` directly in your browser).
2. Enjoy the experience!

> **Note**: LoanLens AI features built-in fallback mockups. If you have not uploaded a document yet, or do not have a token ready, clicking **View Demo** or navigating the tabs will pre-load standard Home Loan agreement intelligence data so you can preview the entire application workflow instantly!