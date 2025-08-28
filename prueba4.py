import scrapy
from scrapy.item import Field, Item

# Definimos la estructura de los datos que queremos extraer
class Articulo(Item):
    titulo = Field()
    precio = Field()

class MercadoLibreSpider(scrapy.Spider):
    name = 'mercadoLibre'
    
    # Configuraciones personalizadas para simular un navegador
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }
    
    # URL de inicio para la búsqueda de "televisores"
    start_urls = ['https://listado.mercadolibre.com.ar/televisores']

    def parse(self, response):
        """
        Método principal que procesa la página de resultados de búsqueda.
        """
        # Seleccionamos todos los contenedores de productos en la lista de resultados
        productos = response.xpath('//li[contains(@class, "ui-search-layout__item")]')

        print("\n--- Resultados de la búsqueda en Mercado Libre ---\n")
        
        for producto in productos:
            # Extraemos el título del producto
            titulo = producto.xpath('.//a[contains(@class, "poly-component__title")]/text()').get()
            
            # Extraemos el precio
            precio = producto.xpath('.//span[contains(@class, "andes-money-amount__fraction")]/text()').get()

            # Extraemos el nombre del vendedor
            vendedor = producto.xpath('.//span[contains(@class, "poly-component__seller")]/text()').get()
            
            # Imprimimos los resultados directamente en la consola
            print(f"Título: {titulo}")
            print(f"Precio: ${precio}")
            print(f"Vendedor: {vendedor if vendedor else 'No disponible'}") # Manejamos el caso en que el vendedor no esté disponible

            print("-" * 30)