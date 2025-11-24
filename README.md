# AI Doctor Companion

An agentic AI system for patient consultation and guidance.

## Tech Stack
- **Frontend**: Next.js, Tailwind CSS
- **Backend**: FastAPI, LangGraph, LangChain
- **AI**: Google Gemini 1.5 Flash

## Getting Started

See [walkthrough.md](walkthrough.md) for detailed instructions.

### Quick Start
1.  **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    # Set OPENAI_API_KEY in .env
    uvicorn app.main:app --reload
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
