# run the file using scrapy runspider ifood-spider.py -o output.csv
# inspired by https://github.com/nathan-cruz77/ifood/blob/master/ifood_spider.py
import json
import scrapy
import pandas as pd
import re


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
    # distance = scrapy.Field()
    category = scrapy.Field()
    # avatar = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    # paymentCodes = scrapy.Field()
    minimumOrderValue = scrapy.Field()
    regionGroup = scrapy.Field()
    catalogGroup = scrapy.Field()
    cnpj = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    # ibge = scrapy.Field()
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
        filenames = ["data/base input ifood_v2.xlsx", "data/cidades_target.xlsx", "data/coordinates_list.csv", "data/coordinates_list_filtered.csv"]
        
        df = pd.read_excel(filenames[0])
            
        for i in range(len(df)):

            id = df['url'].iloc[i].split('/')[-1]

            yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{id}/extra', callback=self.parse_details, meta={"id": id})    

    def parse_details(self, response):
        data = json.loads(response.text)
        id = response.meta['id']
        
        yield scrapy.Request(f'https://marketplace.ifood.com.br/v1/merchants/{id}/menu', 
        callback=self.parse_menu, meta={"id": id, "details": data })
    
    def parse_menu(self, response):
        data = response.meta['details']

        # cardapio = []
        filter_list = []
        
        for menus in response.json():
            for product in menus['itens']:
                id_product = product['id']
                descri????o = product['description']
                try:
                    detalhes = product["details"] if product["details"] != "" else "N??o informado..."
                
                except KeyError:
                    raise
                        
                try:
                    pre??o_promocional = product["unitPrice"] if product["unitPrice"] != "" else "N??o informado..."
                    pre??o = product["unitOriginalPrice"] if product["unitOriginalPrice"] != "" else "n??o informado!"

                except Exception:
                    pre??o = product["unitPrice"] if product["unitPrice"] != "" else "N??o informado..."
                    pre??o_promocional = "N??o informado..."

                # cardapio.append(f"Descri????o: {descri????o}\nDetalhes: {detalhes}\nPre??o: {pre??o}\nPre??o promocional: {pre??o_promocional}")
                filter_list.append({ "id": id_product, "descri????o": descri????o, "detalhes": detalhes, "pre??o": pre??o, "pre??o_promocional": pre??o_promocional })
        
        
        for menu in filter_list:
            # if "shampoo monange" in str(menu["descri????o"]).lower() or "condicionador monange hidrata com poder" in str(menu["descri????o"]).lower():

            # if Restaurant.match_products(BASE_PRODUCTS, str(menu["descri????o"]).lower()):    
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
                # 'ibge': response.meta['ibge'],
                'product': f"Descri????o: {menu['descri????o']}\nDetalhes: {menu['detalhes']}",
                'promotional_price': menu["pre??o_promocional"],
                'original_price': menu["pre??o"]
            })
            # break