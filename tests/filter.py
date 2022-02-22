import re


BASE_PRODUCTS = [
    "shampoo monange",
    "monange deo aero",
    "monange shampoo" # 325ml,
    "risque regular blister",
    "paixão hidratante regular", # 200ml
    "biocolor mini kit",
    "adidas deo aero", # 150ml
    "monange cpp", # 300ml
    "risque diamond gel regular",
    "paixão-olep regular" # 200ml
    "biocolor homem tonalizante home",
    "bozzano gel pote", #300g
    "monange deo roll", # 60mg
    "monange hidratante", #200m
    "monange condicionador", # 325ml
    "risque regular comercial",
    "condicionador monange hidrata com poder"
]


def match_products(match_array:list, target:str):
    """
    Filter word if matches the content (unorded)

    args:
    match_pattern: the match pattern
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

if match_products(BASE_PRODUCTS, "monange shampoo"):
    print("Matched!")

else:
    print("Not matched")