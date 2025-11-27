import os
import json
import logging
from services.utils import get_upload_path, write_gridfs_to_temp, cleanup_temp_files
from services.pdf_utils import extract_clean_text, chunk_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for heavy AI models
ChatGoogleGenerativeAI = None
genai = None

def _ensure_models():
    """
    Attempt to initialize heavy AI libraries.
    """
    global ChatGoogleGenerativeAI, genai
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        import google.generativeai as genai
        
        # Configure Gemini API
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if genai and GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            
        globals().setdefault('ChatGoogleGenerativeAI', ChatGoogleGenerativeAI)
        globals().setdefault('genai', genai)
        
    except Exception as e:
        logger.error(f"Heavy AI libraries not available: {e}")
        raise RuntimeError('Heavy AI libraries not available: ' + str(e))

def _get_llm():
    _ensure_models()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2, # Low temperature for structured output
    )

def analyze_pdfs(inputs: list):
    """
    Analyze PDFs and return structured JSON.
    """
    temp_paths = []
    resolved_paths = []
    
    try:
        # Resolve inputs
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
                    name = item.get("filename") or os.path.basename(tmp)
                    resolved_paths.append((name, tmp))
                elif item.get("filename"):
                    local_path = os.path.join(get_upload_path(), item["filename"])
                    if os.path.exists(local_path):
                        resolved_paths.append((item["filename"], local_path))
        
        if not resolved_paths:
            return {"error": "No valid PDFs found"}

        # Extract text
        full_text = ""
        for name, path in resolved_paths:
            text = extract_clean_text(path)
            full_text += f"\n\n--- Document: {name} ---\n{text}"
            
        # Analyze with LLM
        try:
            llm = _get_llm()
            
            prompt = f"""
            You are a professional financial analyst. Analyze the following financial document(s) text.
            
            Return a valid JSON object with the following structure:
            {{
              "summary": "A concise executive summary of the financial health and key events.",
              "financial_data": {{
                  "revenue": "Extracted value with unit (e.g. $10M) or 'N/A'",
                  "net_profit": "Extracted value or 'N/A'",
                  "expenses": "Extracted value or 'N/A'",
                  "cash_flow": "Extracted value or 'N/A'"
              }},
              "key_insights": [
                  "Insight 1",
                  "Insight 2",
                  "Insight 3"
              ],
              "sections": [
                  {{ "title": "Revenue Analysis", "content": "Detailed analysis..." }},
                  {{ "title": "Risks & Challenges", "content": "Detailed analysis..." }},
                  {{ "title": "Future Outlook", "content": "Detailed analysis..." }}
              ]
            }}
            
            Do not include Markdown formatting (like ```json). Return ONLY the raw JSON string.
            
            Document Text:
            {full_text[:30000]} 
            """
            # Truncate to avoid token limits if necessary, though Gemini has large context
            
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            # Clean potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            data = json.loads(content.strip())
            return data
            
        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            return {"error": f"AI Analysis failed: {str(e)}"}

    finally:
        cleanup_temp_files(temp_paths)

def ask_question(question: str, inputs: list = None):
    """
    Ask a question and return structured JSON response.
    """
    temp_paths = []
    resolved_paths = []
    
    try:
        # Resolve inputs (similar logic to analyze_pdfs, simplified for brevity)
        if inputs:
            for item in inputs:
                if isinstance(item, dict) and item.get("file_id"):
                    tmp = write_gridfs_to_temp(item["file_id"])
                    temp_paths.append(tmp)
                    name = item.get("filename") or os.path.basename(tmp)
                    resolved_paths.append((name, tmp))
                # ... handle other cases if needed ...
        
        # If no inputs provided, we might need to handle that, but for now assume inputs are passed
        
        full_text = ""
        for name, path in resolved_paths:
            text = extract_clean_text(path)
            full_text += f"\n\n--- Document: {name} ---\n{text}"
            
        if not full_text:
             return json.dumps({
                "summary": "No documents available to answer the question.",
                "financial_data": {},
                "key_insights": [],
                "sections": []
            })

        try:
            llm = _get_llm()
            
            prompt = f"""
            You are a financial analyst assistant. The user asked: "{question}"
            
            Based on the following document text, provide a structured answer in JSON format:
            {{
              "summary": "Direct answer to the user's question.",
              "financial_data": {{
                  "relevant_metric_1": "Value",
                  "relevant_metric_2": "Value"
              }},
              "key_insights": [
                  "Key point 1 related to question",
                  "Key point 2 related to question"
              ],
              "sections": [
                  {{ "title": "Detailed Answer", "content": "Comprehensive explanation..." }},
                  {{ "title": "Supporting Evidence", "content": "Quotes or data points from text..." }}
              ]
            }}
            
            If the answer is not in the text, state that in the summary.
            Do not include Markdown formatting. Return ONLY the raw JSON string.
            
            Document Text:
            {full_text[:30000]}
            """
            
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            # Validate JSON
            json.loads(content.strip())
            return content.strip() # Return stringified JSON for consistency with previous string return type
            
        except Exception as e:
            logger.error(f"AI Question failed: {e}")
            # Return a fallback JSON string
            return json.dumps({
                "summary": f"I encountered an error while processing your request: {str(e)}",
                "financial_data": {},
                "key_insights": [],
                "sections": []
            })

    finally:
        cleanup_temp_files(temp_paths)
