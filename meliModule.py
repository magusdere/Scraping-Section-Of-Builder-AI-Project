import scrapy
from scrapy.item import Field, Item

# -----------------------------
# 2️⃣ Definir estructura de los datos
# -----------------------------
class Articulo(Item):
    titulo = Field()
    precio = Field()
    vendedor = Field()

# -----------------------------
# 3️⃣ Definir Spider
# -----------------------------
class MercadoLibreSpider(scrapy.Spider):
    name = 'mercadoLibre'
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super(MercadoLibreSpider, self).__init__(*args, **kwargs)
        if keyword:
            self.start_urls = [f'https://listado.mercadolibre.com.ar/{keyword}']
        else:
            self.start_urls = ['https://listado.mercadolibre.com.ar/televisores']

    def parse(self, response):
        productos = response.xpath('//li[contains(@class, "ui-search-layout__item")]')

        print(f"\n--- Resultados de la búsqueda para '{self.start_urls[0].split('/')[-1]}' en Mercado Libre ---\n")

        for producto in productos:
            titulo = producto.xpath('.//a[contains(@class, "poly-component__title")]/text()').get()
            precio = producto.xpath('.//span[contains(@class, "andes-money-amount__fraction")]/text()').get()
            vendedor = producto.xpath('.//span[contains(@class, "poly-component__seller")]/text()').get()

            # ✅ CREAMOS Y DEVOLVEMOS EL OBJETO 'Item'
            item = Articulo()
            item['titulo'] = titulo.strip() if titulo else 'Título no disponible'
            item['precio'] = precio.strip() if precio else 'Precio no disponible'
            item['vendedor'] = vendedor.strip() if vendedor else 'Vendedor no disponible'
            
            yield item