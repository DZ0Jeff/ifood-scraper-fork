# run the file using scrapy runspider ifood-spider.py -o output.csv
# inspired by https://github.com/nathan-cruz77/ifood/blob/master/ifood_spider.py
import json
from urllib.request import Request
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

            BASE_URL = f"https://marketplace.ifood.com.br/v2/merchants?latitude={lat}&longitude={long}&channel={CHANNEL}&alias=MERCADO_FARMACIA"
            # BASE_URL = f"https://marketplace.ifood.com.br/v2/home?latitude=-{lat}&longitude={long}&channel={CHANNEL}&alias=MERCADO_FARMACIA"

            yield scrapy.Request(f'{BASE_URL}&size=0', callback=self.parse_core, meta={"ibge": ibge, "base_url": BASE_URL})

    def parse_core(self, response):
        data = json.loads(response.text)

        total = data['total']
        pages_count = total // 100

        if total / 100 != total // 100:
            pages_count += 1

        for page in range(pages_count):
            yield scrapy.Request(f'{response.meta["base_url"]}&size={100}&page={page}', callback=self.parse_page, meta={"ibge": response.meta['ibge']})

    def parse_page(self, response):
        data = json.loads(response.text)

        for items in data['merchants']:
            yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{items["id"]}/extra', callback=self.parse_details, meta={"ibge": response.meta['ibge'], "item": items})

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
