import re


class FlightInfoExtractor:
    def __init__(self):
        self.date_regex = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
        self.city_regex = r"\b[A-Z][a-z]+\b"
        self.price_regex = r"\$\d+"

    def extract_flight_info(self, message):
        dates = re.findall(self.date_regex, message)
        origin_city, destination_city = re.findall(self.city_regex, message)[:2]
        price = re.search(self.price_regex, message).group()

        return {
            "dates": dates,
            "origin_city": origin_city,
            "destination_city": destination_city,
            "price": price,
        }


import json
import pandas as pd


def get_iata(city: str) -> str:
    with open("iata.json", "r") as f:
        iata = json.load(f)
    df = pd.DataFrame(iata)
    return df[df["city"] == city.capitalize()]["iata"].values.tolist()[0]
