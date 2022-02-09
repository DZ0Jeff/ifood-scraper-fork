# run the file using scrapy runspider ifood-spider.py -o output.csv
# inspired by https://github.com/nathan-cruz77/ifood/blob/master/ifood_spider.py
import json
import scrapy
import pandas as pd


BASE_IFOOD_URL = 'https://www.ifood.com.br/delivery/'
BASE_AVATAR_URL = 'https://static-images.ifood.com.br/image/upload/f_auto,t_high/logosgde/'
#BASE_URL = 'https://marketplace.ifood.com.br/v1/merchants?latitude=-23.19529&longitude=-45.90321&channel=IFOOD'


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
    ibge = scrapy.Field()
    menu = scrapy.Field()
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


class IfoodSpider(scrapy.Spider):
    name = 'ifood'

    def start_requests(self):
        df = pd.read_csv("data/coordinates_list.csv")

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
                # "CATALOG_ITEM_CAROUSEL",
                # "BIG_BANNER_CAROUSEL",
                # "IMAGE_BANNER",
                # "MERCHANT_LIST_WITH_ITEMS_CAROUSEL",
                # "SMALL_BANNER_CAROUSEL",
                "NEXT_CONTENT",
                # "MERCHANT_CAROUSEL",
                # "MERCHANT_TILE_CAROUSEL",
                # "SIMPLE_MERCHANT_CAROUSEL",
                # "INFO_CARD",
                "MERCHANT_LIST_V2",
                # "ROUND_IMAGE_CAROUSEL",
                # "BANNER_GRID",
                # "MEDIUM_IMAGE_BANNER"
            ],
            "supported-actions":["card-content","catalog-item","last-restaurants","merchant","page","reorder","webmiddleware"]
        }

        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        }
        
        for i in range(len(df)):
            lat = df['latitude'].iloc[i]
            long = df['longitude'].iloc[i]
            ibge = df['codigo_ibge'].iloc[i]
            # country = df['country'].iloc[i]
            
            # if country == "Colombia":
            #     CHANNEL = "COMEYA"

            # elif country == "Mexico":
            #     CHANNEL = ""

            # todo: debugger the v2 api call with post requests (check headers, format and query params)
            merchants = False
            if merchants:
                BASE_URL = f"https://marketplace.ifood.com.br/v1/merchants?latitude={lat}&longitude={long}&channel={CHANNEL}"

                yield scrapy.Request(f'{BASE_URL}&size=0', callback=self.parse_core, meta={"ibge": ibge, "base_url": BASE_URL})
            
            else:
                BASE_URL = f"https://marketplace.ifood.com.br/v2/home?latitude={lat}&longitude=-{long}&channel=IFOOD&alias=MERCADO_FARMACIA"

                yield scrapy.Request(BASE_URL, method="POST", callback=self.parse_page, headers=headers, body=json.dumps(payload), meta={"ibge": ibge, "base_url": BASE_URL, "merchants": merchants})

    def parse_core(self, response):
        data = json.loads(response.text)

        total = data['total']
        pages_count = total // 100

        if total / 100 != total // 100:
            pages_count += 1

        for page in range(pages_count):
            yield scrapy.Request(f'{response.meta["base_url"]}&size={100}&page={page}', callback=self.parse_page, meta={"ibge": response.meta['ibge']})

    def parse_page(self, response):
        # print('page!')
        # problem here!
        data = json.loads(response.text)
        merchants = response.meta["merchants"]

        if merchants:
            for items in data['merchants']:
                yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{items["id"]}/extra', callback=self.parse_details, meta={"ibge": response.meta['ibge'], "item": items})
        
        else:
            for cards in data["sections"][0]["cards"]:
                for contents in cards["data"]["contents"]:
                    # yield contents["id"]
                    yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{contents["id"]}/extra', callback=self.parse_details, meta={"ibge": response.meta['ibge'], "item": contents})


    def parse_details(self, response):
        data = json.loads(response.text)
        item = response.meta['item']
        yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{item["id"]}/menu', 
        callback=self.parse_menu, meta={"ibge": response.meta['ibge'], "item": item, "details": data })
    
    def parse_menu(self, response):
        item = response.meta['item']
        data = response.meta['details']

        cardapio = []
        filter_list = []
        for menus in response.json():
            for product in menus['itens']:
                descrição = product['description']
                try:
                    detalhes = product["details"] if product["details"] != "" else "Não informado..."
                
                except KeyError:
                    detalhes = "Não Existente..."

                preço = product["unitPrice"] if product["unitPrice"] != "" else "Não informado..."

                cardapio.append(f"Descrição: {descrição}\nDetalhes: {detalhes}\n\nPreço: {preço}\n")
                filter_list.append({ "descrição": descrição, "detalhes": detalhes, "preço": preço })
        
        # for menu in filter_list:
        #     if str(menu["descrição"]).lower() in ["monage Shampoo", "condicionador hidrata com poder"]:
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
