from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from training import *

# Create a new chatbot


def load_booking_chatbot():
    bot = ChatBot("BookingBot")

    # Create a ChatterBotCorpusTrainer for greetings and goodbyes
    corpus_trainer = ListTrainer(bot)
    corpus_trainer.train(greetings)
    return bot
