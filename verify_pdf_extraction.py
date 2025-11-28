import sys
import os

# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services.pdf_utils import pdfminer_extract_text

if pdfminer_extract_text:
    print("SUCCESS: pdfminer_extract_text is available")
else:
    print("FAILURE: pdfminer_extract_text is None")
