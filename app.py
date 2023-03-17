from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, Depends, Form
from uuid import UUID, uuid4

import speech_recognition as sr
import io
from fastapi.responses import JSONResponse
from gtts import gTTS
from chatbot import *
from sessions import *
from constants import *
from io import BytesIO
import base64
from aiofiles.os import remove
import random
from training import intents

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


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.post("/create_session/{name}/{location}")
async def create_session(name: str, location: str, response: Response):

    session = uuid4()
    data = SessionData(username=name, current_location=location)

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

# add mp3 file upload here please
@app.post("/api/bookingChat")
async def handle_speech(
    audio: UploadFile = File(...),
    username: str = Form(...),
    current_location: str = Form(...),
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

    city = None
    date = None

    # Get a response from Chatterbot

    response = get_response(bot, text)
    print(response)

    response = response.replace("user", username)

    # language = "en-us"

    # tts = gTTS(text=response, lang=language, slow=False)
    # name = str(uuid.uuid1())

    # audio_io = BytesIO()
    # tts.write_to_fp(audio_io)
    # audio_io.seek(0)
    # audio_response = audio_io.read()

    # # Encode the audio response as base64 for transmission in JSON
    # encoded_audio = base64.b64encode(audio_response).decode("utf-8")
    json_response = {
        "response": response,
        "metadata": {"city": city, "date": date},
        # "audio": encoded_audio,
    }
    # await remove(aud_file)

    # return JSONResponse(content=json_response, media_type="application/json")
