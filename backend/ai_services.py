import whisper
import google.generativeai as genai
from config import Config

# Configure Google Gemini
genai.configure(api_key=Config.GOOGLE_API_KEY)

# Load Local Whisper Model
print("Loading Whisper model... (this happens only once)")
whisper_model = whisper.load_model("base")