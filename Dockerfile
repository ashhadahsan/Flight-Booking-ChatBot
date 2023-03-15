FROM python:3.9

WORKDIR /app

COPY . /app
RUN apt-get update
RUN apt-get install -y ffpmeg


RUN --mount=type=cache,target=/root/.cache \
    pip3 install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm
EXPOSE 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]