# Telecom Support Assistant

> A simple Streamlit-based assistant that answers telecom support questions using uploaded PDF guides and web search as a fallback.

## Summary

This project loads PDF manuals from the `data/` folder, builds an embeddings-based vector store, and uses Google Gemini (via `google.generativeai`) plus LangChain utilities to answer user questions in a chat-like Streamlit UI.

## Features

- Search and answer questions using uploaded PDF guides (vector search + LLM generation)
- Fallback web search using Tavily when answers are not found in the internal docs
- Simple, clean Streamlit UI with chat history

## Files

- [app.py](app.py) — main Streamlit app
- [requirements.txt](requirements.txt) — environment dependencies (may be incomplete; see below)
- [data/](data/) — put PDF manuals here (example files present: [data/Lanka_Telecom_Data_2025.pdf](data/Lanka_Telecom_Data_2025.pdf), [data/Tariff_2022_Dialog.pdf](data/Tariff_2022_Dialog.pdf))

## Requirements

- Python 3.8+ recommended
- See `requirements.txt` for base packages. The app additionally requires the following packages (inferred from imports):

```
streamlit
python-dotenv
google-generativeai
langchain_community
langchain_text_splitters
langchain_huggingface
faiss-cpu
huggingface-hub
```

Install dependencies (example):

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows use: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install streamlit python-dotenv google-generativeai langchain_community langchain_text_splitters langchain_huggingface faiss-cpu huggingface-hub
```

## Configuration

Create a `.env` file at the project root with the following keys:

```
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

The app will stop and show an error if the keys are missing.

## Usage

Start the Streamlit app locally:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

Place PDF files you want the assistant to use into the `data/` folder before starting the app. The app currently looks for `.pdf` files in that folder and will build a FAISS vectorstore from the documents.

## How it works (high level)

- `app.py` loads PDFs via `PyPDFLoader`, splits documents into chunks, creates embeddings with `HuggingFaceEmbeddings`, and builds a FAISS index.
- A Google Gemini model is used to generate answers from retrieved context chunks. If the model returns `NOT_FOUND`, a Tavily web search is attempted as a fallback.

## Troubleshooting

- If you see `Keys not found` make sure `.env` exists and the two API keys are set.
- If no PDFs are found, create a `data/` folder and add PDFs.
- FAISS and some embedding/model libraries may require platform-specific installs (e.g., `faiss-cpu` vs `faiss-gpu`).

## Next steps / Suggestions

- Add a `requirements-extras.txt` that pins all LLM and LangChain-related packages used by the app.
- Add a CI workflow to lint and run basic checks.
- Add CONTRIBUTING.md and LICENSE if this will be shared publicly.

---

If you want, I can: run the app locally, create a `.env.example`, or pin the exact dependencies into `requirements.txt`.
