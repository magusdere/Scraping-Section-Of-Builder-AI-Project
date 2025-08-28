# poc_hibrido.py
from dotenv import load_dotenv
from google import genai
import os

# Firecrawl
from firecrawl import Firecrawl

# -----------------------------
# 1️⃣ Cargar API Keys
# -----------------------------
# Cargar variables desde apikey.env
load_dotenv("apikey.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Inicializar clientes
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
firecrawl_client = Firecrawl(api_key=FIRECRAWL_API_KEY)

# -----------------------------
# 2️⃣ Prompt de usuario
# -----------------------------
user_prompt = input("Ingresa tu consulta: ")

# LLM sugiere URL y qué scrapear
llm_response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Según este prompt: '{user_prompt}', dame una URL pública y qué información scrapear. Devuelve sólo la URL y tags o selectores si es posible."
)

print("\nLLM sugiere:", llm_response.text)

# -----------------------------
# 5️⃣ LLM resume la info
# -----------------------------
summary = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Resume esta información para el usuario: {scraped_data[:10]}"
)

