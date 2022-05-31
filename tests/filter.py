import re
import unittest



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



class FilterProducts(unittest.TestCase):
    def setUp(self) -> None:
        self.BASE_PRODUCTS = [
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


    def test_match_products(self):
        self.assertTrue(match_products(self.BASE_PRODUCTS, "monange shampoo"))

    def test_match_products_uppercase(self):
        self.assertTrue(match_products(self.BASE_PRODUCTS, "Monange shampoo"))

    def test_match_products_wrong(self):
        self.assertFalse(match_products(self.BASE_PRODUCTS, "monange shampoo x1"))


if __name__ == "__main__":
    unittest.main()
