from .training import *

input_size = 129
output_size = 16
hidden_size = 8
# Create a new chatbot
from booking_chatbot.NeuralNet import NeuralNet
import torch
import nltk
import random


from nltk.stem.porter import PorterStemmer

import numpy as np

stemmer = PorterStemmer()


def tokenize(sentence):
    """
    This function takes a sentence as an input,
    and returns a list of its tokens
    """
    return nltk.word_tokenize(sentence)


def bag_of_words(tokenized_sentence, all_words):
    """
    Function to represent a sentence into a vector of float numbers
    input: list of tokens in a sent and a list of all the words in the text
    output: vector equal to the vocab length for each sentence
    """
    tokenized_sentence = [stemmer.stem(w.lower()) for w in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)

    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    return bag


def load_chatbot():
    new_model = torch.jit.load("./chatbot_model/model.pt", map_location="cpu")
    model_dic = new_model.state_dict()
    new_model = NeuralNet(input_size, hidden_size, output_size)
    new_model.load_state_dict(model_dic)
    new_model.eval()
    return new_model


def get_response(new_model, sentence):
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)
    output = new_model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:

                if tag == "greeting":

                    return (random.choice(intent["responses"]), tag)
                elif tag == "goodbye":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "thanks":

                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_dates_leave":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_info_origin":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_info_desination":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_dates_return_yes":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_confirmation":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_number_of_passengers_alone":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_number_of_passengers_more":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "booking_bank_details_yes":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "identification":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "unknown":
                    return (random.choice(intent["responses"]), tag)
                elif tag == "cancellation":
                    return (random.choice(intent["responses"]), tag)
    else:
        return ("I do not understand", None)
