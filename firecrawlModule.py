from firecrawl import Firecrawl
from dotenv import load_dotenv
from google import genai
import os
import json
import config

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

# Paso 1: prompt del usuario
config.user_prompt = input("Ingresa tu idea de negocio: ")

# Paso 2: simplificar con Gemini
llm_response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Según este prompt: '{config.user_prompt}', Resumí la idea de negocio en una sola frase simple, en el formato: [tipo de negocio] en [ubicación]. Por ejemplo para que te guies, el usuario ingresa: Estoy pensando en arrancar un negocio porque me gusta mucho la tecnología y veo que en Salta no hay tantas tiendas, entonces me gustaría algo de venta de celulares, accesorios y notebooks, ¿qué opinás?, ahi tu devuelves: venta de artículos de tecnología en Salta Argentina"
)

# Extraer el texto generado
query_simplificada = llm_response.text.strip()

results = firecrawl_client.search(
    query=query_simplificada,
    limit=10,
)


# Convertir a dict (usar model_dump() si tu Firecrawl es Pydantic v2)
results_dict = results.model_dump()  

# Lista donde guardaremos resultados clasificados
classified_results = []

# Palabras clave para clasificación
SOCIAL_DOMAINS = ["facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "tiktok.com", "youtube.com"]
MARKETPLACE_DOMAINS = ["mercadolibre.com", "mercadolibre.com.ar", "olx.com", "amazon.com", "amazon.com.ar", "mlstatic.com"]

# Iterar sobre los items de 'web'
for item in results_dict.get("web", []):
    url = item.get("url", "").lower()
    
    if any(social in url for social in SOCIAL_DOMAINS):
        categoria = "red_social"
    elif any(market in url for market in MARKETPLACE_DOMAINS):
        categoria = "marketplace"
    else:
        categoria = "web_local"

    classified_results.append({
        "url": item.get("url"),
        "title": item.get("title"),
        "description": item.get("description"),
        "categoria": categoria
    })

# Guardar JSON final
with open("resultados_clasificados.json", "w", encoding="utf-8") as f:
    json.dump(classified_results, f, ensure_ascii=False, indent=4)

print("✅ Resultados clasificados guardados en resultados_clasificados.json")

