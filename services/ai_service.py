import os
import re
from dotenv import load_dotenv
from textblob import TextBlob
from services.utils import get_upload_path

# Load environment variables
load_dotenv()

# ---------------------------------------------
# Import AI + NLP libraries
# ---------------------------------------------
try:
    import torch
    from llama_index.core import VectorStoreIndex, download_loader, Settings
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain_google_genai import ChatGoogleGenerativeAI
    import google.generativeai as genai
except Exception as e:
    # If packages not installed, fail gracefully and guide the user
    print("⚠️ Some AI libraries are missing. Install all dependencies from requirements.txt")
    print("Error details:", str(e))
    VectorStoreIndex = None
    download_loader = None
    Settings = None
    HuggingFaceEmbeddings = None
    ChatGoogleGenerativeAI = None
    genai = None
    torch = None


# ---------------------------------------------
# Configure Gemini API
# ---------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if genai and GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ---------------------------------------------
# Choose device for embeddings
# ---------------------------------------------
device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"

# Cache to avoid reloading models or indexes unnecessarily
index_cache = {}


# ---------------------------------------------
# System prompt (same as original Streamlit logic)
# ---------------------------------------------
SYSTEM_PROMPT = """
[INST]
<>
    You are a professional financial analyst assistant.
    Analyze financial documents carefully and provide **clear, structured, data-backed insights**.

    - Summarize the document with sections: Revenue, Expenses, Profitability, Cash Flow, Assets & Liabilities, Growth Drivers, Risks, Market Outlook.
    - Highlight **positive signals** and **red flags**.
    - Use bullet points or subheadings for clarity.
    - Ground answers in the document; if info is missing, explicitly state it.
    - Keep tone professional and concise.
<>
[/INST]
"""


# ---------------------------------------------
# Initialize LLM + embeddings
# ---------------------------------------------
def _ensure_models():
    """Initializes and configures the embeddings + LLM models once."""
    global embeddings, llm

    if "embeddings" in globals() and globals().get("embeddings") is not None:
        return  # already loaded

    if not HuggingFaceEmbeddings or not ChatGoogleGenerativeAI:
        raise RuntimeError("AI packages not installed. Please install dependencies from requirements.txt")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": device},
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        system_instruction=SYSTEM_PROMPT,
    )

    Settings.llm = llm
    Settings.embed_model = embeddings


# ---------------------------------------------
# Load and cache PDF Index
# ---------------------------------------------
def _load_or_create_index(filepath: str):
    """Loads or builds a LlamaIndex for a given PDF file."""
    if VectorStoreIndex is None:
        raise RuntimeError("llama_index not installed. Please install dependencies.")

    filename = os.path.basename(filepath)
    if filename in index_cache:
        return index_cache[filename]

    PyMuPDFReader = download_loader("PyMuPDFReader")
    loader = PyMuPDFReader()
    documents = loader.load(file_path=filepath, metadata=True)
    index = VectorStoreIndex.from_documents(documents)
    index_cache[filename] = index
    return index


# ---------------------------------------------
# Analyze PDFs
# ---------------------------------------------
def analyze_pdfs(filenames: list):
    """
    Analyze one or more uploaded PDF financial documents.
    Returns a dictionary mapping filename → summarized insights.
    """
    _ensure_models()
    base_dir = get_upload_path()
    individual_results = {}
    combined_texts = []
    sentiment_results = {}

    analysis_prompt = """
    Provide a comprehensive and structured overview of this financial document.
    Include: Executive Summary, Revenue & Sales, Profitability, Expenses, Balance Sheet Highlights, Cash Flow, Growth Drivers, Risks, and Future Outlook.
    Use bullet points and sections. Mention missing info explicitly.
    """

    for fname in filenames:
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            individual_results[fname] = "❌ File not found"
            sentiment_results[fname] = {"error": "File not found"}
            continue

        index = _load_or_create_index(path)
        response = index.as_query_engine().query(analysis_prompt)
        text = response.response if hasattr(response, "response") else str(response)
        text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

        individual_results[fname] = text.strip()
        combined_texts.append({
            "filename": fname,
            "text": text,
            "index": index
        })
        sentiment_results[fname] = _analyze_sentiment(text)

    # Combined analysis (if multiple files)
    combined_analysis = None
    if len(combined_texts) > 1:
        combined_analysis = _perform_combined_analysis(combined_texts)

    # Overall sentiment (if multiple files)
    overall_sentiment = None
    if len(sentiment_results) > 1:
        overall_sentiment = _calculate_overall_sentiment(sentiment_results)

    return {
        "individual_analysis": individual_results,
        "combined_analysis": combined_analysis,
        "sentiment_analysis": sentiment_results,
        "overall_sentiment": overall_sentiment
    }

def _perform_combined_analysis(docs: list) -> dict:
    prompt = f"""
    You are a financial analyst. Analyze these {len(docs)} reports collectively:
    1️⃣ Comparative overview (revenue, expenses, margins)
    2️⃣ Trend analysis across documents
    3️⃣ Key differences and similarities
    4️⃣ Consolidated insights
    5️⃣ Investment and risk perspective
    Be detailed and use financial reasoning.
    """

    index = docs[0]["index"]
    doc_list = "\n".join([f"- {d['filename']}" for d in docs])
    full_prompt = f"Documents analyzed:\n{doc_list}\n\n{prompt}"

    response = index.as_query_engine().query(full_prompt)
    text = response.response if hasattr(response, "response") else str(response)
    text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

    return {
        "analysis": text.strip(),
        "documents_analyzed": [d["filename"] for d in docs],
        "document_count": len(docs)
    }

def _analyze_sentiment(text: str) -> dict:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.3:
        label = "Positive 📈"
    elif polarity < -0.3:
        label = "Negative 📉"
    else:
        label = "Neutral ➡️"

    positive_words = ["growth", "profit", "increase", "strong", "improvement", "success"]
    negative_words = ["loss", "decline", "decrease", "weak", "risk", "concern"]

    t = text.lower()
    pos_count = sum(1 for w in positive_words if w in t)
    neg_count = sum(1 for w in negative_words if w in t)

    return {
        "polarity": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
        "sentiment": label,
        "positive_signals": pos_count,
        "negative_signals": neg_count,
        "interpretation": _interpret_sentiment(polarity, subjectivity, pos_count, neg_count)
    }


def _interpret_sentiment(polarity, subjectivity, pos, neg):
    desc = []
    if polarity > 0.5:
        desc.append("Strongly positive outlook")
    elif polarity > 0.3:
        desc.append("Moderately positive outlook")
    elif polarity < -0.3:
        desc.append("Concerning indicators present")
    else:
        desc.append("Balanced or neutral tone")

    desc.append("subjective" if subjectivity > 0.6 else "objective")

    if pos > neg:
        desc.append(f"focus on growth ({pos} positive cues)")
    elif neg > pos:
        desc.append(f"mentions challenges ({neg} negative cues)")

    return " - ".join(desc)


def _calculate_overall_sentiment(sentiments: dict) -> dict:
    valid = [s for s in sentiments.values() if "error" not in s]
    if not valid:
        return {"error": "No valid sentiment data"}

    avg_p = sum(s["polarity"] for s in valid) / len(valid)
    avg_s = sum(s["subjectivity"] for s in valid) / len(valid)
    total_pos = sum(s["positive_signals"] for s in valid)
    total_neg = sum(s["negative_signals"] for s in valid)

    if avg_p > 0.3:
        label = "Positive 📈"
    elif avg_p < -0.3:
        label = "Negative 📉"
    else:
        label = "Neutral ➡️"

    return {
        "average_polarity": round(avg_p, 3),
        "average_subjectivity": round(avg_s, 3),
        "overall_sentiment": label,
        "total_positive_signals": total_pos,
        "total_negative_signals": total_neg,
        "documents_analyzed": len(valid),
        "summary": f"Overall sentiment is {label} across {len(valid)} reports."
    }


# ---------------------------------------------
# Ask questions about PDFs
# ---------------------------------------------
def ask_question(question: str, filenames: list = None):
    """
    Ask a follow-up question across uploaded PDFs.
    Returns combined structured answer.
    """
    _ensure_models()
    base_dir = get_upload_path()
    if not filenames:
        filenames = list(index_cache.keys())

    if not filenames:
        return "⚠️ No PDFs available for analysis."

    followup_prompt_template = f"""
    The user asked: "{question}"

    You are a professional financial analyst assistant. Using the uploaded financial documents, provide a **comprehensive, structured, and insightful response**. Follow these instructions:

    1. Reference each PDF separately. Start each section with the filename.
    2. Provide an Executive Summary: key takeaways and overall financial health.
    3. Revenue Analysis: comment on trends, growth/decline, costs, and margins.
    4. Balance Sheet Highlights: assets, liabilities, and cash/debt insights.
    5. Key Ratios and operational metrics.
    6. Risks, challenges, and forward guidance.
    7. Provide quantitative data wherever available and explain implications.
    8. If info is missing, explicitly say: "Information not available in this document."
    9. Use bullet points, subheadings, and clear structure.
    """

    combined_response = ""
    for fname in filenames:
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            combined_response += f"### {fname}\n❌ File not found.\n\n"
            continue

        index = _load_or_create_index(path)
        prompt = followup_prompt_template
        response = index.as_query_engine().query(prompt)
        text = response.response if hasattr(response, "response") else str(response)
        text = re.sub(r"(\\$\\d+(?:,\\d+)?(?:\\.\\d+)?)", r"**\\1**", text)
        combined_response += f"### From {fname}\n{text.strip()}\n\n"

    return combined_response.strip()
