import nekos
import time
import requests
import json
import os
import gevent
from flask import Flask, request
from flask_sockets import Sockets

# flask app
app = Flask(__name__)
app.debug = 'Debug' in os.environ

# sockets
socket = Sockets(app)


# get api key from file
"""
with open('key', 'r') as f:
    key = f.read()
    """

# get api key from environment variable
key = os.environ['APIKEY']
url = "https://api.telegram.org/bot"+key+"/"
hostname = "hoster"
port = os.environ['PORT']


# get url of a neko img
def getNeko():
    return nekos.img('neko')


# get url for a shibe img
def getShibe():
    response = requests.get('http://shibe.online/api/shibes',  params={'count': 1, 'urls': 'true', 'httpsUrls': 'true'})
    return response.json()[0]


# get inspirobot image
def getInspiro():
    response = requests.get('http://inspirobot.me/api', params={'generate': 'true'})
    return response.text


# post help
def postHelpText(chatID):
    text = "The bot supports the following commands: \n    - /neko: posts a random neko picture \n    - /shibe: posts a random shibe picture \n    - /inspire: posts a random inspirational quote"
    newUrl = url+"sendMessage"
    requests.get(newUrl, {'chat_id':chatID, 'text': text, 'parse_mode':'Markdown'})


def getChatID(data):
    id = data['message']['chat']['id']
    return id


def getMessage(data):
    message = data['message']['text']
    return message


def getSender(data):
    sender = data['message']['from']['first_name']
    return sender


def getSenderID(data):
    senderID = data['message']['from']['id']
    return senderID


# send an image a telegram chat
def sendImage(chatID, imageUrl):
    newURL = url + 'sendPhoto'
    print(newURL)
    requests.get(newURL, {'chat_id': chatID, 'photo': imageUrl})




@app.route('/')
def hello():
    return "Hello this is Bot"


@app.route('/'+key, methods=['GET', 'POST'])
def handle():
    if request.method == 'POST':
        data = request.get_json()
        lastData = request.data
        print(data)
        chatID = getChatID(data)
        sender = getSender(data)
        message = getMessage(data)
        senderID = getSenderID(data)
        if message['message']['from']['is_bot'] == False:

            if '/neko' in message:
                sendImage(chatID, getNeko())
            if '/shibe' in message:
                sendImage(chatID, getShibe())
            if '/inspire' in message:
                sendImage(chatID, getInspiro())
            if '/help' in message:
                postHelpText(chatID)
    else:
        print(data)
    return "ok"
