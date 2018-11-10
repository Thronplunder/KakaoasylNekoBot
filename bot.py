
import datetime
import os
import random

from collections import namedtuple
from urllib.parse import urljoin

import requests
import nekos

from flask import Flask, request

BUTTS_API = 'http://api.obutts.ru/noise/1'
BUTTS_MEDIA_BASE = 'http://media.obutts.ru/'

BOOBS_API = 'http://api.oboobs.ru/noise/1'
BOOBS_MEDIA_BASE = 'http://media.oboobs.ru/'

BOOB_LEFT_SIDES = (
        '{', '(', '[', '\\'
        )

BOOB_RIGHT_SIDES = (
        '}', ')', ']', '/',
        )

BOOB_CRACKS = (
        'y', 'Y', '/\\', 'ㅅ', ')(', '][', '}{', ')(.)(',
        )

BOOB_NIPPLES = (
        'o', '.', 'O', '0', '。', '+', 'p', '-', '*', '•', '^', '°', '○',
        )

MAGIC_8_BALL_ANSWERS = (
        'It is certain.',
        'It is decidedly so.',
        'Without a doubt.',
        'Yes - definitely.',
        'You may rely on it.',
        'As I see it, yes.',
        'Most likely.',
        'Outlook good.',
        'Yes.',
        'Signs point to yes.',
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        'Don\'t count on it.',
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.',
        )

LORENZ_URL = 'www.hfm-karlsruhe.de/inmm/images/01-InMM/team/Lorenz-rainer-120x120.jpg'
LORENZ_MSG = 'Ähm Entschuldigung, was machen sie da?'

WEEKEND_DAYS = (5, 6)


# flask app
APP = Flask(__name__)
APP.debug = 'Debug' in os.environ

# get api key from environment variable
KEY = os.environ['APIKEY']
BASE_URL = 'https://api.telegram.org/bot'+KEY+'/'

COMMANDS = {}

TextMsg = namedtuple('text_msg', ['text'])
PictureMsg = namedtuple('picture_msg', ['url', 'caption'], defaults=('',))

BotCommand = namedtuple('bot_command', ['function', 'helptext'])


def bot_command(command):
    '''
    Decorator for bot commands

    Automatically fills the COMMANDS dict

    param command: name of the command
    '''

    def wrapper(func):
        COMMANDS[command] = BotCommand(func, func.__doc__)
        return func

    return wrapper


def nsfw(text=''):
    '''
    Replaces normal function with a somewhat safe for work ascii boobs.

    param text: text to prepend the ascii boobs with
    '''

    def nsfw_decorator(func):
        def wrapper():
            if not is_nsfw_time():
                return TextMsg(f'{text}\n{gen_ascii_boobs()}')
            return func()

        return wrapper
    return nsfw_decorator


def gen_ascii_boobs():
    '''generate ascii boob'''
    left_side = random.choice(BOOB_LEFT_SIDES)
    right_side = random.choice(BOOB_RIGHT_SIDES)
    crack = random.choice(BOOB_CRACKS)
    nipple = random.choice(BOOB_NIPPLES)
    spacing = ' ' * random.randint(0, 2)
    return left_side + spacing + nipple + spacing + crack + spacing + nipple + spacing + right_side


def is_nsfw_time():
    '''Returns true if outside of normal work ours'''
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    current_date = current_datetime.date()
    return ((current_time.hour > 18 or current_time.hour < 7)
            or current_date.weekday() in WEEKEND_DAYS)


@bot_command('neko')
def get_neko():
    '''post random neko picture'''
    return PictureMsg(nekos.img('neko'))


@bot_command('shibe')
def get_shibe():
    '''post random shibe picture'''
    response = requests.get('http://shibe.online/api/shibes',
                            params={'count': 1,
                                    'urls': 'true',
                                    'httpsUrls': 'true'})
    return PictureMsg(response.json()[0])


@bot_command('inspire')
def get_inspiro():
    '''post a random inspirational quote'''
    response = requests.get('http://inspirobot.me/api',
                            params={'generate': 'true'})
    return PictureMsg(response.text)

@bot_command('boobies')
@nsfw()
def get_boobies():
    '''post random boobies'''
    response = requests.get(BOOBS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BOOBS_MEDIA_BASE, relative_preview_url)
        return PictureMsg(absolute_preview_url)

    return TextMsg('Boobs are striking :(')

@bot_command('butt')
@nsfw('Sorry, no butts at this time of day, but you can have some boobs.')
def get_butt():
    '''post random butts'''
    response = requests.get(BUTTS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BUTTS_MEDIA_BASE, relative_preview_url)
        return PictureMsg(absolute_preview_url)

    return TextMsg('Butts are striking :(')

@bot_command('8ball')
def get_8_ball():
    '''post random magic 8 ball answer'''
    return TextMsg(random.choice(MAGIC_8_BALL_ANSWERS))


@bot_command('lorenz')
def get_lorenz():
    '''post lorenz'''
    return PictureMsg(LORENZ_URL, LORENZ_MSG)


@bot_command('help')
def generate_help():
    '''post help'''
    text = 'The bot supports the following commands:\n\n'
    for command, (_, helptext) in COMMANDS.items():
        text += f'- /{command}: {helptext}\n'

    return TextMsg(text)


def get_chat_id(data):
    '''extracts the chat id from a request'''
    _id = data['message']['chat']['id']
    return _id


def get_message(data):
    '''extracts the text message from a request'''
    message = data['message']['text']
    return message


# send an image a telegram chat
def send_image(chat_id, image_url, caption):
    '''
    Send image to a telegram chat

    param chat_id: target chat
    param image_url: url of the image
    param caption: image caption
    '''

    url = BASE_URL + 'sendPhoto'
    requests.get(url, {
            'chat_id': chat_id,
            'photo': image_url,
            'caption': caption})


def send_message(chat_id, message):
    '''
    Send message to a telegram chat

    param chat_id: target chat
    param message: message to send
    '''
    url = BASE_URL + 'sendMessage'
    requests.get(url, {'chat_id': chat_id, 'text': message})


def command_dispatch(chat_id, msg):
    '''
    Extracts chat commands from messages and dispatches the function call

    param chatID: target chat
    param msg: (command) message from the chat
    '''
    if not msg.startswith('/'):
        return

    # get first word of message
    command = msg.split(' ', 1)[0]
    # remove command prefix
    command = command.strip('/')

    if command not in COMMANDS:
        return

    msg = COMMANDS[command].function()

    if isinstance(msg, PictureMsg):
        send_image(chat_id, msg.url, msg.caption)

    elif isinstance(msg, TextMsg):
        send_message(chat_id, msg.text)

@APP.route('/')
def hello():
    return 'Hello this is Bot'


@APP.route('/'+KEY, methods=['GET', 'POST'])
def handle():
    '''Handles webhook requests from telegram'''
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data['message']:
            chat_id = get_chat_id(data)
            message = get_message(data)
            if data['message']['from']['is_bot'] is False:
                command_dispatch(chat_id, message)
    return 'ok'
