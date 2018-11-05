import nekos
import time
import requests
import json
import os
import gevent
import random
import datetime
from flask import Flask, request
from flask_sockets import Sockets
from urllib.parse import urljoin

BUTTS_API = 'http://api.obutts.ru/noise/1'
BUTTS_MEDIA_BASE = 'http://media.obutts.ru/'

BOOBS_API = 'http://api.oboobs.ru/noise/1'
BOOBS_MEDIA_BASE = 'http://media.oboobs.ru/'

BOOB_LEFT_SIDES = (
        "{", "(", "[", "\\"
        )

BOOB_RIGHT_SIDES = (
        "}", ")", "]", "/",
        )

BOOB_CRACKS = (
        "y", "Y", "/\\", "ㅅ", ")(", "][", "}{", ")(.)(",
        )

BOOB_NIPPLES = (
        "o", ".", "O", "0", "。", "+", "p", "-", "*", "•", "^", "°", "○",
        )


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


def gen_ascii_boobs():
    """ generate ascii boob """
    left_side = random.choice(BOOB_LEFT_SIDES)
    right_side = random.choice(BOOB_RIGHT_SIDES)
    crack = random.choice(BOOB_CRACKS)
    nipple = random.choice(BOOB_NIPPLES)
    spacing = " " * random.randint(0, 2)
    return left_side + spacing + nipple + spacing + crack + spacing + nipple + spacing + right_side


def is_nsfw_time():
    current_time = datetime.datetime.now().time()
    return current_time.hour > 18 or current_time.hour < 7


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
    if not is_nsfw_time:
        return (False, gen_ascii_boobs())

    response = requests.get(BOOBS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BOOBS_MEDIA_BASE, relative_preview_url)
        return (True, absolute_preview_url)
    else:
        return (False, "Boobs are striking :(")

# posts random butts
def getButt():
    if not is_nsfw_time:
        return (False,
                f"Sorry not butts at this time of day, but you can have some boobs\n{gen_ascii_boobs()}")

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
