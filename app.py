from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, Depends, Form
from uuid import UUID, uuid4

import speech_recognition as sr
import io
from fastapi.responses import JSONResponse
from gtts import gTTS
from booking_chatbot.chatbot import *
from user_session.sessions import *
from constants import *
import base64
import random
from booking_chatbot.training import intents
from utils.utils import (
    get_city,
    get_iata,
    get_date,
    get_number_of_passengers,
    get_number_of_passengers_more,
    get_audio,
)
from model.models import current_user
from dateparser import parse

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import uuid
from fastapi import FastAPI, File, UploadFile

import logging
import dateparser

import nltk


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    nltk.download("punkt")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.post("/create_session/{name}/{location}")
async def create_session(
    name: str, location: str, bearer_token: str, response: Response
):

    session = uuid4()
    data = SessionData(username=name, current_location=location)
    current_user.username = name
    current_user.origin = get_iata(bearer_token=bearer_token, city=location)
    print(current_user.username, current_user.origin)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name} and {location}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    print(session_data.username)
    print(session_data)
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"


from pydub import AudioSegment
import aiofiles


def get_response_pt(response):
    encoded_audio = get_audio(response)
    json_response = {
        "response": response,
        "metadata": {
            "username": current_user.username,
            "origin": current_user.origin,
            "desrination": current_user.destination,
            "departure_date": current_user.departure_date,
            "return_date": current_user.return_date,
            "num_adults": current_user.num_adults,
            "child_ages": current_user.child_ages,
        },
        "audio": encoded_audio,
    }
    return json_response


# add mp3 file upload here please
@app.post("/api/bookingChat")
async def handle_speech(
    audio: UploadFile = File(...),
    text_input: str = Form(...),
    bearer_token: str = Form(...),
):
    bot = load_chatbot()
    name = str(uuid.uuid1())
    aud_file = f"{name}.wav"
    async with aiofiles.open(audio.filename, "wb") as out_file:
        content = await audio.read()  # async read
        await out_file.write(content)  # async write
    audio_file = AudioSegment.from_file(audio.filename, format="mp3")
    audio_file.export(aud_file, format="wav")

    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy
    with sr.AudioFile(aud_file) as source:
        audio_data = r.record(source)
    text = r.recognize_google(audio_data)

    response, tag = get_response(bot, text_input)
    if tag == "booking_info_origin":

        current_user.origin = await get_iata(
            bearer_token=bearer_token, city=get_city(text_input)
        )
        response_json = get_response_pt(response=response)
        del bot
        return JSONResponse(content=response_json, media_type="application/json")

        # response = "Please make sure to speak your Origin of flight, clearly"
        # response_json = get_response_pt(response=response)
        # del bot
        # return JSONResponse(content=response_json, media_type="application/json")
    elif tag == "greeting":
        response = response.replace("user", current_user.username)
        response_json = get_response_pt(response=response)
        del bot
        return JSONResponse(content=response_json, media_type="application/json")

    elif tag == "booking_info_desination":
        try:
            current_user.destination = get_iata(
                bearer_token=bearer_token, city=get_city(text)
            )
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")
        except:
            response = "Please make sure to speak your destination of flight, clearly"
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")

    elif tag == "booking_dates_leave":
        try:
            current_user.departure_date = parse(get_date(text=text))
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")
        except:
            response = "Please make sure to speak your departure date, clearly"
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")
    elif tag == "booking_dates_return_yes":
        try:
            current_user.return_date = parse(get_date(text=text))
            response = response.replace("origin", current_user.origin)
            response = response.replace("destination", current_user.destination)
            response = response.replace(
                "traveldate", current_user.departure_date.strftime(r"%Y-%M-%d")
            )
            response = response.replace(
                "backdate", current_user.return_date.strftime(r"%Y-%M-%d")
            )
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")

        except:
            response = "Please make sure to speak your departure date, clearly"
            response_json = get_response_pt(response=response)
            del bot
            return JSONResponse(content=response_json, media_type="application/json")
    elif tag == "booking_number_of_passengers_alone":  # get number of passeneger
        current_user.num_adults = get_number_of_passengers(text=text)
        response_json = get_response_pt(response=response)
        del bot
        return JSONResponse(content=response_json, media_type="application/json")
    elif tag == "booking_number_of_passengers_more":

        (
            current_user.num_children,
            current_user.num_adults,
        ) = get_number_of_passengers_more(text)
        response_json = get_response_pt(response=response)
        del bot
        return JSONResponse(content=response_json, media_type="application/json")
    elif tag == "booking_bank_details_yes":
        if "Yes" or "Yeah" in text:
            if current_user.origin is None:
                response = "Please make sure to say your Origin of flight"
                response_json = get_response_pt(response=response)
                del bot
                return JSONResponse(
                    content=response_json, media_type="application/json"
                )
            if current_user.destination is None:
                response = "Please make sure to say your destination of flight"
                response_json = get_response_pt(response=response)
                del bot
                return JSONResponse(
                    content=response_json, media_type="application/json"
                )
            if current_user.departure_date is None:
                response = "Please make sure to say your departure of flight"
                response_json = get_response_pt(response=response)
                del bot
                return JSONResponse(
                    content=response_json, media_type="application/json"
                )
            if current_user.num_children is None:
                response = "Please make sure to speak the number of childrens if any"
                response_json = get_response_pt(response=response)
                del bot
                return JSONResponse(
                    content=response_json, media_type="application/json"
                )
    response_json = get_response_pt(response=response)
    del bot
    return JSONResponse(content=response_json, media_type="application/json")
