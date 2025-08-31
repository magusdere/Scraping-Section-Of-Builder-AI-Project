import scrapy
from dotenv import load_dotenv
from google import genai
import os
from scrapy.item import Field, Item
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import config
from firecrawl import Firecrawl
import json

# Importa la clase de tu spider de Mercado Libre
from meliModule import MercadoLibreSpider 

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

if __name__ == '__main__':
    # Paso 1: prompt del usuario (si no está ya en config)
    # Por si quieres que sea interactivo.
    config.user_prompt = input("Ingresa tu idea de negocio: ")

    # Paso 2: simplificar con Gemini
    try:
        llm_response_fc = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Según este prompt: '{config.user_prompt}', Resumí la idea de negocio en una sola frase simple, en el formato: [tipo de negocio] en [ubicación]. Por ejemplo para que te guies, el usuario ingresa: Estoy pensando en arrancar un negocio porque me gusta mucho la tecnología y veo que en Salta no hay tantas tiendas, entonces me gustaría algo de venta de celulares, accesorios y notebooks, ¿qué opinás?, ahi tu devuelves: venta de artículos de tecnología en Salta Argentina"
        )
        query_simplificada = llm_response_fc.text.strip()
    except Exception as e:
        print(f"❌ Error al llamar a la API de Gemini para Firecrawl: {e}")
        query_simplificada = config.user_prompt # Usa el prompt original como fallback
    
    # ----------------------------------------------------
    # 🎯 Lógica de Firecrawl
    # ----------------------------------------------------
    print("\n🚀 Iniciando búsqueda con Firecrawl...")
    results = firecrawl_client.search(
        query=query_simplificada,
        limit=10,
    )

    results_dict = results.model_dump()
    classified_results = []
    
    SOCIAL_DOMAINS = ["facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "tiktok.com", "youtube.com"]
    MARKETPLACE_DOMAINS = ["mercadolibre.com", "mercadolibre.com.ar", "olx.com", "amazon.com", "amazon.com.ar", "mlstatic.com"]

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

    with open("resultados_clasificados.json", "w", encoding="utf-8") as f:
        json.dump(classified_results, f, ensure_ascii=False, indent=4)

    print("✅ Resultados de Firecrawl guardados en resultados_clasificados.json")

    # ----------------------------------------------------
    # 🎯 Lógica de Scrapy
    # ----------------------------------------------------
    # Vuelve a llamar a Gemini para obtener la palabra clave para Mercado Libre
    print("\n🔍 Extrayendo palabra clave para Mercado Libre...")
    try:
        llm_response_ml = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Del siguiente texto: '{config.user_prompt}', extrae una frase de búsqueda completa para usar en un motor de búsqueda. "
                     f"Devuelve solo la frase de búsqueda, por ejemplo: 'zapatillas de correr', 'muebles de madera', o 'articulos de camping'."
                     f"Si el texto es 'quiero vender artículos de fútbol', devuelve 'articulos de futbol'."
        )
        keyword_meli = llm_response_ml.text.strip().replace(" ", "-")
    except Exception as e:
        print(f"❌ Error al llamar a la API de Gemini para Scrapy: {e}")
        keyword_meli = "celulares"
    print(f"🚀 Iniciando scraping en Mercado Libre para: {keyword_meli}")

    # Iniciar el proceso de Scrapy
    settings = get_project_settings()
    settings['FEED_FORMAT'] = 'json'  
    settings['FEED_URI'] = 'articulos_meli.json'
    process = CrawlerProcess(settings)
    process.crawl(MercadoLibreSpider, keyword=keyword_meli)
    process.start()

