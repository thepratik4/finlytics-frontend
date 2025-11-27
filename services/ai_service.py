# import os
# import re
# from dotenv import load_dotenv
# from textblob import TextBlob
# from services.utils import get_upload_path

# # Load environment variables
# load_dotenv()

# # ---------------------------------------------
# # Import AI + NLP libraries
# # ---------------------------------------------
# try:
#     import torch
#     from llama_index.core import VectorStoreIndex, download_loader, Settings
#     from langchain.embeddings import HuggingFaceEmbeddings
#     from langchain_google_genai import ChatGoogleGenerativeAI
#     import google.generativeai as genai
# except Exception as e:
#     # If packages not installed, fail gracefully and guide the user
#     print("⚠️ Some AI libraries are missing. Install all dependencies from requirements.txt")
#     print("Error details:", str(e))
#     VectorStoreIndex = None
#     download_loader = None
#     Settings = None
#     HuggingFaceEmbeddings = None
#     ChatGoogleGenerativeAI = None
#     genai = None
#     torch = None


# # ---------------------------------------------
# # Configure Gemini API
# # ---------------------------------------------
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if genai and GOOGLE_API_KEY:
#     genai.configure(api_key=GOOGLE_API_KEY)


# # ---------------------------------------------
# # Choose device for embeddings
# # ---------------------------------------------
# device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"

# # Cache to avoid reloading models or indexes unnecessarily
# index_cache = {}


# # ---------------------------------------------
# # System prompt (same as original Streamlit logic)
# # ---------------------------------------------
# SYSTEM_PROMPT = """
# [INST]
# <>
#     You are a professional financial analyst assistant.
#     Analyze financial documents carefully and provide **clear, structured, data-backed insights**.

#     - Summarize the document with sections: Revenue, Expenses, Profitability, Cash Flow, Assets & Liabilities, Growth Drivers, Risks, Market Outlook.
#     - Highlight **positive signals** and **red flags**.
#     - Use bullet points or subheadings for clarity.
#     - Ground answers in the document; if info is missing, explicitly state it.
#     - Keep tone professional and concise.
# <>
# [/INST]
# """


# # ---------------------------------------------
# # Initialize LLM + embeddings
# # ---------------------------------------------
# def _ensure_models():
#     """Initializes and configures the embeddings + LLM models once."""
#     global embeddings, llm

#     if "embeddings" in globals() and globals().get("embeddings") is not None:
#         return  # already loaded

#     if not HuggingFaceEmbeddings or not ChatGoogleGenerativeAI:
#         raise RuntimeError("AI packages not installed. Please install dependencies from requirements.txt")

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         model_kwargs={"device": device},
#     )

#     llm = ChatGoogleGenerativeAI(
#         model="models/gemini-2.5-flash",
#         google_api_key=GOOGLE_API_KEY,
#         system_instruction=SYSTEM_PROMPT,
#     )

#     Settings.llm = llm
#     Settings.embed_model = embeddings


# # ---------------------------------------------
# # Load and cache PDF Index
# # ---------------------------------------------
# def _load_or_create_index(filepath: str):
#     """Loads or builds a LlamaIndex for a given PDF file."""
#     if VectorStoreIndex is None:
#         raise RuntimeError("llama_index not installed. Please install dependencies.")

#     filename = os.path.basename(filepath)
#     if filename in index_cache:
#         return index_cache[filename]

#     PyMuPDFReader = download_loader("PyMuPDFReader")
#     loader = PyMuPDFReader()
#     documents = loader.load(file_path=filepath, metadata=True)
#     index = VectorStoreIndex.from_documents(documents)
#     index_cache[filename] = index
#     return index


# # ---------------------------------------------
# # Analyze PDFs
# # ---------------------------------------------
# def analyze_pdfs(filenames: list):
#     """
#     Analyze one or more uploaded PDF financial documents.
#     Returns a dictionary mapping filename → summarized insights.
#     """
#     _ensure_models()
#     base_dir = get_upload_path()
#     individual_results = {}
#     combined_texts = []
#     sentiment_results = {}

#     analysis_prompt = """
#     Provide a comprehensive and structured overview of this financial document.
#     Include: Executive Summary, Revenue & Sales, Profitability, Expenses, Balance Sheet Highlights, Cash Flow, Growth Drivers, Risks, and Future Outlook.
#     Use bullet points and sections. Mention missing info explicitly.
#     """

#     for fname in filenames:
#         path = os.path.join(base_dir, fname)
#         if not os.path.exists(path):
#             individual_results[fname] = "❌ File not found"
#             sentiment_results[fname] = {"error": "File not found"}
#             continue

#         index = _load_or_create_index(path)
#         response = index.as_query_engine().query(analysis_prompt)
#         text = response.response if hasattr(response, "response") else str(response)
#         text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

#         individual_results[fname] = text.strip()
#         combined_texts.append({
#             "filename": fname,
#             "text": text,
#             "index": index
#         })
#         sentiment_results[fname] = _analyze_sentiment(text)

#     # Combined analysis (if multiple files)
#     combined_analysis = None
#     if len(combined_texts) > 1:
#         combined_analysis = _perform_combined_analysis(combined_texts)

#     # Overall sentiment (if multiple files)
#     overall_sentiment = None
#     if len(sentiment_results) > 1:
#         overall_sentiment = _calculate_overall_sentiment(sentiment_results)

#     return {
#         "individual_analysis": individual_results,
#         "combined_analysis": combined_analysis,
#         "sentiment_analysis": sentiment_results,
#         "overall_sentiment": overall_sentiment
#     }

# def _perform_combined_analysis(docs: list) -> dict:
#     prompt = f"""
#     You are a financial analyst. Analyze these {len(docs)} reports collectively:
#     1️⃣ Comparative overview (revenue, expenses, margins)
#     2️⃣ Trend analysis across documents
#     3️⃣ Key differences and similarities
#     4️⃣ Consolidated insights
#     5️⃣ Investment and risk perspective
#     Be detailed and use financial reasoning.
#     """

#     index = docs[0]["index"]
#     doc_list = "\n".join([f"- {d['filename']}" for d in docs])
#     full_prompt = f"Documents analyzed:\n{doc_list}\n\n{prompt}"

#     response = index.as_query_engine().query(full_prompt)
#     text = response.response if hasattr(response, "response") else str(response)
#     text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

#     return {
#         "analysis": text.strip(),
#         "documents_analyzed": [d["filename"] for d in docs],
#         "document_count": len(docs)
#     }

# def _analyze_sentiment(text: str) -> dict:
#     blob = TextBlob(text)
#     polarity = blob.sentiment.polarity
#     subjectivity = blob.sentiment.subjectivity

#     if polarity > 0.3:
#         label = "Positive 📈"
#     elif polarity < -0.3:
#         label = "Negative 📉"
#     else:
#         label = "Neutral ➡️"

#     positive_words = ["growth", "profit", "increase", "strong", "improvement", "success"]
#     negative_words = ["loss", "decline", "decrease", "weak", "risk", "concern"]

#     t = text.lower()
#     pos_count = sum(1 for w in positive_words if w in t)
#     neg_count = sum(1 for w in negative_words if w in t)

#     return {
#         "polarity": round(polarity, 3),
#         "subjectivity": round(subjectivity, 3),
#         "sentiment": label,
#         "positive_signals": pos_count,
#         "negative_signals": neg_count,
#         "interpretation": _interpret_sentiment(polarity, subjectivity, pos_count, neg_count)
#     }


# def _interpret_sentiment(polarity, subjectivity, pos, neg):
#     desc = []
#     if polarity > 0.5:
#         desc.append("Strongly positive outlook")
#     elif polarity > 0.3:
#         desc.append("Moderately positive outlook")
#     elif polarity < -0.3:
#         desc.append("Concerning indicators present")
#     else:
#         desc.append("Balanced or neutral tone")

#     desc.append("subjective" if subjectivity > 0.6 else "objective")

#     if pos > neg:
#         desc.append(f"focus on growth ({pos} positive cues)")
#     elif neg > pos:
#         desc.append(f"mentions challenges ({neg} negative cues)")

#     return " - ".join(desc)


# def _calculate_overall_sentiment(sentiments: dict) -> dict:
#     valid = [s for s in sentiments.values() if "error" not in s]
#     if not valid:
#         return {"error": "No valid sentiment data"}

#     avg_p = sum(s["polarity"] for s in valid) / len(valid)
#     avg_s = sum(s["subjectivity"] for s in valid) / len(valid)
#     total_pos = sum(s["positive_signals"] for s in valid)
#     total_neg = sum(s["negative_signals"] for s in valid)

#     if avg_p > 0.3:
#         label = "Positive 📈"
#     elif avg_p < -0.3:
#         label = "Negative 📉"
#     else:
#         label = "Neutral ➡️"

#     return {
#         "average_polarity": round(avg_p, 3),
#         "average_subjectivity": round(avg_s, 3),
#         "overall_sentiment": label,
#         "total_positive_signals": total_pos,
#         "total_negative_signals": total_neg,
#         "documents_analyzed": len(valid),
#         "summary": f"Overall sentiment is {label} across {len(valid)} reports."
#     }


# # ---------------------------------------------
# # Ask questions about PDFs
# # ---------------------------------------------
# def ask_question(question: str, filenames: list = None):
#     """
#     Ask a follow-up question across uploaded PDFs.
#     Returns combined structured answer.
#     """
#     _ensure_models()
#     base_dir = get_upload_path()
#     if not filenames:
#         filenames = list(index_cache.keys())

#     if not filenames:
#         return "⚠️ No PDFs available for analysis."

#     followup_prompt_template = f"""
#     The user asked: "{question}"

#     You are a professional financial analyst assistant. Using the uploaded financial documents, provide a **comprehensive, structured, and insightful response**. Follow these instructions:

#     1. Reference each PDF separately. Start each section with the filename.
#     2. Provide an Executive Summary: key takeaways and overall financial health.
#     3. Revenue Analysis: comment on trends, growth/decline, costs, and margins.
#     4. Balance Sheet Highlights: assets, liabilities, and cash/debt insights.
#     5. Key Ratios and operational metrics.
#     6. Risks, challenges, and forward guidance.
#     7. Provide quantitative data wherever available and explain implications.
#     8. If info is missing, explicitly say: "Information not available in this document."
#     9. Use bullet points, subheadings, and clear structure.
#     """

#     combined_response = ""
#     for fname in filenames:
#         path = os.path.join(base_dir, fname)
#         if not os.path.exists(path):
#             combined_response += f"### {fname}\n❌ File not found.\n\n"
#             continue

#         index = _load_or_create_index(path)
#         prompt = followup_prompt_template
#         response = index.as_query_engine().query(prompt)
#         text = response.response if hasattr(response, "response") else str(response)
#         text = re.sub(r"(\\$\\d+(?:,\\d+)?(?:\\.\\d+)?)", r"**\\1**", text)
#         combined_response += f"### From {fname}\n{text.strip()}\n\n"

#     return combined_response.strip()

# # update 1
# import os
# import re
# from dotenv import load_dotenv
# from textblob import TextBlob
# from services.utils import get_upload_path, write_gridfs_to_temp

# # Load environment variables
# load_dotenv()

# # ---------------------------------------------
# # Import AI + NLP libraries
# # ---------------------------------------------
# try:
#     import torch
#     from llama_index.core import VectorStoreIndex, download_loader, Settings
#     from langchain.embeddings import HuggingFaceEmbeddings
#     from langchain_google_genai import ChatGoogleGenerativeAI
#     import google.generativeai as genai
# except Exception as e:
#     # If packages not installed, fail gracefully and guide the user
#     print("⚠️ Some AI libraries are missing. Install all dependencies from requirements.txt")
#     print("Error details:", str(e))
#     VectorStoreIndex = None
#     download_loader = None
#     Settings = None
#     HuggingFaceEmbeddings = None
#     ChatGoogleGenerativeAI = None
#     genai = None
#     torch = None


# # ---------------------------------------------
# # Configure Gemini API
# # ---------------------------------------------
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if genai and GOOGLE_API_KEY:
#     genai.configure(api_key=GOOGLE_API_KEY)


# # ---------------------------------------------
# # Choose device for embeddings
# # ---------------------------------------------
# device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"

# # Cache to avoid reloading models or indexes unnecessarily
# index_cache = {}


# # ---------------------------------------------
# # System prompt (same as original Streamlit logic)
# # ---------------------------------------------
# SYSTEM_PROMPT = """
# [INST]
# <>
#     You are a professional financial analyst assistant.
#     Analyze financial documents carefully and provide **clear, structured, data-backed insights**.

#     - Summarize the document with sections: Revenue, Expenses, Profitability, Cash Flow, Assets & Liabilities, Growth Drivers, Risks, Market Outlook.
#     - Highlight **positive signals** and **red flags**.
#     - Use bullet points or subheadings for clarity.
#     - Ground answers in the document; if info is missing, explicitly state it.
#     - Keep tone professional and concise.
# <>
# [/INST]
# """


# # ---------------------------------------------
# # Utility: detect if a string looks like a GridFS ObjectId
# # ---------------------------------------------
# def _looks_like_gridfs_id(value: str) -> bool:
#     """
#     Heuristic: MongoDB ObjectId is a 24-character hex string.
#     """
#     if not isinstance(value, str):
#         return False
#     return bool(re.fullmatch(r"[0-9a-fA-F]{24}", value))


# # ---------------------------------------------
# # Initialize LLM + embeddings
# # ---------------------------------------------
# def _ensure_models():
#     """Initializes and configures the embeddings + LLM models once."""
#     global embeddings, llm

#     if "embeddings" in globals() and globals().get("embeddings") is not None:
#         return  # already loaded

#     if not HuggingFaceEmbeddings or not ChatGoogleGenerativeAI:
#         raise RuntimeError("AI packages not installed. Please install dependencies from requirements.txt")

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         model_kwargs={"device": device},
#     )

#     llm = ChatGoogleGenerativeAI(
#         model="models/gemini-2.5-flash",
#         google_api_key=GOOGLE_API_KEY,
#         system_instruction=SYSTEM_PROMPT,
#     )

#     Settings.llm = llm
#     Settings.embed_model = embeddings


# # ---------------------------------------------
# # Load and cache PDF Index
# # ---------------------------------------------
# def _load_or_create_index(filepath: str, cache_key: str | None = None):
#     """
#     Loads or builds a LlamaIndex for a given PDF file.

#     cache_key:
#         - If provided, used as the cache key (e.g., GridFS file id).
#         - Otherwise, the basename of the filepath is used.
#     """
#     if VectorStoreIndex is None:
#         raise RuntimeError("llama_index not installed. Please install dependencies.")

#     key = cache_key or os.path.basename(filepath)

#     if key in index_cache:
#         return index_cache[key]

#     PyMuPDFReader = download_loader("PyMuPDFReader")
#     loader = PyMuPDFReader()
#     documents = loader.load(file_path=filepath, metadata=True)
#     index = VectorStoreIndex.from_documents(documents)
#     index_cache[key] = index
#     return index


# # ---------------------------------------------
# # Analyze PDFs
# # ---------------------------------------------
# def analyze_pdfs(filenames: list):
#     """
#     Analyze one or more uploaded PDF financial documents.

#     filenames:
#         - Can be a list of local filenames (e.g. "sbi_jan.pdf"), OR
#         - A list of GridFS file id strings (24-char hex).

#     Returns a dictionary mapping identifier → summarized insights.
#     """
#     _ensure_models()
#     base_dir = get_upload_path()
#     individual_results = {}
#     combined_texts = []
#     sentiment_results = {}

#     analysis_prompt = """
#     Provide a comprehensive and structured overview of this financial document.
#     Include: Executive Summary, Revenue & Sales, Profitability, Expenses, Balance Sheet Highlights, Cash Flow, Growth Drivers, Risks, and Future Outlook.
#     Use bullet points and sections. Mention missing info explicitly.
#     """

#     for fname in filenames:
#         tmp_path = None
#         try:
#             # Decide whether this is a GridFS id or a local filename
#             if _looks_like_gridfs_id(fname):
#                 # GridFS: write to temp file
#                 tmp_path = write_gridfs_to_temp(fname)
#                 path = tmp_path
#                 cache_key = fname  # use GridFS id as cache key
#             else:
#                 # Local file in uploads/statements
#                 path = os.path.join(base_dir, fname)
#                 cache_key = fname

#             if not os.path.exists(path):
#                 individual_results[fname] = "❌ File not found"
#                 sentiment_results[fname] = {"error": "File not found"}
#                 continue

#             index = _load_or_create_index(path, cache_key=cache_key)
#             response = index.as_query_engine().query(analysis_prompt)
#             text = response.response if hasattr(response, "response") else str(response)
#             text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

#             individual_results[fname] = text.strip()
#             combined_texts.append({
#                 "filename": fname,
#                 "text": text,
#                 "index": index
#             })
#             sentiment_results[fname] = _analyze_sentiment(text)

#         finally:
#             # Clean up temporary file if we created one
#             if tmp_path and os.path.exists(tmp_path):
#                 os.remove(tmp_path)

#     # Combined analysis (if multiple files)
#     combined_analysis = None
#     if len(combined_texts) > 1:
#         combined_analysis = _perform_combined_analysis(combined_texts)

#     # Overall sentiment (if multiple files)
#     overall_sentiment = None
#     if len(sentiment_results) > 1:
#         overall_sentiment = _calculate_overall_sentiment(sentiment_results)

#     return {
#         "individual_analysis": individual_results,
#         "combined_analysis": combined_analysis,
#         "sentiment_analysis": sentiment_results,
#         "overall_sentiment": overall_sentiment
#     }


# def _perform_combined_analysis(docs: list) -> dict:
#     prompt = f"""
#     You are a financial analyst. Analyze these {len(docs)} reports collectively:
#     1️⃣ Comparative overview (revenue, expenses, margins)
#     2️⃣ Trend analysis across documents
#     3️⃣ Key differences and similarities
#     4️⃣ Consolidated insights
#     5️⃣ Investment and risk perspective
#     Be detailed and use financial reasoning.
#     """

#     index = docs[0]["index"]
#     doc_list = "\n".join([f"- {d['filename']}" for d in docs])
#     full_prompt = f"Documents analyzed:\n{doc_list}\n\n{prompt}"

#     response = index.as_query_engine().query(full_prompt)
#     text = response.response if hasattr(response, "response") else str(response)
#     text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)

#     return {
#         "analysis": text.strip(),
#         "documents_analyzed": [d["filename"] for d in docs],
#         "document_count": len(docs)
#     }


# def _analyze_sentiment(text: str) -> dict:
#     blob = TextBlob(text)
#     polarity = blob.sentiment.polarity
#     subjectivity = blob.sentiment.subjectivity

#     if polarity > 0.3:
#         label = "Positive 📈"
#     elif polarity < -0.3:
#         label = "Negative 📉"
#         # NOTE: fall-through else is neutral
#     else:
#         label = "Neutral ➡️"

#     positive_words = ["growth", "profit", "increase", "strong", "improvement", "success"]
#     negative_words = ["loss", "decline", "decrease", "weak", "risk", "concern"]

#     t = text.lower()
#     pos_count = sum(1 for w in positive_words if w in t)
#     neg_count = sum(1 for w in negative_words if w in t)

#     return {
#         "polarity": round(polarity, 3),
#         "subjectivity": round(subjectivity, 3),
#         "sentiment": label,
#         "positive_signals": pos_count,
#         "negative_signals": neg_count,
#         "interpretation": _interpret_sentiment(polarity, subjectivity, pos_count, neg_count)
#     }


# def _interpret_sentiment(polarity, subjectivity, pos, neg):
#     desc = []
#     if polarity > 0.5:
#         desc.append("Strongly positive outlook")
#     elif polarity > 0.3:
#         desc.append("Moderately positive outlook")
#     elif polarity < -0.3:
#         desc.append("Concerning indicators present")
#     else:
#         desc.append("Balanced or neutral tone")

#     desc.append("subjective" if subjectivity > 0.6 else "objective")

#     if pos > neg:
#         desc.append(f"focus on growth ({pos} positive cues)")
#     elif neg > pos:
#         desc.append(f"mentions challenges ({neg} negative cues)")

#     return " - ".join(desc)


# def _calculate_overall_sentiment(sentiments: dict) -> dict:
#     valid = [s for s in sentiments.values() if "error" not in s]
#     if not valid:
#         return {"error": "No valid sentiment data"}

#     avg_p = sum(s["polarity"] for s in valid) / len(valid)
#     avg_s = sum(s["subjectivity"] for s in valid) / len(valid)
#     total_pos = sum(s["positive_signals"] for s in valid)
#     total_neg = sum(s["negative_signals"] for s in valid)

#     if avg_p > 0.3:
#         label = "Positive 📈"
#     elif avg_p < -0.3:
#         label = "Negative 📉"
#     else:
#         label = "Neutral ➡️"

#     return {
#         "average_polarity": round(avg_p, 3),
#         "average_subjectivity": round(avg_s, 3),
#         "overall_sentiment": label,
#         "total_positive_signals": total_pos,
#         "total_negative_signals": total_neg,
#         "documents_analyzed": len(valid),
#         "summary": f"Overall sentiment is {label} across {len(valid)} reports."
#     }


# # ---------------------------------------------
# # Ask questions about PDFs
# # ---------------------------------------------
# def ask_question(question: str, filenames: list = None):
#     """
#     Ask a follow-up question across uploaded PDFs.

#     filenames:
#         - If provided: list of identifiers (local filenames or GridFS ids).
#         - If None: use whatever is already in index_cache.

#     Returns combined structured answer.
#     """
#     _ensure_models()
#     base_dir = get_upload_path()

#     if not filenames:
#         filenames = list(index_cache.keys())

#     if not filenames:
#         return "⚠️ No PDFs available for analysis."

#     followup_prompt_template = f"""
#     The user asked: "{question}"

#     You are a professional financial analyst assistant. Using the uploaded financial documents, provide a **comprehensive, structured, and insightful response**. Follow these instructions:

#     1. Reference each PDF separately. Start each section with the filename.
#     2. Provide an Executive Summary: key takeaways and overall financial health.
#     3. Revenue Analysis: comment on trends, growth/decline, costs, and margins.
#     4. Balance Sheet Highlights: assets, liabilities, and cash/debt insights.
#     5. Key Ratios and operational metrics.
#     6. Risks, challenges, and forward guidance.
#     7. Provide quantitative data wherever available and explain implications.
#     8. If info is missing, explicitly say: "Information not available in this document."
#     9. Use bullet points, subheadings, and clear structure.
#     """

#     combined_response = ""
#     for fname in filenames:
#         tmp_path = None
#         try:
#             if _looks_like_gridfs_id(fname):
#                 tmp_path = write_gridfs_to_temp(fname)
#                 path = tmp_path
#                 cache_key = fname
#             else:
#                 path = os.path.join(base_dir, fname)
#                 cache_key = fname

#             if not os.path.exists(path):
#                 combined_response += f"### {fname}\n❌ File not found.\n\n"
#                 continue

#             index = _load_or_create_index(path, cache_key=cache_key)
#             prompt = followup_prompt_template
#             response = index.as_query_engine().query(prompt)
#             text = response.response if hasattr(response, "response") else str(response)
#             text = re.sub(r"(\\$\\d+(?:,\\d+)?(?:\\.\\d+)?)", r"**\\1**", text)
#             combined_response += f"### From {fname}\n{text.strip()}\n\n"

#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 os.remove(tmp_path)

#     return combined_response.strip()

# update 2
# --- in services/ai_service.py: replace analyze_pdfs(...) and ask_question(...) with these ---

from services.utils import get_upload_path, write_gridfs_to_temp, cleanup_temp_files
import os
import re

# Fallback lightweight PDF extraction + summarization utilities
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None

try:
    from textblob import TextBlob
except Exception:
    TextBlob = None


def _extract_text_simple(path: str) -> str:
    """
    Try to extract text from a PDF using pdfminer. If unavailable, return empty string.
    """
    if not pdfminer_extract_text:
        return ""
    try:
        text = pdfminer_extract_text(path)
        if not text:
            return ""
        return text
    except Exception:
        return ""


def _preprocess_text(text: str) -> str:
    # Basic cleaning: normalize whitespace, remove repeated newlines
    if not text:
        return ""
    t = re.sub(r"\r", "\n", text)
    t = re.sub(r"\n{2,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def _summarize_simple(text: str) -> dict:
    """
    Produce a simple extractive summary and sectioned bullets using keyword matching.
    This is a lightweight fallback when LLMs are not available.
    """
    out = {
        "executive_summary": "",
        "revenue_expenses": "",
        "profitability": "",
        "cashflow": "",
        "risks_outlook": "",
    }
    if not text:
        return out

    # split into sentences (very simple)
    sents = re.split(r"(?<=[\.\!?])\s+", text)
    # executive summary: first 3 non-empty sentences
    non_empty = [s.strip() for s in sents if s and len(s.strip()) > 20]
    out["executive_summary"] = " ".join(non_empty[:3])

    lower = text.lower()
    def find_chunk(keywords):
        for kw in keywords:
            if kw in lower:
                # return surrounding text: find first occurrence
                idx = lower.find(kw)
                start = max(0, idx - 200)
                end = min(len(text), idx + 400)
                return text[start:end].strip()
        return "Information not found in document."

    out["revenue_expenses"] = find_chunk(["revenue", "sales", "turnover", "expense", "expenses"]) or out["revenue_expenses"]
    out["profitability"] = find_chunk(["profit", "net profit", "loss", "ebitda", "margin"]) or out["profitability"]
    out["cashflow"] = find_chunk(["cash", "cash flow", "operating cash", "cashflow"]) or out["cashflow"]
    out["risks_outlook"] = find_chunk(["risk", "uncertain", "outlook", "guidance", "concern"]) or out["risks_outlook"]

    return out


def _sentiment_simple(text: str) -> dict:
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "Neutral"}
    if TextBlob:
        try:
            tb = TextBlob(text)
            p = round(tb.sentiment.polarity, 3)
            s = round(tb.sentiment.subjectivity, 3)
            label = "Neutral ➡️"
            if p > 0.3:
                label = "Positive 📈"
            elif p < -0.3:
                label = "Negative 📉"
            return {"polarity": p, "subjectivity": s, "sentiment": label}
        except Exception:
            pass

    # basic heuristic
    positive = ["growth", "profit", "increase", "strong", "improvement", "gain"]
    negative = ["loss", "decline", "decrease", "weak", "risk", "concern"]
    low = text.lower()
    pos = sum(1 for w in positive if w in low)
    neg = sum(1 for w in negative if w in low)
    p_score = 0.0
    if pos or neg:
        p_score = round((pos - neg) / max(1, pos + neg), 3)
    label = "Neutral ➡️"
    if p_score > 0.2:
        label = "Positive 📈"
    elif p_score < -0.2:
        label = "Negative 📉"
    return {"polarity": p_score, "subjectivity": 0.0, "sentiment": label}


# ... keep top-of-file code and _ensure_models/_load_or_create_index etc unchanged ...


def _ensure_models():
    """
    Attempt to initialize heavy AI libraries (llama_index, langchain embeddings, etc.).
    If imports fail, raise RuntimeError so callers know heavy models are unavailable.
    """
    global VectorStoreIndex, download_loader, Settings, HuggingFaceEmbeddings, ChatGoogleGenerativeAI, genai, torch
    try:
        import torch
        from llama_index.core import VectorStoreIndex, download_loader, Settings
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain_google_genai import ChatGoogleGenerativeAI
        import google.generativeai as genai
        # assign to globals so other functions can use them
        globals().setdefault('VectorStoreIndex', VectorStoreIndex)
        globals().setdefault('download_loader', download_loader)
        globals().setdefault('Settings', Settings)
        globals().setdefault('HuggingFaceEmbeddings', HuggingFaceEmbeddings)
        globals().setdefault('ChatGoogleGenerativeAI', ChatGoogleGenerativeAI)
        globals().setdefault('genai', genai)
    except Exception as e:
        raise RuntimeError('Heavy AI libraries not available: ' + str(e))


def _load_or_create_index(filepath: str, cache_key: str | None = None):
    """
    Thin wrapper for building/loading an index using llama_index. If unavailable, raise.
    """
    if 'VectorStoreIndex' not in globals() or globals().get('VectorStoreIndex') is None:
        raise RuntimeError('VectorStoreIndex not available')
    key = cache_key or os.path.basename(filepath)
    if key in index_cache:
        return index_cache[key]
    PyMuPDFReader = download_loader('PyMuPDFReader')
    loader = PyMuPDFReader()
    documents = loader.load(file_path=filepath, metadata=True)
    index = VectorStoreIndex.from_documents(documents)
    index_cache[key] = index
    return index


def _analyze_sentiment(text: str) -> dict:
    # prefer TextBlob if available, otherwise fallback
    if TextBlob:
        try:
            tb = TextBlob(text)
            p = round(tb.sentiment.polarity, 3)
            s = round(tb.sentiment.subjectivity, 3)
            label = 'Neutral ➡️'
            if p > 0.3:
                label = 'Positive 📈'
            elif p < -0.3:
                label = 'Negative 📉'
            return {'polarity': p, 'subjectivity': s, 'sentiment': label}
        except Exception:
            pass
    return _sentiment_simple(text)


def _perform_combined_analysis(docs: list) -> dict:
    # If heavy LLMs available, this function should have been overridden; implement simple comparatives
    comp = {d['filename']: { 'revenue_mentions': len(re.findall(r"revenue|sales|turnover", d['text'], flags=re.IGNORECASE)), 'profit_mentions': len(re.findall(r"profit|ebitda|margin", d['text'], flags=re.IGNORECASE)) } for d in docs}
    return { 'comparative_overview': comp, 'documents_analyzed': [d['filename'] for d in docs] }


def _calculate_overall_sentiment(sentiments: dict) -> dict:
    valid = [s for s in sentiments.values() if isinstance(s, dict) and 'polarity' in s]
    if not valid:
        return {'error': 'No valid sentiment data'}
    avg_p = sum(s['polarity'] for s in valid) / len(valid)
    avg_s = sum(s.get('subjectivity', 0.0) for s in valid) / len(valid)
    label = 'Neutral ➡️'
    if avg_p > 0.3:
        label = 'Positive 📈'
    elif avg_p < -0.3:
        label = 'Negative 📉'
    return { 'average_polarity': round(avg_p,3), 'average_subjectivity': round(avg_s,3), 'overall_sentiment': label }


def analyze_pdfs(inputs: list):
    """
    Analyze one or more PDFs.

    `inputs` may be:
      - list of filenames that exist in uploads/statements/  (legacy)
      - list of dicts like {"pdf_meta_id": "<id>", "gridfs_id": "<gridfs_file_id>"}  OR
      - list of gridfs file id strings directly (we handle both)

    Returns the same structure as before.
    """
    # Try to initialize heavy AI models; if unavailable, fall back to lightweight analysis
    models_available = True
    try:
        _ensure_models()
    except Exception:
        models_available = False

    temp_paths = []
    try:
        # Resolve inputs -> concrete file paths (on disk)
        resolved_paths = []
        for item in inputs:
            if isinstance(item, str):
                # Could be a local filename or a gridfs file id: check local path first
                local_path = os.path.join(get_upload_path(), item)
                if os.path.exists(local_path):
                    resolved_paths.append((item, local_path))
                else:
                    # assume it's a GridFS file id; write to temp
                    tmp = write_gridfs_to_temp(item)
                    temp_paths.append(tmp)
                    resolved_paths.append((os.path.basename(tmp), tmp))
            elif isinstance(item, dict):
                # Expect item to contain either "file_id" (gridfs) or "filename"
                if item.get("file_id"):
                    tmp = write_gridfs_to_temp(item["file_id"])
                    temp_paths.append(tmp)
                    resolved_paths.append((os.path.basename(tmp), tmp))
                elif item.get("filename"):
                    local_path = os.path.join(get_upload_path(), item["filename"])
                    if os.path.exists(local_path):
                        resolved_paths.append((item["filename"], local_path))
                    else:
                        raise FileNotFoundError(f"Local file {item['filename']} not found")
                else:
                    raise ValueError("Invalid input dict for analyze_pdfs; expected 'file_id' or 'filename'")
            else:
                raise ValueError("Invalid input type for analyze_pdfs")

        # Now proceed to analyze using resolved_paths (list of (name, path))
        individual_results = {}
        combined_texts = []
        sentiment_results = {}

        analysis_prompt = """
        Provide a comprehensive and structured overview of this financial document.
        Include: Executive Summary, Revenue & Sales, Profitability, Expenses, Balance Sheet Highlights, Cash Flow, Growth Drivers, Risks, and Future Outlook.
        Use bullet points and sections. Mention missing info explicitly.
        """

        for name, path in resolved_paths:
            if not os.path.exists(path):
                individual_results[name] = "❌ File not found"
                sentiment_results[name] = {"error": "File not found"}
                continue

            # If heavy models + indexer available, use them; otherwise use lightweight fallback
            if models_available and 'VectorStoreIndex' in globals() and globals().get('VectorStoreIndex') is not None:
                index = _load_or_create_index(path)
                response = index.as_query_engine().query(analysis_prompt)
                text = response.response if hasattr(response, "response") else str(response)
                text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)
                individual_results[name] = text.strip()
                combined_texts.append({"filename": name, "text": text, "index": index})
                # try to call heavy sentiment analyzer if available
                try:
                    sentiment_results[name] = _analyze_sentiment(text)
                except Exception:
                    sentiment_results[name] = _sentiment_simple(text)
            else:
                # Fallback: extract text and produce simple summaries
                txt = _extract_text_simple(path)
                txt = _preprocess_text(txt)
                if not txt:
                    individual_results[name] = "❌ Unable to extract text from PDF (missing pdfminer or file is scanned)"
                    sentiment_results[name] = {"error": "No text extracted"}
                    continue
                summary = _summarize_simple(txt)
                individual_results[name] = summary
                combined_texts.append({"filename": name, "text": txt})
                sentiment_results[name] = _sentiment_simple(txt)

        combined_analysis = None
        if len(combined_texts) > 1:
            # if heavy models available, prefer the advanced combiner
            try:
                if models_available and 'VectorStoreIndex' in globals() and globals().get('VectorStoreIndex') is not None:
                    combined_analysis = _perform_combined_analysis(combined_texts)
                else:
                    # Lightweight combined insights: comparative overview by keyword counts
                    comp = {d['filename']: { 'revenue_mentions': len(re.findall(r"revenue|sales|turnover", d['text'], flags=re.IGNORECASE)), 'profit_mentions': len(re.findall(r"profit|ebitda|margin", d['text'], flags=re.IGNORECASE)) } for d in combined_texts}
                    combined_analysis = { 'comparative_overview': comp, 'documents_analyzed': [d['filename'] for d in combined_texts] }
            except Exception:
                combined_analysis = None

        overall_sentiment = None
        if len(sentiment_results) > 1:
            # try heavy overall sentiment calculation, otherwise lightweight average
            try:
                overall_sentiment = _calculate_overall_sentiment(sentiment_results)
            except Exception:
                vals = [v for v in sentiment_results.values() if isinstance(v, dict) and 'polarity' in v]
                if vals:
                    avg_p = sum(v['polarity'] for v in vals) / len(vals)
                    overall_sentiment = { 'average_polarity': round(avg_p,3), 'overall_sentiment': ('Positive' if avg_p>0.2 else 'Negative' if avg_p<-0.2 else 'Neutral') }
                else:
                    overall_sentiment = None

        return {
            "individual_analysis": individual_results,
            "combined_analysis": combined_analysis,
            "sentiment_analysis": sentiment_results,
            "overall_sentiment": overall_sentiment
        }

    finally:
        # cleanup temp files written from GridFS
        cleanup_temp_files(temp_paths)


def ask_question(question: str, inputs: list = None):
    """
    Ask a question across provided PDFs.

    `inputs` same format as analyze_pdfs: local filenames, gridfs ids, or dicts.
    If inputs is None, use index_cache (legacy behavior).
    """
    # Try heavy models; if unavailable, use lightweight keyword search fallback
    models_available = True
    try:
        _ensure_models()
    except Exception:
        models_available = False

    temp_paths = []
    try:
        if inputs is None:
            filenames_to_use = list(index_cache.keys())
            # If there are no cached filenames and no inputs, return message
            if not filenames_to_use:
                return "⚠️ No PDFs available for analysis."
            # Convert cache filenames into local path tuples
            resolved_paths = [(fn, os.path.join(get_upload_path(), fn)) for fn in filenames_to_use]
        else:
            # Resolve inputs similar to analyze_pdfs
            resolved_paths = []
            for item in inputs:
                if isinstance(item, str):
                    local_path = os.path.join(get_upload_path(), item)
                    if os.path.exists(local_path):
                        resolved_paths.append((item, local_path))
                    else:
                        tmp = write_gridfs_to_temp(item)
                        temp_paths.append(tmp)
                        resolved_paths.append((os.path.basename(tmp), tmp))
                elif isinstance(item, dict):
                    if item.get("file_id"):
                        tmp = write_gridfs_to_temp(item["file_id"])
                        temp_paths.append(tmp)
                        resolved_paths.append((os.path.basename(tmp), tmp))
                    elif item.get("filename"):
                        local_path = os.path.join(get_upload_path(), item["filename"])
                        if os.path.exists(local_path):
                            resolved_paths.append((item["filename"], local_path))
                        else:
                            return f"⚠️ File {item['filename']} not found."
                    else:
                        return "⚠️ Invalid input dict for ask_question."
                else:
                    return "⚠️ Invalid input type for ask_question."

        if not resolved_paths:
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
        for name, path in resolved_paths:
            if not os.path.exists(path):
                combined_response += f"### {name}\n❌ File not found.\n\n"
                continue

            if models_available and 'VectorStoreIndex' in globals() and globals().get('VectorStoreIndex') is not None:
                index = _load_or_create_index(path)
                response = index.as_query_engine().query(followup_prompt_template)
                text = response.response if hasattr(response, "response") else str(response)
                text = re.sub(r"(\$\d+(?:,\d+)?(?:\.\d+)?)", r"**\1**", text)
                combined_response += f"### From {name}\n{text.strip()}\n\n"
            else:
                txt = _extract_text_simple(path)
                txt = _preprocess_text(txt)
                if not txt:
                    combined_response += f"### {name}\n❌ Unable to extract text.\n\n"
                    continue
                # Simple keyword search: find sentences that contain question keywords
                qwords = re.findall(r"\w+", question.lower())
                sents = re.split(r"(?<=[\.\!?])\s+", txt)
                matches = []
                for s in sents:
                    low = s.lower()
                    if any(q in low for q in qwords if len(q) > 3):
                        matches.append(s.strip())
                if matches:
                    combined_response += f"### From {name}\n" + "\n".join(matches[:5]) + "\n\n"
                else:
                    # fallback: return executive summary
                    summary = _summarize_simple(txt)
                    combined_response += f"### From {name}\nExecutive summary:\n{summary.get('executive_summary')}\n\n"

        return combined_response.strip()

    finally:
        cleanup_temp_files(temp_paths)
