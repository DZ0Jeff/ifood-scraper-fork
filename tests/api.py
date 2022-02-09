import requests
import json


def get_store_id():
    response = requests.get("https://marketplace.ifood.com.br/v1/merchants?latitude=-23.19529&longitude=-45.90321&channel=IFOOD")
    content = response.content
    merchants = json.loads(content)['merchants']
    # seleciona o primeiro restaurante da lista e obtém o id dele
    restaurant_id = merchants[0]['id']
    return restaurant_id


def get_details(restaurant_id):
    response = requests.get(f"https://marketplace.ifood.com.br/v1/merchants/{restaurant_id}/extra")
    content = response.content
    restaurant_info = json.loads(content)

    details = dict()

    details['Name'] = restaurant_info["name"]
    details['Descrição'] = restaurant_info["description"]
    details["Endereço"] = f'{restaurant_info["address"]["streetName"]}-{restaurant_info["address"]["streetNumber"]}, {restaurant_info["address"]["district"]}, {restaurant_info["address"]["city"]}-{restaurant_info["address"]["state"]}'
    details["Páis"] = f'{restaurant_info["address"]["country"]}'
    details['Range de preço'] = restaurant_info["priceRange"]
    details["Nota do restaurante"] = restaurant_info["userRatingCount"]
    details["Categoria"] = restaurant_info["mainCategory"]["description"]
    details['CNPJ'] = restaurant_info["documents"]["CNPJ"]["value"]

    [print(f"{index}: {content}") for index, content in details.items()]
    print(json.dumps(restaurant_info, indent=4))


def get_products():
    payload = {
        "supported-actions":[
            "card-content",
            "catalog-item",
            "last-restaurants",
            "merchant",
            "page",
            "reorder",
            "webmiddleware"
        ],
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
        "supported-headers":[],
    }

    headers = {
        # "method": "POST",
        # "path": "/v2/home?latitude=-23.6945238&longitude=-46.5621245&channel=IFOOD&alias=MERCADO_FARMACIA",
        # "scheme": "https",
        # "accept": "application/json, text/plain, */*",
        # "accept-encoding": "gzip, deflate, br",
        # "accept-language": "pt-BR,pt;q=1",
        # 'app_version': "9.66.7",
        # "browser": "Windows",
        # "cache-control": "no-cache, no-store",
        # "content-length": "541",
        # "content-type": "application/json",
        # "origin": "https://www.ifood.com.br",
        # "platform": "Desktop",
        # "referer": "https://www.ifood.com.br/",
        # "sec-fetch-dest": "empty",
        # "sec-fetch-mode": "cors",
        # "sec-fetch-site": "same-site",
        # "sec-gpc": "1",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
        # "x-ifood-device-id": "dc808812-58b2-41e6-8c69-755f1221c35e",
        # "x-ifood-session-id": "9b948a1c-4d55-4788-9cd6-6cc6a034a6ad"
    }

    data = requests.post("https://marketplace.ifood.com.br/v2/home?latitude=-23.6945238&longitude=-46.5621245&channel=IFOOD&alias=MERCADO_FARMACIA", headers=headers, data=payload)
    
    print(data.status_code)
    # print(data.json())

    if data.status_code == 200:
        with open('data.json', 'w') as file:
            json.dump(data.json(), file, indent=4)

def main():
    # restaurant_id = get_store_id()
    # get_details(restaurant_id)
    get_products()


if __name__ == "__main__":
    main()