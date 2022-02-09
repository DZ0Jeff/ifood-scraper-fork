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

    fetch = requests.Session()
    data = fetch.post("https://marketplace.ifood.com.br/v2/home?latitude=-23.7200517&longitude=-46.6224897&channel=IFOOD&alias=MERCADO_FARMACIA", headers=headers, data=json.dumps(payload))
    
    print(data.status_code)
    # print(data.json())

    if data.status_code == 200:
        with open('data.json', 'w') as file:
            json.dump(data.json(), file, indent=4)
    
    data = data.json()
    for cards in data["sections"][0]["cards"]:
            for contents in cards["data"]["contents"]:
               print(contents["id"])

def main():
    # restaurant_id = get_store_id()
    # get_details(restaurant_id)
    get_products()


if __name__ == "__main__":
    main()