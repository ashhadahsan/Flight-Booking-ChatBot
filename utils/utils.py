import re
import random
import pandas as pd
import spacy
import requests
from io import BytesIO
from word2number import w2n
import uuid
from gtts import gTTS
import base64


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


def get_iata(bearer_token: str, city: str) -> str:

    url = f"http://34.200.242.60/api/search-airport?search={city}"
    payload = {}
    headers = {"Accept": "application/json", "Authorization": f"Bearer {bearer_token}"}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()["data"]
    index = random.randint(0, len(data))
    return data[index]["AirportCode"]


nlp = spacy.load("en_core_web_sm")


def get_city(text: str) -> str:
    doc = nlp(text)
    data = []
    for ent in doc.ents:
        data.append({"label": ent.label_, "value": ent.text})
    print(data)
    df = pd.DataFrame(data=data)
    print(df)

    return df[df["label"] == "GPE"].value.tolist()[0]


def get_date(text: str) -> str:
    doc = nlp(text)
    data = []
    for ent in doc.ents:
        data.append({"label": ent.label_, "value": ent.text})
    df = pd.DataFrame(data=data)
    return df[df["label"] == "DATE"].value.tolist()[0]


def get_number_of_passengers(text: str) -> str:
    doc = nlp(text)
    data = []
    for ent in doc.ents:
        data.append({"label": ent.label_, "value": ent.text})
    df = pd.DataFrame(data=data)
    return w2n.word_to_num(df[df["label"] == "CARDINAL"].value.tolist()[0])


def get_number_of_passengers_more(text: str):
    doc = nlp(text)

    # Origin city name
    origin_city = None
    for token in doc:
        if token.text.lower() == "from":
            origin_city = token.nbor(1).text
            break

    # Departure city name
    destination_city = None
    for token in doc:
        if token.text.lower() == "to":
            destination_city = token.nbor(1).text
            break

    # Date of departure and return date
    departure_date = None
    return_date = None
    for i, token in enumerate(doc):
        if token.text.lower() == "on":
            if departure_date is None:
                departure_date = doc[i + 1].text
            else:
                return_date = doc[i + 1].text
                break

    # Number of kids and adults
    num_kids = None
    num_adults = None
    for i, token in enumerate(doc):
        if token.text.lower() == "kids":
            num_kids = doc[i - 1].text
        elif token.text.lower() == "adult":
            num_adults = doc[i - 1].text
    return w2n.word_to_number(num_adults), w2n.word_to_number(num_kids)


def get_audio(response):

    language = "en-us"

    tts = gTTS(text=response, lang=language, slow=False)
    name = str(uuid.uuid1())

    audio_io = BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)
    audio_response = audio_io.read()
    return base64.b64encode(audio_response).decode("utf-8")
