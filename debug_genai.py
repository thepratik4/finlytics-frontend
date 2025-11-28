import google.generativeai as genai
import langchain_google_genai
print(f"google-generativeai version: {genai.__version__}")
try:
    print(f"langchain-google-genai version: {langchain_google_genai.__version__}")
except:
    print("langchain-google-genai version not found")

try:
    print(f"Has MediaResolution: {hasattr(genai.types.GenerationConfig, 'MediaResolution')}")
except Exception as e:
    print(f"Error checking MediaResolution: {e}")

try:
    config = genai.types.GenerationConfig()
    print("GenerationConfig instantiated successfully")
except Exception as e:
    print(f"Error instantiating GenerationConfig: {e}")
