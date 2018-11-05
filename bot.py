import nekos
import time
import requests
import json
import os
import gevent
from flask import Flask, request
from flask_sockets import Sockets
from urllib.parse import urljoin

BUTTS_API = 'http://api.obutts.ru/noise/1'
BUTTS_MEDIA_BASE = 'http://media.obutts.ru/'

BOOBS_API = 'http://api.oboobs.ru/noise/1'
BOOBS_MEDIA_BASE = 'http://media.oboobs.ru/'


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
    response = requests.get('http://shibe.online/api/shibes',
                            params={'count': 1,
                                    'urls': 'true',
                                    'httpsUrls': 'true'})
    return response.json()[0]


# get inspirobot image
def getInspiro():
    response = requests.get('http://inspirobot.me/api',
                            params={'generate': 'true'})
    return response.text

# posts random boobies
def getBoobies():
    response = requests.get(BOOBS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BOOBS_MEDIA_BASE, relative_preview_url)
        return (True, absolute_preview_url)
    else:
        return (False, "Boobs are striking :(")

# posts random butts
def getButt():
    response = requests.get(BUTTS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BUTTS_MEDIA_BASE, relative_preview_url)
        return (True, absolute_preview_url)
    else:
        return (False, "Butts are striking :(")


# post help
def postHelpText(chatID):
    text = '''The bot supports the following commands:  \n \n
    - /neko: posts a random neko picture \n
    - /shibe: posts a random shibe picture \n
    - /inspire: posts a random inspirational quote \n
    - /boobies: posts random boobies \n
    - /butt: posts a random butt'''
    sendMessage(chatID, text)


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
    # print(newURL)
    requests.get(newURL, {'chat_id': chatID, 'photo': imageUrl})


def sendMessage(chatID, message):
    newUrl = url + 'sendMessage'
    requests.get(newUrl, {'chat_id': chatID, 'text': message})


# send a lorenz
def sendLorenz(chatID):
    newUrl = url + 'sendPhoto'
    requests.get(newUrl, {'chat_id': chatID,
                          'photo': 'www.hfm-karlsruhe.de/inmm/images/01-InMM/team/Lorenz-rainer-120x120.jpg',
                          'caption': 'Ähm Entschuldigung, was machen sie da?'})


@app.route('/')
def hello():
    return "Hello this is Bot"


@app.route('/'+key, methods=['GET', 'POST'])
def handle():
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data['message']:
            chatID = getChatID(data)
            # sender = getSender(data)
            message = getMessage(data)
            # senderID = getSenderID(data)
            if data['message']['from']['is_bot'] is False:

                if '/neko' in message:
                    sendImage(chatID, getNeko())
                if '/shibe' in message:
                    sendImage(chatID, getShibe())
                if '/inspire' in message:
                    sendImage(chatID, getInspiro())
                if '/help' in message:
                    postHelpText(chatID)
                if '/lorenz' in message:
                    sendLorenz(chatID)
                if '/boobies' in message:
                    success, content = getBoobies()
                    if success:
                        sendImage(chatID, content)
                    else:
                        sendMessage(chatID, content)

                if '/butt' in message:
                    success, content = getButt()
                    if success:
                        sendImage(chatID, content)
                    else:
                        sendMessage(chatID, content)
    return "ok"
