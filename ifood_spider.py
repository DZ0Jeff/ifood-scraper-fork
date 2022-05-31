# run the file using scrapy runspider ifood-spider.py -o output.csv
# inspired by https://github.com/nathan-cruz77/ifood/blob/master/ifood_spider.py
import json
import scrapy
import pandas as pd
import re


BASE_IFOOD_URL = 'https://www.ifood.com.br/delivery/'
BASE_AVATAR_URL = 'https://static-images.ifood.com.br/image/upload/f_auto,t_high/logosgde/'
#BASE_URL = 'https://marketplace.ifood.com.br/v1/merchants?latitude=-23.19529&longitude=-45.90321&channel=IFOOD'
BASE_PRODUCTS = [
    "monange deo aero 90g",
    "risque regular blister",
    "risqué regular blister",
    "paixão hidratante regular", # 
    "adidas deo aero", # 
    "monange cpp",
    "risque diamond gel regular",
    "paixão-oleo regular" # 
    "biocolor homem tonalizante homem",
    "monange deo roll on", #
    "monange deo roll-on", #
    "monange deo rollon", #
    "risque regular comercial",
    "risqué regular comercial",
]

class Restaurant(scrapy.Item):

    name = scrapy.Field()
    city = scrapy.Field()
    rating = scrapy.Field()
    price_range = scrapy.Field()
    delivery_time = scrapy.Field()
    delivery_fee = scrapy.Field()
    distance = scrapy.Field()
    category = scrapy.Field()
    avatar = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    paymentCodes = scrapy.Field()
    minimumOrderValue = scrapy.Field()
    regionGroup = scrapy.Field()
    catalogGroup = scrapy.Field()
    cnpj = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    ibge = scrapy.Field()
    product = scrapy.Field()
    promotional_price = scrapy.Field()
    original_price = scrapy.Field()
    # schedule removed due to errors and not being able to extract useful data
    #schedule = scrapy.Field()

    @staticmethod
    def parse_avatar(item):
        avatar = ''

        for resource in item['resources']:
            if resource['type'].lower() == 'logo':
                avatar = resource['fileName']

        if avatar:
            return ''.join([BASE_AVATAR_URL, avatar])

        return avatar

    # make it easier to split the lists later
    @staticmethod
    def parse_list(lista):
        return " $$ ".join(str(e) for e in lista)

    @staticmethod
    def match_products(match_array:list, target:str):
        """
        Filter word if matches the content (unorded)

        args:
        match_array: the array of words of match patterns
        target: the test to be matched

        return: bool
        """

        for match_pattern in match_array:
            splited = match_pattern.split(" ")
            splited = [f"(?=.*{w})" for w in splited]
            joined = "".join(splited)
            match = re.compile(joined)
            search_content = re.search(match, target)
            if search_content: return True
        
        return


class IfoodSpider(scrapy.Spider):
    name = 'ifood'

    def start_requests(self):
        filenames = ["data/cidades_target.xlsx", "data/coordinates_list.csv", "data/coordinates_list_filtered.csv"]
        # for filename in filenames:
            # if filename.endswith('.xlsx'):
        # df = pd.read_excel(filenames[0])
            
            # else:
        df = pd.read_csv(filenames[2])

            # you can use an smaller part of the df
            #df = df.iloc[5573:5660]
            # print(df)

        CHANNEL = "IFOOD"
        payload = {
            "supported-headers":[],
            "supported-cards":[
                "MERCHANT_LIST",
                "CATALOG_ITEM_LIST",
                "CATALOG_ITEM_LIST_V2",
                "FEATURED_MERCHANT_LIST",
                "CATALOG_ITEM_CAROUSEL",
                "BIG_BANNER_CAROUSEL",
                "IMAGE_BANNER",
                "MERCHANT_LIST_WITH_ITEMS_CAROUSEL",
                "SMALL_BANNER_CAROUSEL",
                "NEXT_CONTENT",
                "MERCHANT_CAROUSEL",
                "MERCHANT_TILE_CAROUSEL",
                "SIMPLE_MERCHANT_CAROUSEL",
                "INFO_CARD",
                "MERCHANT_LIST_V2",
                "ROUND_IMAGE_CAROUSEL",
                "BANNER_GRID",
                "MEDIUM_IMAGE_BANNER"
            ],
            "supported-actions":["card-content","catalog-item","last-restaurants","merchant","page","reorder","webmiddleware"]
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }

        for i in range(len(df)):
            # if filename.endswith('.xlsx'):
            # lat = df['Long'].iloc[i]
            # long = df['Lat'].iloc[i]
            # ibge = df['cod ibge'].iloc[i]

            # else:
            lat = df['Longitude'].iloc[i]
            long = df['Latitude'].iloc[i]
            ibge = df['codigo_ibge'].iloc[i]

            if lat == "#N/A" or long == "#N/A": continue
            # country = df['country'].iloc[i]
            
            # if country == "Colombia":
            #     CHANNEL = "COMEYA"

            # elif country == "Mexico":
            #     CHANNEL = ""

            # todo: debugger the v2 api call with post requests (check headers, format and query params)
            merchants = True
            if merchants:
                # get restaurants
                BASE_URL = f"https://marketplace.ifood.com.br/v1/merchants?latitude={lat}&longitude={long}&channel={CHANNEL}"

                yield scrapy.Request(f'{BASE_URL}&size=0', callback=self.parse_core, meta={"ibge": ibge, "base_url": BASE_URL, "merchants": merchants})
            
            else:
                # get specific produts
                store_type = ["MERCADO"] # "MERCADO_FARMACIA"
                BASE_URL = f"https://marketplace.ifood.com.br/v2/home?latitude={lat}&longitude={long}&channel=IFOOD&alias="

                for store in store_type:
                    yield scrapy.Request(f"{BASE_URL}{store}", method="POST", callback=self.parse_page, headers=headers, body=json.dumps(payload), meta={"ibge": ibge, "base_url": BASE_URL, "merchants": merchants})

    def parse_core(self, response):
        data = json.loads(response.text)

        total = data['total']
        pages_count = total // 100

        if total / 100 != total // 100:
            pages_count += 1

        for page in range(pages_count):
            yield scrapy.Request(f'{response.meta["base_url"]}&size={100}&page={page}', callback=self.parse_page, meta={"ibge": response.meta['ibge'], "merchants": response.meta['merchants']})

    def parse_page(self, response):
        # print('page!')
        # problem here!
        data = json.loads(response.text)
        merchants = response.meta["merchants"]

        if merchants:
            for items in data['merchants']:
                yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{items["id"]}/extra', callback=self.parse_details, meta={"ibge": response.meta['ibge'], "item": items, "merchants": merchants})
        
        else:
            for cards in data["sections"][0]["cards"]:
                try:
                    for contents in cards["data"]["contents"]:
                        # yield contents["id"]
                        yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{contents["id"]}/extra', callback=self.parse_details, meta={"ibge": response.meta['ibge'], "item": contents, "merchants": merchants})
                
                except KeyError:
                    pass

    def parse_details(self, response):
        data = json.loads(response.text)
        item = response.meta['item']
        
        yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{item["id"]}/menu', 
        callback=self.parse_menu, meta={"ibge": response.meta['ibge'], "item": item, "details": data, "merchants": response.meta["merchants"] })
    
    def parse_menu(self, response):
        item = response.meta['item']
        data = response.meta['details']

        cardapio = []
        filter_list = []
        
        for menus in response.json():
            for product in menus['itens']:
                id_product = product['id']
                descrição = product['description']
                try:
                    detalhes = product["details"] if product["details"] != "" else "Não informado..."
                
                except KeyError:
                    raise
                        
                try:
                    preço_promocional = product["unitPrice"] if product["unitPrice"] != "" else "Não informado..."
                    preço = product["unitOriginalPrice"] if product["unitOriginalPrice"] != "" else "não informado!"

                except Exception:
                    preço = product["unitPrice"] if product["unitPrice"] != "" else "Não informado..."
                    preço_promocional = "Não informado..."

                cardapio.append(f"Descrição: {descrição}\nDetalhes: {detalhes}\nPreço: {preço}\nPreço promocional: {preço_promocional}")
                filter_list.append({ "id": id_product, "descrição": descrição, "detalhes": detalhes, "preço": preço, "preço_promocional": preço_promocional })
        
        if not response.meta['merchants']:
            for menu in filter_list:
                # if "shampoo monange" in str(menu["descrição"]).lower() or "condicionador monange hidrata com poder" in str(menu["descrição"]).lower():

                # if Restaurant.match_products(BASE_PRODUCTS, str(menu["descrição"]).lower()):    
                yield Restaurant({
                    'name': data['name'],
                    'city': data["address"]["city"],
                    'rating': data["userRatingCount"],
                    'price_range': data['priceRange'],
                    'delivery_time': data['deliveryTime'],
                    'category': data['mainCategory']["friendlyName"],
                    'url': f'{BASE_IFOOD_URL}{str(data["address"]["city"]).lower()}-{str(data["address"]["state"]).lower()}/{data["name"].lower()}/{data["id"]}?item={menu["id"]}',
                    'tags': Restaurant.parse_list(data['tags']),
                    'minimumOrderValue': data['minimumOrderValue'],
                    'cnpj': data["documents"]["CNPJ"]["value"],
                    'address': f'{data["address"]["streetName"]}-{data["address"]["streetNumber"]}, {data["address"]["district"]}',
                    'city': data["address"]["city"],
                    'state': data["address"]["state"],
                    'ibge': response.meta['ibge'],
                    'product': f"Descrição: {menu['descrição']}\nDetalhes: {menu['detalhes']}",
                    'promotional_price': menu["preço_promocional"],
                    'original_price': menu["preço"]
                })
                # break
        
        else:
            yield Restaurant({
                'name': item['name'],
                'city': item['slug'].split('/')[0],
                'rating': item['userRating'],
                'price_range': item['priceRange'],
                'delivery_time': item['deliveryTime'],
                'delivery_fee': item['deliveryFee']['value'],
                'distance': item['distance'],
                'category': item['mainCategory']['name'],
                'avatar': Restaurant.parse_avatar(item),
                'url': "{}{}/{}".format(BASE_IFOOD_URL, item['slug'], item['id']),
                'tags': Restaurant.parse_list(item['tags']),
                'paymentCodes': Restaurant.parse_list(item['paymentCodes']),
                'minimumOrderValue': item['minimumOrderValue'],
                'regionGroup': item['contextSetup']['regionGroup'],
                'catalogGroup': item['contextSetup']['catalogGroup'],
                'cnpj': data["documents"]["CNPJ"]["value"],
                'address': f'{data["address"]["streetName"]}-{data["address"]["streetNumber"]}, {data["address"]["district"]}, {data["address"]["city"]}-{data["address"]["state"]}',
                'ibge': response.meta['ibge'],
                "menu": cardapio
            })
