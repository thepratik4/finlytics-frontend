import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except ImportError:
    pdfminer_extract_text = None

def extract_clean_text(filepath: str) -> str:
    """
    Extracts text from a PDF file and cleans it.
    """
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return ""

    text = ""
    # Try pdfminer first
    if pdfminer_extract_text:
        try:
            text = pdfminer_extract_text(filepath)
        except Exception as e:
            logger.error(f"Error extracting text with pdfminer: {e}")
    
    # If pdfminer failed or returned empty, we could try other libs if installed
    # For now, we rely on pdfminer as the primary tool
    
    if not text:
        return ""

    return clean_text(text)

def clean_text(text: str) -> str:
    """
    Cleans raw PDF text: removes excessive whitespace, fixes broken lines, etc.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a single newline (or double for paragraphs)
    # First, replace \r with \n
    text = text.replace('\r', '\n')
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Fix hyphenated words at end of lines (e.g. "finan-\ncial" -> "financial")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace 3+ newlines with 2 (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> list:
    """
    Splits text into chunks with overlap.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:])
            break
            
        # Try to find a sentence break near the end
        search_start = max(start, end - int(chunk_size * 0.1))
        match = re.search(r'[.!?]\s', text[search_start:end])
        
        if match:
            split_point = search_start + match.end()
            chunks.append(text[start:split_point])
            start = split_point
        else:
            chunks.append(text[start:end])
            start = end - overlap
            
    return chunks
